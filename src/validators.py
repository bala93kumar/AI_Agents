"""Data validation utilities"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate data against schemas and constraints."""
    
    @staticmethod
    def validate_required_columns(data: pd.DataFrame, required: List[str]) -> bool:
        """
        Check if all required columns exist.
        
        Args:
            data: DataFrame to validate
            required: List of required column names
            
        Returns:
            True if all required columns exist
        """
        missing = set(required) - set(data.columns)
        if missing:
            logger.error(f"Missing required columns: {missing}")
            return False
        return True
    
    @staticmethod
    def validate_data_types(data: pd.DataFrame, type_map: Dict[str, str]) -> Dict[str, bool]:
        """
        Validate that columns have expected data types.
        
        Args:
            data: DataFrame to validate
            type_map: Dictionary mapping column names to expected types
            
        Returns:
            Dictionary of column validation results
        """
        results = {}
        
        for column, expected_type in type_map.items():
            if column not in data.columns:
                results[column] = False
                continue
            
            actual_type = str(data[column].dtype)
            results[column] = expected_type in actual_type
        
        return results
    
    @staticmethod
    def check_null_values(data: pd.DataFrame, max_null_ratio: float = 0.1) -> Dict[str, float]:
        """
        Check null value ratios in each column.
        
        Args:
            data: DataFrame to check
            max_null_ratio: Maximum allowed ratio of null values (0-1)
            
        Returns:
            Dictionary mapping columns to their null ratios
        """
        ratios = (data.isnull().sum() / len(data)).to_dict()
        
        for column, ratio in ratios.items():
            if ratio > max_null_ratio:
                logger.warning(f"Column {column} has {ratio:.1%} null values")
        
        return ratios
    
    @staticmethod
    def check_duplicates(data: pd.DataFrame, subset: Optional[List[str]] = None) -> int:
        """
        Count duplicate rows.
        
        Args:
            data: DataFrame to check
            subset: Columns to consider for duplicates (None = all columns)
            
        Returns:
            Number of duplicate rows
        """
        if subset:
            duplicates = data.duplicated(subset=subset).sum()
        else:
            duplicates = data.duplicated().sum()
        
        if duplicates > 0:
            logger.warning(f"Found {duplicates} duplicate rows")
        
        return duplicates
