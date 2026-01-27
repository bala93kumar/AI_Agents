"""Main Data Curation Agent"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from .config_parser import ConfigParser
from .rules_engine import RulesEngine

logger = logging.getLogger(__name__)


class DataCurationAgent:
    """
    Main agent class for data curation operations.
    
    Reads curation requirements from YAML files and applies them to datasets.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the Data Curation Agent.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config_parser = ConfigParser()
        self.rules_engine = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load and parse the YAML configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        self.config = self.config_parser.parse(str(self.config_path))
        self.rules_engine = RulesEngine(self.config)
        logger.info(f"Configuration loaded from {self.config_path}")
    
    def curate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply curation rules to the dataset.
        
        Args:
            data: Input DataFrame to curate
            
        Returns:
            Curated DataFrame
        """
        if self.rules_engine is None:
            raise RuntimeError("Rules engine not initialized")
        
        logger.info(f"Starting curation of {len(data)} records")
        
        # Apply all rules in sequence
        curated_data = data.copy()
        curated_data = self.rules_engine.apply_rules(curated_data)
        
        logger.info(f"Curation complete. Result: {len(curated_data)} records")
        return curated_data
    
    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate dataset against curation schema.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            Validation report dictionary
        """
        return self.rules_engine.validate(data)
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        return self.config
