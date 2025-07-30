"""
Configuration management module
"""

import os
import yaml
from typing import Any, Dict, Optional
from datetime import datetime

from utils.logger import setup_logger

logger = setup_logger(__name__)


class Config:
    """Configuration manager for the code analysis tool"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config_data = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file and environment variables"""
        try:
            # Load from YAML file
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config_data = yaml.safe_load(f) or {}
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.warning(f"Configuration file {self.config_path} not found, using defaults")
                self.config_data = {}
            
            # Override with environment variables
            self._load_env_overrides()
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self.config_data = {}
    
    def _load_env_overrides(self):
        """Load environment variable overrides"""
        env_mappings = {
            "GITHUB_TOKEN": "github.token",
            "GITHUB_REPOSITORY_OWNER": "github.owner",
            "GITHUB_REPOSITORY_NAME": "github.repo",
            "OPENAI_API_KEY": "ai.openai_api_key",
            "ANTHROPIC_API_KEY": "ai.anthropic_api_key",
            "REPO_PATH": "repository.path",
            "LOAD_TESTING_ENABLED": "load_testing.enabled",
            "LOAD_TESTING_HOST": "load_testing.host"
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self._set_nested_value(config_key, env_value)
    
    def _set_nested_value(self, key_path: str, value: Any):
        """Set nested configuration value"""
        keys = key_path.split('.')
        current = self.config_data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string boolean values
        if isinstance(value, str):
            if value.lower() in ('true', 'yes', '1'):
                value = True
            elif value.lower() in ('false', 'no', '0'):
                value = False
            elif value.isdigit():
                value = int(value)
        
        current[keys[-1]] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by key path"""
        keys = key_path.split('.')
        current = self.config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value"""
        self._set_nested_value(key_path, value)
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
    
    def to_dict(self) -> Dict:
        """Get configuration as dictionary"""
        return self.config_data.copy()