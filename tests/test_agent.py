"""Tests for the Data Curation Agent"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import DataCurationAgent


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'email': ['alice@test.com', 'bob@test.com', None, 'david@test.com', 'eve@test.com'],
        'status': ['active', 'inactive', 'active', 'pending', 'active'],
    })


def test_agent_initialization(tmp_path):
    """Test agent initialization with valid config."""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text("""
name: "Test Config"
version: "1.0.0"
rules:
  - type: filter
    name: "Test filter"
    condition: "id > 0"
""")
    
    agent = DataCurationAgent(str(config_file))
    assert agent.config is not None
    assert agent.config['name'] == "Test Config"


def test_agent_missing_config():
    """Test agent initialization with missing config."""
    with pytest.raises(FileNotFoundError):
        DataCurationAgent("non_existent_config.yaml")


def test_filter_rule(sample_data, tmp_path):
    """Test filter rule application."""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text("""
name: "Filter Test"
version: "1.0.0"
rules:
  - type: filter
    name: "Keep IDs > 2"
    condition: "id > 2"
""")
    
    agent = DataCurationAgent(str(config_file))
    result = agent.curate(sample_data)
    
    assert len(result) == 3
    assert all(result['id'] > 2)


def test_validation(sample_data, tmp_path):
    """Test validation report generation."""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text("""
name: "Validation Test"
version: "1.0.0"
rules:
  - type: validate
    name: "Check not null"
    checks:
      - column: "email"
        type: "not_null"
""")
    
    agent = DataCurationAgent(str(config_file))
    report = agent.validate(sample_data)
    
    assert 'total_records' in report
    assert report['total_records'] == 5
