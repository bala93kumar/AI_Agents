"""Basic example of using the Data Curation Agent"""

import logging
import sys
from pathlib import Path

import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import DataCurationAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_data() -> pd.DataFrame:
    """Create sample customer data for demonstration."""
    data = {
        'customer_id': [1, 2, 3, 4, 5, 6, 7, 8],
        'name': ['  John Doe  ', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 
                 'Charlie Davis', 'Eve Wilson', 'Frank Miller', 'Grace Lee'],
        'email': ['john@example.com', 'jane@example.com', None, 'alice@EXAMPLE.COM',
                  'charlie@example.com', 'eve@example.com', 'frank@example.com', 'grace@example.com'],
        'status': ['Active', 'INACTIVE', 'pending', 'active', 'Active', 'inactive', 'INVALID', 'pending'],
        'created_at': pd.date_range('2024-01-01', periods=8),
    }
    
    return pd.DataFrame(data)


def main():
    """Run the basic example."""
    logger.info("Starting Data Curation Agent example")
    
    # Create sample data
    logger.info("Creating sample data...")
    sample_data = create_sample_data()
    logger.info(f"Sample data shape: {sample_data.shape}")
    print("\n--- Original Data ---")
    print(sample_data)
    
    # Initialize agent with configuration
    config_path = Path(__file__).parent.parent / 'config' / 'example_curation.yaml'
    logger.info(f"Loading configuration from {config_path}")
    
    agent = DataCurationAgent(str(config_path))
    
    # Perform curation
    logger.info("Running curation...")
    curated_data = agent.curate(sample_data)
    
    print("\n--- Curated Data ---")
    print(curated_data)
    
    # Validate the curated data
    logger.info("Running validation...")
    validation_report = agent.validate(curated_data)
    
    print("\n--- Validation Report ---")
    for key, value in validation_report.items():
        if not isinstance(value, dict):
            print(f"{key}: {value}")
    
    logger.info("Example completed successfully")


if __name__ == "__main__":
    main()
