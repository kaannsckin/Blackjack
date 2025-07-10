# AI Strategy API Documentation

## Overview

The AI Strategy module provides a comprehensive interface for integrating trained reinforcement learning models with the blackjack engine. It includes robust error handling, validation, and monitoring capabilities.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Classes](#core-classes)
3. [Configuration](#configuration)
4. [Integration Examples](#integration-examples)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

## Quick Start

```python
from utils.ai_play_strategy import create_ai_play_strategy
from gymnasium import spaces

# Create AI strategy
action_space = spaces.Discrete(4)
ai_strategy = create_ai_play_strategy(
    action_space=action_space,
    model_path="runs/phase1/models/best_model.zip",
    use_validation=True
)

# Use in game loop
obs = (15, 7, False, 1.5)  # (player_total, dealer_up, usable_ace, true_count)
action = ai_strategy.act(obs)  # Returns action index (0-3)
```

## Core Classes

### AIPlayStrategy

The main AI strategy class that wraps a trained RL model.

#### Constructor

```python
AIPlayStrategy(
    action_space: spaces.Discrete,
    model_path: str | pathlib.Path | None = None
)
```

**Parameters:**
- `action_space`: Gymnasium discrete action space (typically Discrete(4))
- `model_path`: Path to trained Stable-Baselines3 model (.zip file)

#### Methods

##### `act(obs) -> int`

Get action for given observation.

**Parameters:**
- `obs`: Observation tuple or numpy array `(player_total, dealer_up, usable_ace, true_count)`

**Returns:**
- Action index: 0=stand, 1=hit, 2=double, 3=split

**Example:**
```python
obs = (16, 10, False, -1.5)
action = strategy.act(obs)  # Returns 0, 1, 2, or 3
```

##### `reset() -> None`

Reset strategy state (called before new episode).

##### `get_model_info() -> Dict[str, Any]`

Get information about loaded model.

**Returns:**
```python
{
    "loaded": bool,
    "path": str,
    "validation": Dict,
    "action_space_size": int
}
```

### AIPlayStrategyWithValidation

Enhanced version with action validation and statistics.

#### Additional Methods

##### `get_validation_stats() -> Dict[str, int]`

Get validation statistics.

**Returns:**
```python
{
    "total_actions": int,
    "validated_actions": int,
    "corrected_actions": int
}
```

## Configuration

### YAML Configuration

The AI strategy can be configured using YAML files:

```yaml
ai_strategy:
  model:
    path: "runs/phase1/models/best_model.zip"
    device: "cpu"
    load_on_init: true
  
  validation:
    enabled: true
    strict_mode: false
    log_corrections: true
  
  fallback:
    strategy: "random"  # "random", "basic", "conservative"
    enabled: true
  
  monitoring:
    enabled: true
    log_level: "INFO"
    track_actions: true
    track_validation: true
```

### Configuration Manager

```python
from utils.config_manager import get_config_manager

# Load configuration
config_manager = get_config_manager("config/ai_strategy_config.yaml")

# Get specific configs
ai_config = config_manager.get_ai_strategy_config()
engine_config = config_manager.get_engine_config()
```

## Integration Examples

### Basic Integration

```python
from utils.ai_play_strategy import create_ai_play_strategy
from gymnasium import spaces

class BlackjackEngine:
    def __init__(self, player_config):
        self.action_space = spaces.Discrete(4)
        self.player_strategy = self._create_strategy(player_config)
    
    def _create_strategy(self, config):
        if config["strategy"] == "ai_play":
            return create_ai_play_strategy(
                action_space=self.action_space,
                model_path=config.get("model_path"),
                use_validation=config.get("use_validation", True)
            )
        # ... other strategies
    
    def play_hand(self, player_total, dealer_up, usable_ace=False, true_count=0.0):
        obs = (player_total, dealer_up, usable_ace, true_count)
        action_idx = self.player_strategy.act(obs)
        action_map = {0: "stand", 1: "hit", 2: "double", 3: "split"}
        return action_map[action_idx]
```

### Advanced Integration with Monitoring

```python
from utils.ai_play_strategy import AIPlayStrategyWithValidation
from utils.config_manager import get_config_manager

class MonitoredAIStrategy:
    def __init__(self, config_path=None):
        self.config_manager = get_config_manager(config_path)
        self.ai_config = self.config_manager.get_ai_strategy_config()
        
        # Create strategy with monitoring
        action_space = spaces.Discrete(4)
        self.strategy = AIPlayStrategyWithValidation(
            action_space=action_space,
            model_path=self.ai_config.model.path
        )
    
    def act(self, obs):
        action = self.strategy.act(obs)
        
        # Log action if monitoring enabled
        if self.ai_config.monitoring.enabled:
            logger.info(f"Action taken: {action} for obs: {obs}")
        
        return action
    
    def get_performance_stats(self):
        return {
            "model_info": self.strategy.get_model_info(),
            "validation_stats": self.strategy.get_validation_stats()
        }
```

## Testing

### Unit Tests

```python
import pytest
from utils.ai_play_strategy import AIPlayStrategy

def test_basic_functionality():
    action_space = spaces.Discrete(4)
    strategy = AIPlayStrategy(action_space, model_path=None)
    
    # Test random fallback
    obs = (15, 7, False, 0.0)
    action = strategy.act(obs)
    assert 0 <= action <= 3

def test_observation_normalization():
    action_space = spaces.Discrete(4)
    strategy = AIPlayStrategy(action_space, model_path=None)
    
    # Test tuple observation
    obs_tuple = (15, 7, True, 2)
    action1 = strategy.act(obs_tuple)
    assert isinstance(action1, int)
    
    # Test numpy array observation
    obs_array = np.array([15, 7, True, 2], dtype=np.float32)
    action2 = strategy.act(obs_array)
    assert isinstance(action2, int)
```

### Integration Tests

```python
def test_engine_integration():
    from tests.test_ai_play_integration import test_ai_play_random_fallback
    
    # Test with environment
    test_ai_play_random_fallback(10)
```

## Troubleshooting

### Common Issues

#### 1. Model Loading Errors

**Problem:** Model fails to load
```
❌ Failed to load AI model: [Errno 2] No such file or directory
```

**Solution:**
- Check model file path
- Ensure model file exists and is readable
- Verify model is compatible with Stable-Baselines3

```python
# Check model info
strategy = AIPlayStrategy(action_space, model_path="path/to/model.zip")
info = strategy.get_model_info()
print(f"Model loaded: {info['loaded']}")
print(f"Model path: {info['path']}")
print(f"Validation: {info['validation']}")
```

#### 2. Observation Format Errors

**Problem:** Invalid observation format
```
ValueError: Expected 4-dimensional observation, got 3
```

**Solution:**
- Ensure observation has 4 elements: `(player_total, dealer_up, usable_ace, true_count)`
- Check data types (player_total, dealer_up should be int, usable_ace should be bool, true_count should be float)

#### 3. Action Validation Issues

**Problem:** Invalid actions being generated
```
AssertionError: Geçersiz aksiyon: 5
```

**Solution:**
- Use `AIPlayStrategyWithValidation` for automatic action correction
- Check action space size (should be 4 for blackjack)
- Verify model output is within valid range

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use configuration
config_manager = get_config_manager()
config_manager.update_config({
    "ai_strategy": {
        "monitoring": {"log_level": "DEBUG"}
    }
})
```

### Performance Monitoring

Monitor strategy performance:

```python
strategy = AIPlayStrategyWithValidation(action_space, model_path)

# After some actions
stats = strategy.get_validation_stats()
print(f"Total actions: {stats['total_actions']}")
print(f"Validated actions: {stats['validated_actions']}")
print(f"Corrected actions: {stats['corrected_actions']}")
```

## Best Practices

1. **Always use validation** for production systems
2. **Monitor performance** regularly
3. **Test thoroughly** before deployment
4. **Use configuration files** for easy management
5. **Implement proper logging** for debugging
6. **Handle fallback gracefully** when model is unavailable

## API Reference

### Factory Functions

#### `create_ai_play_strategy(action_space, model_path=None, use_validation=True)`

Create AI strategy instance with optional validation.

**Parameters:**
- `action_space`: Gymnasium discrete action space
- `model_path`: Path to trained model (optional)
- `use_validation`: Whether to use action validation

**Returns:**
- `AIPlayStrategy` or `AIPlayStrategyWithValidation` instance

### Configuration Classes

#### `AIStrategyConfig`
Complete AI strategy configuration with validation.

#### `ConfigManager`
Manages YAML configuration loading and validation.

### Error Classes

#### `ModelLoadError`
Custom exception for model loading errors. 