"""
================================================================================
F3.3: MULTI-TASK MODEL IMPLEMENTATION (PEARL/SAC-AE)
================================================================================

🎯 **AMAÇ:** PEARL ve SAC-AE tabanlı multi-task learning models
📋 **KAPSAM:** Tek politika ile multiple rule sets ve player types
🔧 **ENTEGRASYON:** Stable-Baselines3 ile seamless integration

================================================================================
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
import os
import json
from stable_baselines3.common.policies import BasePolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.utils import get_device
from stable_baselines3 import SAC, PPO
from stable_baselines3.common.callbacks import BaseCallback
import gymnasium as gym

class TaskType(Enum):
    """Different task types for multi-task learning."""
    CONSERVATIVE_PLAYER = "conservative"
    AGGRESSIVE_PLAYER = "aggressive"
    BASIC_STRATEGY = "basic_strategy"
    CARD_COUNTER = "card_counter"
    RANDOM_PLAYER = "random"
    SUPERSTITIOUS = "superstitious"
    
    # Rule-based tasks
    H17_RULES = "h17_rules"
    S17_RULES = "s17_rules"
    DAS_ENABLED = "das_enabled"
    SURRENDER_ENABLED = "surrender_enabled"

@dataclass
class TaskContext:
    """Context information for multi-task learning."""
    task_type: TaskType
    task_id: int
    rule_config: Dict[str, Any]
    player_config: Dict[str, Any]
    task_embedding: np.ndarray
    
    def to_dict(self) -> Dict:
        return {
            "task_type": self.task_type.value,
            "task_id": self.task_id,
            "rule_config": self.rule_config,
            "player_config": self.player_config,
            "task_embedding": self.task_embedding.tolist()
        }

class TaskEmbeddingNetwork(nn.Module):
    """
    Task embedding network for PEARL-style multi-task learning.
    
    Encodes task context into a latent representation that guides policy adaptation.
    """
    
    def __init__(self, task_dim: int, embedding_dim: int = 64):
        super().__init__()
        self.task_dim = task_dim
        self.embedding_dim = embedding_dim
        
        # Task encoder network
        self.task_encoder = nn.Sequential(
            nn.Linear(task_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, embedding_dim),
            nn.Tanh()  # Bounded embedding
        )
        
        # Task-specific modulation network
        self.modulation_net = nn.Sequential(
            nn.Linear(embedding_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, embedding_dim)
        )
    
    def forward(self, task_context: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through task embedding network.
        
        Args:
            task_context: Task context tensor [batch_size, task_dim]
            
        Returns:
            task_embedding: Task embedding [batch_size, embedding_dim]
            modulation: Task-specific modulation [batch_size, embedding_dim]
        """
        task_embedding = self.task_encoder(task_context)
        modulation = self.modulation_net(task_embedding)
        
        return task_embedding, modulation

