# Data Curation Agent

An intelligent agent that performs data curation based on requirements defined in YAML configuration files.

## Overview

The Data Curation Agent automatically processes and curates datasets according to specifications defined in YAML files. It supports validation, filtering, transformation, and quality assessment of data.

## Project Structure

```
data-curation-agent/
├── src/                          # Source code
│   ├── __init__.py
│   ├── agent.py                 # Main agent class
│   ├── config_parser.py         # YAML configuration parser
│   ├── rules_engine.py          # Rules and curation logic
│   └── validators.py            # Data validation utilities
├── config/                       # Configuration files
│   ├── example_curation.yaml    # Example curation config
│   └── schema.yaml              # YAML schema definition
├── tests/                        # Unit tests
│   ├── __init__.py
│   ├── test_agent.py
│   └── test_rules.py
├── examples/                     # Example usage scripts
│   └── basic_example.py
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Features

- **YAML-based Configuration**: Define curation rules in simple YAML format
- **Flexible Rules Engine**: Support for filtering, validation, and transformation
- **Data Quality Checks**: Validate data against defined schemas
- **Batch Processing**: Process multiple datasets efficiently

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

1. Create a curation configuration file (see `config/example_curation.yaml`)
2. Initialize the agent with your configuration
3. Run the curation process

Example:
```python
from src.agent import DataCurationAgent

agent = DataCurationAgent('config/example_curation.yaml')
result = agent.curate(data)
```

## Configuration

See [config/schema.yaml](config/schema.yaml) for the complete YAML schema.

## License

MIT
