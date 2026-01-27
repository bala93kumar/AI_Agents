"""Rules Engine for Data Curation"""

import logging
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class RulesEngine:
    """
    Executes curation rules defined in configuration.
    
    Supports various rule types:
    - filter: Remove rows based on conditions
    - transform: Apply transformations to columns
    - validate: Check data quality
    """
    
    RULE_HANDLERS = {
        'filter': 'apply_filter',
        'transform': 'apply_transform',
        'validate': 'apply_validation',
        'deduplicate': 'apply_deduplication',
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the rules engine.
        
        Args:
            config: Configuration dictionary containing rules
        """
        self.config = config
        self.rules = config.get('rules', [])
    
    def apply_rules(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all configured rules to the dataset.
        
        Args:
            data: Input DataFrame
            
        Returns:
            Processed DataFrame
        """
        result = data.copy()
        
        for rule in self.rules:
            rule_type = rule.get('type')
            
            if rule_type not in self.RULE_HANDLERS:
                logger.warning(f"Unknown rule type: {rule_type}")
                continue
            
            handler_name = self.RULE_HANDLERS[rule_type]
            handler = getattr(self, handler_name)
            result = handler(result, rule)
            logger.info(f"Applied {rule_type} rule: {rule.get('name', 'unnamed')}")
        
        return result
    
    def apply_filter(self, data: pd.DataFrame, rule: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filter rule to remove rows.
        
        Args:
            data: Input DataFrame
            rule: Filter rule configuration
            
        Returns:
            Filtered DataFrame
        """
        condition = rule.get('condition')
        if not condition:
            logger.warning("Filter rule missing condition")
            return data
        
        # Simple implementation - can be extended with more complex conditions
        try:
            mask = eval(f"data.{condition}")
            result = data[mask].reset_index(drop=True)
            logger.debug(f"Filter removed {len(data) - len(result)} rows")
            return result
        except Exception as e:
            logger.error(f"Error applying filter: {e}")
            return data
    
    def apply_transform(self, data: pd.DataFrame, rule: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply transformation rule to columns.
        
        Args:
            data: Input DataFrame
            rule: Transform rule configuration
            
        Returns:
            Transformed DataFrame
        """
        result = data.copy()
        
        transforms = rule.get('transforms', [])
        for transform in transforms:
            column = transform.get('column')
            operation = transform.get('operation')
            
            if column not in result.columns:
                logger.warning(f"Column not found: {column}")
                continue
            
            try:
                if operation == 'lowercase':
                    result[column] = result[column].str.lower()
                elif operation == 'uppercase':
                    result[column] = result[column].str.upper()
                elif operation == 'strip':
                    result[column] = result[column].str.strip()
                else:
                    logger.warning(f"Unknown operation: {operation}")
            except Exception as e:
                logger.error(f"Error applying transform to {column}: {e}")
        
        return result
    
    def apply_validation(self, data: pd.DataFrame, rule: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply validation rule and log results.
        
        Args:
            data: Input DataFrame
            rule: Validation rule configuration
            
        Returns:
            Original DataFrame (validation doesn't modify data)
        """
        checks = rule.get('checks', [])
        
        for check in checks:
            column = check.get('column')
            check_type = check.get('type')
            
            if column not in data.columns:
                logger.warning(f"Column not found for validation: {column}")
                continue
            
            valid_count = data[column].notna().sum()
            logger.info(f"Validation {check_type} on {column}: {valid_count}/{len(data)} valid")
        
        return data
    
    def apply_deduplication(self, data: pd.DataFrame, rule: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply deduplication rule.
        
        Args:
            data: Input DataFrame
            rule: Deduplication rule configuration
            
        Returns:
            Deduplicated DataFrame
        """
        subset = rule.get('subset')
        keep = rule.get('keep', 'first')
        
        if subset and isinstance(subset, list):
            result = data.drop_duplicates(subset=subset, keep=keep)
        else:
            result = data.drop_duplicates(keep=keep)
        
        logger.debug(f"Deduplication removed {len(data) - len(result)} rows")
        return result.reset_index(drop=True)
    
    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run validation checks on the dataset.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            Validation report
        """
        report = {
            'total_records': len(data),
            'columns': list(data.columns),
            'missing_values': data.isnull().sum().to_dict(),
            'dtypes': data.dtypes.astype(str).to_dict(),
        }
        
        return report
