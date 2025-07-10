"""
Configuration Manager for AI Strategy

Handles loading, validation, and management of YAML configuration files.
"""

from __future__ import annotations

import logging
import pathlib
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field, validator


class ModelConfig(BaseModel):
    """Model configuration settings."""
    path: Optional[str] = None
    device: str = "cpu"
    load_on_init: bool = True


class ValidationConfig(BaseModel):
    """Validation configuration settings."""
    enabled: bool = True
    strict_mode: bool = False
    log_corrections: bool = True


class FallbackConfig(BaseModel):
    """Fallback configuration settings."""
    strategy: str = "random"
    enabled: bool = True
    
    @validator('strategy')
    def validate_strategy(cls, v):
        valid_strategies = ["random", "basic", "conservative"]
        if v not in valid_strategies:
            raise ValueError(f"Invalid fallback strategy: {v}. Must be one of {valid_strategies}")
        return v


class MonitoringConfig(BaseModel):
    """Performance monitoring configuration."""
    enabled: bool = True
    log_level: str = "INFO"
    track_actions: bool = True
    track_validation: bool = True
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()


class ObservationConfig(BaseModel):
    """Observation normalization configuration."""
    normalize: bool = True
    player_total_max: float = 21.0
    dealer_up_max: float = 11.0
    true_count_max: float = 10.0


class ActionConfig(BaseModel):
    """Action mapping configuration."""
    actions: Dict[int, str] = Field(default_factory=lambda: {
        0: "stand",
        1: "hit", 
        2: "double",
        3: "split"
    })


class AIStrategyConfig(BaseModel):
    """Complete AI strategy configuration."""
    model: ModelConfig = Field(default_factory=ModelConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    fallback: FallbackConfig = Field(default_factory=FallbackConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    observation: ObservationConfig = Field(default_factory=ObservationConfig)
    actions: ActionConfig = Field(default_factory=ActionConfig)


class EngineConfig(BaseModel):
    """Engine integration configuration."""
    strategy_factory: Dict[str, str] = Field(default_factory=lambda: {
        "default_strategy": "basic",
        "ai_strategy_key": "ai_play"
    })
    performance: Dict[str, float] = Field(default_factory=lambda: {
        "min_agreement_rate": 0.6,
        "min_ev_threshold": -0.1,
        "max_volatility": 0.2
    })


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    console: bool = True


class TestingConfig(BaseModel):
    """Testing configuration."""
    random_seed: int = 42
    num_episodes: int = 1000
    validation_episodes: int = 100
    performance_threshold: float = 0.05


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path or "config/ai_strategy_config.yaml"
        self.config: Dict[str, Any] = {}
        self._load_config()
        self._setup_logging()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        config_file = pathlib.Path(self.config_path)
        
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_file}, using defaults")
            self.config = self._get_default_config()
            return
        
        try:
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_file}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}, using defaults")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "ai_strategy": {
                "model": {"path": None, "device": "cpu", "load_on_init": True},
                "validation": {"enabled": True, "strict_mode": False, "log_corrections": True},
                "fallback": {"strategy": "random", "enabled": True},
                "monitoring": {"enabled": True, "log_level": "INFO", "track_actions": True, "track_validation": True},
                "actions": {0: "stand", 1: "hit", 2: "double", 3: "split"},
                "observation": {"normalize": True, "player_total_max": 21.0, "dealer_up_max": 11.0, "true_count_max": 10.0}
            },
            "engine": {
                "strategy_factory": {"default_strategy": "basic", "ai_strategy_key": "ai_play"},
                "performance": {"min_agreement_rate": 0.6, "min_ev_threshold": -0.1, "max_volatility": 0.2}
            },
            "logging": {"level": "INFO", "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "file": None, "console": True},
            "testing": {"random_seed": 42, "num_episodes": 1000, "validation_episodes": 100, "performance_threshold": 0.05}
        }
    
    def _setup_logging(self) -> None:
        """Setup logging based on configuration."""
        logging_config = self.get_logging_config()
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, logging_config.level),
            format=logging_config.format,
            handlers=[]
        )
        
        # Add console handler if enabled
        if logging_config.console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(logging_config.format))
            logging.getLogger().addHandler(console_handler)
        
        # Add file handler if file path is specified
        if logging_config.file:
            file_path = pathlib.Path(logging_config.file)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(logging.Formatter(logging_config.format))
            logging.getLogger().addHandler(file_handler)
    
    def get_ai_strategy_config(self) -> AIStrategyConfig:
        """Get AI strategy configuration."""
        ai_config = self.config.get("ai_strategy", {})
        return AIStrategyConfig(**ai_config)
    
    def get_engine_config(self) -> EngineConfig:
        """Get engine configuration."""
        engine_config = self.config.get("engine", {})
        return EngineConfig(**engine_config)
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        logging_config = self.config.get("logging", {})
        return LoggingConfig(**logging_config)
    
    def get_testing_config(self) -> TestingConfig:
        """Get testing configuration."""
        testing_config = self.config.get("testing", {})
        return TestingConfig(**testing_config)
    
    def get_config(self) -> Dict[str, Any]:
        """Get raw configuration dictionary."""
        return self.config.copy()
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        self.config.update(updates)
        logger.info("Configuration updated")
    
    def save_config(self, path: Optional[str] = None) -> None:
        """Save current configuration to file."""
        save_path = path or self.config_path
        config_file = pathlib.Path(save_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            logger.info(f"Configuration saved to {config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")


# Global configuration manager instance
config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """Get global configuration manager instance."""
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager(config_path)
    return config_manager


# Configure logging for this module
logger = logging.getLogger(__name__) 