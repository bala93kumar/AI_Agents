"""Tests for the Rules Engine"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rules_engine import RulesEngine


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['alice', 'bob', 'charlie', 'david', 'eve'],
        'email': ['ALICE@TEST.COM', 'BOB@TEST.COM', 'CHARLIE@TEST.COM', 'DAVID@TEST.COM', 'EVE@TEST.COM'],
        'value': [10, 20, 30, 40, 50],
    })


def test_filter_rule(sample_data):
    """Test filter rule execution."""
    config = {
        'name': 'Test',
        'rules': [
            {
                'type': 'filter',
                'condition': 'id > 2'
            }
        ]
    }
    
    engine = RulesEngine(config)
    result = engine.apply_rules(sample_data)
    
    assert len(result) == 3
    assert all(result['id'] > 2)


def test_transform_rule(sample_data):
    """Test transform rule execution."""
    config = {
        'name': 'Test',
        'rules': [
            {
                'type': 'transform',
                'transforms': [
                    {'column': 'email', 'operation': 'lowercase'},
                    {'column': 'name', 'operation': 'uppercase'}
                ]
            }
        ]
    }
    
    engine = RulesEngine(config)
    result = engine.apply_rules(sample_data)
    
    assert all(result['email'].str.islower())
    assert all(result['name'].str.isupper())


def test_deduplication_rule():
    """Test deduplication rule."""
    data = pd.DataFrame({
        'id': [1, 1, 2, 2, 3],
        'name': ['Alice', 'Alice', 'Bob', 'Bob', 'Charlie']
    })
    
    config = {
        'name': 'Test',
        'rules': [
            {
                'type': 'deduplicate',
                'subset': ['id'],
                'keep': 'first'
            }
        ]
    }
    
    engine = RulesEngine(config)
    result = engine.apply_rules(data)
    
    assert len(result) == 3
