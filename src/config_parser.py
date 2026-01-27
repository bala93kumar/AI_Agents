"""YAML Configuration Parser"""

import logging
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)


class ConfigParser:
    """Parse and validate YAML configuration files."""
    
    def parse(self, config_path: str) -> Dict[str, Any]:
        """
        Parse a YAML configuration file.
        
        Args:
            config_path: Path to the YAML file
            
        Returns:
            Parsed configuration dictionary
        """
        path = Path(config_path)
        
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        
        if config is None:
            raise ValueError(f"Configuration file is empty: {config_path}")
        
        self._validate_config_structure(config)
        logger.info(f"Successfully parsed configuration from {config_path}")
        
        return config
    
    def _validate_config_structure(self, config: Dict[str, Any]) -> None:
        """
        Validate the basic structure of the configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ValueError: If configuration structure is invalid
        """
        required_keys = ['name', 'rules']
        
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        if not isinstance(config['rules'], list):
            raise ValueError("'rules' must be a list")
        
        logger.debug("Configuration structure validation passed")