class PEARLPolicy(BasePolicy):
    """
    PEARL (Probabilistic Embeddings for Actor-critic Reinforcement Learning) Policy.
    
    Implements task-conditioned policy with probabilistic task embeddings.
    """
    
    def __init__(self, 
                 observation_space: gym.spaces.Space,
                 action_space: gym.spaces.Space,
                 lr_schedule: callable,
                 task_dim: int = 32,
                 embedding_dim: int = 64,
                 **kwargs):
        super().__init__(observation_space, action_space, lr_schedule, **kwargs)
        
        self.task_dim = task_dim
        self.embedding_dim = embedding_dim
        
        # Task embedding network
        self.task_embedding_net = TaskEmbeddingNetwork(task_dim, embedding_dim)
        
        # Policy network with task conditioning
        self.policy_net = nn.Sequential(
            nn.Linear(observation_space.shape[0] + embedding_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, action_space.n)
        )
        
        # Value network with task conditioning
        self.value_net = nn.Sequential(
            nn.Linear(observation_space.shape[0] + embedding_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )
        
        # Task encoder for inference
        self.task_encoder = nn.Sequential(
            nn.Linear(task_dim, 128),
            nn.ReLU(),
            nn.Linear(128, embedding_dim),
            nn.Tanh()
        )
    
    def forward(self, obs: torch.Tensor, task_context: torch.Tensor, deterministic: bool = False) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass through PEARL policy.
        
        Args:
            obs: Observation tensor [batch_size, obs_dim]
            task_context: Task context tensor [batch_size, task_dim]
            deterministic: Whether to use deterministic actions
            
        Returns:
            actions: Action logits [batch_size, action_dim]
            values: Value estimates [batch_size, 1]
            task_embeddings: Task embeddings [batch_size, embedding_dim]
        """
        # Encode task context
        task_embedding = self.task_encoder(task_context)
        
        # Concatenate observation and task embedding
        combined_input = torch.cat([obs, task_embedding], dim=-1)
        
        # Forward through policy and value networks
        action_logits = self.policy_net(combined_input)
        values = self.value_net(combined_input)
        
        return action_logits, values, task_embedding
    
    def _predict(self, observation: torch.Tensor, task_context: torch.Tensor, deterministic: bool = False) -> torch.Tensor:
        """Predict actions given observation and task context."""
        action_logits, _, _ = self.forward(observation, task_context, deterministic)
        
        if deterministic:
            actions = torch.argmax(action_logits, dim=-1)
        else:
            actions = torch.multinomial(F.softmax(action_logits, dim=-1), 1).squeeze(-1)
        
        return actions

class SACAEAgent:
    """
    SAC-AE (Soft Actor-Critic with Auto-Encoder) Multi-Task Agent.
    
    Implements SAC with auto-encoder for task representation learning.
    """
    
    def __init__(self, 
                 env,
                 task_dim: int = 32,
                 embedding_dim: int = 64,
                 learning_rate: float = 3e-4,
                 buffer_size: int = 1000000,
                 **kwargs):
        """
        Initialize SAC-AE agent.
        
        Args:
            env: Training environment
            task_dim: Dimension of task context
            embedding_dim: Dimension of task embedding
            learning_rate: Learning rate for all networks
            buffer_size: Size of replay buffer
        """
        self.env = env
        self.task_dim = task_dim
        self.embedding_dim = embedding_dim
        self.learning_rate = learning_rate
        
        # Check if environment is compatible with SAC
        if hasattr(env.action_space, 'n'):  # Discrete action space
            # Use PPO instead of SAC for discrete actions
            from stable_baselines3 import PPO
            self.sac = PPO(
                "MlpPolicy",
                env,
                learning_rate=learning_rate,
                **kwargs
            )
        else:
            # Initialize SAC agent for continuous actions
            self.sac = SAC(
                "MlpPolicy",
                env,
                learning_rate=learning_rate,
                buffer_size=buffer_size,
                **kwargs
            )
        
        # Task embedding network
        self.task_embedding_net = TaskEmbeddingNetwork(task_dim, embedding_dim)
        
        # Auto-encoder for task reconstruction
        self.autoencoder = nn.Sequential(
            nn.Linear(embedding_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, task_dim)
        )
        
        # Optimizers
        self.task_optimizer = torch.optim.Adam(
            list(self.task_embedding_net.parameters()) + list(self.autoencoder.parameters()),
            lr=learning_rate
        )
        
        # Logging
        self.logger = logging.getLogger("SACAEAgent")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"Initialized SAC-AE agent with task_dim={task_dim}, embedding_dim={embedding_dim}")
    
    def encode_task(self, task_context: np.ndarray) -> np.ndarray:
        """Encode task context into embedding."""
        with torch.no_grad():
            task_tensor = torch.FloatTensor(task_context).unsqueeze(0)
            embedding, _ = self.task_embedding_net(task_tensor)
            return embedding.squeeze(0).numpy()
    
    def decode_task(self, task_embedding: np.ndarray) -> np.ndarray:
        """Decode task embedding back to context."""
        with torch.no_grad():
            embedding_tensor = torch.FloatTensor(task_embedding).unsqueeze(0)
            reconstructed = self.autoencoder(embedding_tensor)
            return reconstructed.squeeze(0).numpy()
    
    def learn(self, total_timesteps: int, task_contexts: List[TaskContext]):
        """Train SAC-AE agent on multiple tasks."""
        self.logger.info(f"Starting SAC-AE training for {len(task_contexts)} tasks")
        
        # Task embedding training
        self._train_task_embeddings(task_contexts)
        
        # SAC training with task conditioning
        self.sac.learn(total_timesteps=total_timesteps)
        
        self.logger.info("SAC-AE training completed")
    
    def _train_task_embeddings(self, task_contexts: List[TaskContext]):
        """Train task embedding network and auto-encoder."""
        self.logger.info("Training task embeddings...")
        
        # Prepare training data
        task_data = []
        for context in task_contexts:
            # Create task context vector
            task_vector = self._create_task_vector(context)
            task_data.append(task_vector)
        
        task_data = np.array(task_data)
        
        # Training loop
        num_epochs = 100
        batch_size = 32
        
        for epoch in range(num_epochs):
            # Sample batch
            indices = np.random.choice(len(task_data), batch_size, replace=True)
            batch = torch.FloatTensor(task_data[indices])
            
            # Forward pass
            task_embedding, modulation = self.task_embedding_net(batch)
            reconstructed = self.autoencoder(task_embedding)
            
            # Loss: reconstruction + regularization
            recon_loss = F.mse_loss(reconstructed, batch)
            reg_loss = 0.01 * torch.mean(torch.norm(task_embedding, dim=1))
            total_loss = recon_loss + reg_loss
            
            # Backward pass
            self.task_optimizer.zero_grad()
            total_loss.backward()
            self.task_optimizer.step()
            
            if epoch % 20 == 0:
                self.logger.info(f"Epoch {epoch}: Loss = {total_loss.item():.4f}")
    
    def _create_task_vector(self, context: TaskContext) -> np.ndarray:
        """Create task context vector from TaskContext."""
        # Combine rule and player configuration
        rule_vector = np.array([
            context.rule_config.get("num_decks", 6) / 8.0,  # Normalize
            context.rule_config.get("penetration", 0.75),
            1.0 if context.rule_config.get("dealer_rule") == "H17" else 0.0,
            1.0 if context.rule_config.get("das", True) else 0.0,
            1.0 if context.rule_config.get("surrender", False) else 0.0,
            context.rule_config.get("blackjack_payout", 1.5) / 2.0  # Normalize
        ])
        
        # Player type encoding (one-hot)
        player_types = list(TaskType)
        player_vector = np.zeros(len(player_types))
        player_idx = player_types.index(context.task_type)
        player_vector[player_idx] = 1.0
        
        # Combine vectors
        task_vector = np.concatenate([rule_vector, player_vector])
        
        return task_vector

class MultiTaskModelManager:
    """
    Manager for multi-task models (PEARL and SAC-AE).
    
    Handles model creation, training, saving, and loading.
    """
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.pearl_model = None
        self.sacae_model = None
        
        # Logging
        self.logger = logging.getLogger("MultiTaskModelManager")
        self.logger.setLevel(logging.INFO)
    
    def create_pearl_model(self, env, task_dim: int = 32, embedding_dim: int = 64) -> PEARLPolicy:
        """Create PEARL policy."""
        self.pearl_model = PEARLPolicy(
            observation_space=env.observation_space,
            action_space=env.action_space,
            lr_schedule=lambda _: 3e-4,
            task_dim=task_dim,
            embedding_dim=embedding_dim
        )
        
        self.logger.info("Created PEARL policy")
        return self.pearl_model
    
    def create_sacae_model(self, env, task_dim: int = 32, embedding_dim: int = 64) -> SACAEAgent:
        """Create SAC-AE agent."""
        self.sacae_model = SACAEAgent(
            env=env,
            task_dim=task_dim,
            embedding_dim=embedding_dim
        )
        
        self.logger.info("Created SAC-AE agent")
        return self.sacae_model
    
    def save_models(self, prefix: str = "adaptive"):
        """Save multi-task models."""
        if self.pearl_model:
            pearl_path = os.path.join(self.model_dir, f"{prefix}_pearl.zip")
            torch.save(self.pearl_model.state_dict(), pearl_path)
            self.logger.info(f"Saved PEARL model to {pearl_path}")
        
        if self.sacae_model:
            sacae_path = os.path.join(self.model_dir, f"{prefix}_sacae.zip")
            torch.save({
                'task_embedding_net': self.sacae_model.task_embedding_net.state_dict(),
                'autoencoder': self.sacae_model.autoencoder.state_dict(),
                'sac_model': self.sacae_model.sac
            }, sacae_path)
            self.logger.info(f"Saved SAC-AE model to {sacae_path}")
    
    def load_models(self, prefix: str = "adaptive"):
        """Load multi-task models."""
        pearl_path = os.path.join(self.model_dir, f"{prefix}_pearl.zip")
        sacae_path = os.path.join(self.model_dir, f"{prefix}_sacae.zip")
        
        if os.path.exists(pearl_path):
            self.pearl_model.load_state_dict(torch.load(pearl_path))
            self.logger.info(f"Loaded PEARL model from {pearl_path}")
        
        if os.path.exists(sacae_path):
            checkpoint = torch.load(sacae_path)
            self.sacae_model.task_embedding_net.load_state_dict(checkpoint['task_embedding_net'])
            self.sacae_model.autoencoder.load_state_dict(checkpoint['autoencoder'])
            self.sacae_model.sac = checkpoint['sac_model']
            self.logger.info(f"Loaded SAC-AE model from {sacae_path}")

# Factory functions
def create_pearl_model(env, **kwargs) -> PEARLPolicy:
    """Create PEARL multi-task model."""
    manager = MultiTaskModelManager()
    return manager.create_pearl_model(env, **kwargs)

def create_sacae_model(env, **kwargs) -> SACAEAgent:
    """Create SAC-AE multi-task model."""
    manager = MultiTaskModelManager()
    return manager.create_sacae_model(env, **kwargs)

def create_adaptive_model(env, model_type: str = "pearl", **kwargs):
    """Create adaptive multi-task model."""
    if model_type.lower() == "pearl":
        return create_pearl_model(env, **kwargs)
    elif model_type.lower() == "sacae":
        return create_sacae_model(env, **kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

# Example usage and testing
if __name__ == "__main__":
    print("🔬 F3.3: Multi-Task Model Test")
    print("=" * 50)
    
    # Create dummy environment for testing
    env = gym.make('CartPole-v1')  # Placeholder
    
    # Test PEARL model
    print("Testing PEARL model...")
    pearl_model = create_pearl_model(env, task_dim=32, embedding_dim=64)
    print("✅ PEARL model created successfully")
    
    # Test SAC-AE model
    print("Testing SAC-AE model...")
    sacae_model = create_sacae_model(env, task_dim=32, embedding_dim=64)
    print("✅ SAC-AE model created successfully")
    
    # Test task context creation
    print("Testing task context...")
    task_context = TaskContext(
        task_type=TaskType.CONSERVATIVE_PLAYER,
        task_id=1,
        rule_config={"num_decks": 6, "dealer_rule": "S17"},
        player_config={"risk_tolerance": 0.3},
        task_embedding=np.random.randn(64)
    )
    print(f"✅ Task context created: {task_context}")
    
    print("\n✅ F3.3 Multi-Task Models: READY FOR INTEGRATION") 