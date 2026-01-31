"""
Complete Setup and Deployment Guide for Databricks AI Agent

This guide walks through the entire process of setting up, testing, and deploying
the AI-powered Databricks job monitoring system.
"""

# ============================================================================
# STEP 1: PREREQUISITES
# ============================================================================

"""
Required accounts and access:
1. Azure subscription with OpenAI service deployed
2. Databricks workspace
3. Email account (Gmail, corporate, or SMTP server)
4. Python 3.8 or higher
"""

# ============================================================================
# STEP 2: INSTALLATION
# ============================================================================

# Clone or navigate to your AI_Agents project
# cd /path/to/AI_Agents

# Install dependencies
# pip install -r requirements.txt

# ============================================================================
# STEP 3: GET CREDENTIALS
# ============================================================================

"""
AZURE OPENAI CREDENTIALS:
1. Go to Azure Portal → Search "OpenAI"
2. Select your OpenAI resource
3. Go to "Keys and Endpoints"
4. Copy Key 1 and Endpoint URL
5. Note the deployment name (e.g., "gpt-4")

Example values:
- AZURE_OPENAI_KEY: 1a2b3c4d5e6f7g8h9i0j...
- AZURE_OPENAI_ENDPOINT: https://my-resource.openai.azure.com/
- Deployment: gpt-4

DATABRICKS CREDENTIALS:
1. Open your Databricks workspace
2. User icon → User Settings
3. Go to "Access Tokens"
4. Generate new token (copy immediately)
5. Get workspace URL from browser: https://abc123.cloud.databricks.com

Example values:
- DATABRICKS_HOST: https://abc123.cloud.databricks.com
- DATABRICKS_TOKEN: dapi1234567890abcdef...

EMAIL/SMTP CREDENTIALS:
For Gmail:
1. Enable 2-factor authentication
2. Generate app-specific password: https://myaccount.google.com/apppasswords
3. Use email@gmail.com and the app-specific password

For corporate email:
1. Get SMTP server from IT department
2. Use your corporate credentials

Example values:
- SMTP_SERVER: smtp.gmail.com
- SENDER_EMAIL: your-email@gmail.com
- SENDER_PASSWORD: xxxx xxxx xxxx xxxx (16-char app password)
"""

# ============================================================================
# STEP 4: CREATE .ENV FILE
# ============================================================================

env_content = """
# Azure OpenAI Configuration
AZURE_OPENAI_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Databricks Configuration  
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-databricks-token-here

# Email Configuration (SMTP)
SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-specific-password

# Optional Configuration
MAX_RETRY_ATTEMPTS=3
RETRY_WITH_PARAMS_ATTEMPTS=2
LOG_LEVEL=INFO
"""

# Save this to .env file in your project root
# $ cat > .env << 'EOF'
# [paste content above]
# EOF

# ============================================================================
# STEP 5: TEST CONFIGURATION
# ============================================================================

def test_configuration():
    """Test that all credentials are properly configured."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("Testing Configuration...")
    print("=" * 60)
    
    # Check Azure OpenAI
    azure_key = os.getenv("AZURE_OPENAI_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    
    if azure_key and azure_endpoint:
        print("✅ Azure OpenAI: Configured")
    else:
        print("❌ Azure OpenAI: Missing credentials")
    
    # Check Databricks
    db_host = os.getenv("DATABRICKS_HOST")
    db_token = os.getenv("DATABRICKS_TOKEN")
    
    if db_host and db_token:
        print("✅ Databricks: Configured")
    else:
        print("❌ Databricks: Missing credentials")
    
    # Check Email
    smtp_server = os.getenv("SMTP_SERVER")
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if smtp_server and sender_email and sender_password:
        print("✅ Email (SMTP): Configured")
    else:
        print("❌ Email (SMTP): Missing credentials")
    
    print("=" * 60)

# Run this: python -c "from setup_guide import test_configuration; test_configuration()"

# ============================================================================
# STEP 6: TEST CONNECTIONS
# ============================================================================

def test_all_connections():
    """Test all service connections."""
    from src.azure_openai_client import AzureOpenAIClient
    from src.databricks_connector import DatabricksConnector
    from src.email_notifier import EmailNotifier
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("\nTesting Service Connections...")
    print("=" * 60)
    
    # Test Azure OpenAI
    try:
        ai_client = AzureOpenAIClient()
        print("✅ Azure OpenAI: Connected")
    except Exception as e:
        print(f"❌ Azure OpenAI: {str(e)}")
    
    # Test Databricks
    try:
        db_connector = DatabricksConnector()
        print("✅ Databricks: Connected")
    except Exception as e:
        print(f"❌ Databricks: {str(e)}")
    
    # Test Email
    try:
        email_notifier = EmailNotifier()
        if email_notifier.test_connection():
            print("✅ Email (SMTP): Connected")
        else:
            print("⚠️  Email: Configuration incomplete")
    except Exception as e:
        print(f"❌ Email: {str(e)}")
    
    print("=" * 60)

# Run this: python -c "from setup_guide import test_all_connections; test_all_connections()"

# ============================================================================
# STEP 7: RUN BASIC MONITORING
# ============================================================================

def run_basic_monitoring():
    """Run a basic monitoring cycle."""
    from src.azure_openai_client import AzureOpenAIClient
    from src.databricks_connector import DatabricksConnector
    from src.databricks_agent import DatabricksAgent
    from src.email_notifier import EmailNotifier
    from src.error_decision_engine import ErrorDecisionEngine
    import os
    from dotenv import load_dotenv
    import logging
    
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    print("\nRunning Basic Monitoring...")
    print("=" * 60)
    
    # Initialize components
    ai_client = AzureOpenAIClient()
    db_connector = DatabricksConnector()
    email_notifier = EmailNotifier()
    decision_engine = ErrorDecisionEngine(ai_client)
    
    # Create agent
    agent = DatabricksAgent(
        azure_openai_client=ai_client,
        databricks_connector=db_connector,
        email_notifier=email_notifier,
        error_decision_engine=decision_engine
    )
    
    # Run monitoring - check last 10 failed jobs
    try:
        summary = agent.monitor_jobs(
            job_ids=None,  # Check all jobs
            escalation_emails=["your-email@example.com"],  # Change this!
            check_failed_only=True
        )
        
        print(f"Failed jobs found: {len(summary['failed_jobs'])}")
        print(f"Retried: {len(summary['actions']['retried'])}")
        print(f"Escalated: {len(summary['actions']['escalated'])}")
        
        return summary
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

# Run this: python -c "from setup_guide import run_basic_monitoring; run_basic_monitoring()"

# ============================================================================
# STEP 8: SCHEDULE IN DATABRICKS
# ============================================================================

"""
Option A: Using Databricks Jobs UI

1. Go to Databricks workspace
2. Click "Workflows" (formerly Jobs)
3. Click "Create Job"
4. Configure:
   - Name: "AI Agent - Job Monitoring"
   - Type: "Notebook"
   - Select notebook: /Repos/.../databricks_agent_runner.py
   - Schedule: Every 30 minutes (or as needed)
   - Cluster: Use existing or create new
5. Click "Create"

Option B: Using Databricks CLI

$ databricks jobs create --json-file job-config.json

Where job-config.json contains:
{
    "name": "AI Agent - Job Monitoring",
    "new_cluster": {
        "spark_version": "12.2.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 1
    },
    "notebook_task": {
        "notebook_path": "/Repos/your-user/AI_Agents/notebooks/databricks_agent_runner"
    },
    "schedule": {
        "quartz_cron_expression": "0 */30 * * * ?",
        "timezone_id": "UTC"
    }
}

Option C: Using Terraform

resource "databricks_job" "ai_agent" {
  name = "AI Agent - Job Monitoring"
  
  notebook_task {
    notebook_path = databricks_notebook.agent.path
  }
  
  schedule {
    quartz_cron_expression = "0 */30 * * * ?"
    timezone_id            = "UTC"
  }
  
  new_cluster {
    spark_version   = "12.2.x-scala2.12"
    node_type_id    = "i3.xlarge"
    num_workers     = 1
    aws_attributes {
      availability        = "SPOT"
      zone_id             = "us-west-2a"
    }
  }
}
"""

# ============================================================================
# STEP 9: PREPARE TRAINING DATA FOR FINE-TUNING
# ============================================================================

def prepare_fine_tuning_data():
    """Prepare training data from decision history."""
    from src.databricks_agent import DatabricksAgent
    from src.azure_openai_client import AzureOpenAIClient
    from src.databricks_connector import DatabricksConnector
    from src.email_notifier import EmailNotifier
    from src.error_decision_engine import ErrorDecisionEngine
    from pathlib import Path
    import json
    
    print("\nPreparing Fine-Tuning Data...")
    print("=" * 60)
    
    # Create data directory
    Path("data").mkdir(exist_ok=True)
    
    # Create sample run history
    sample_history = {
        "run_001": [
            {
                "error": "Connection timeout after 30 seconds",
                "context": {"retry_count": 1, "cluster_size": "small"},
                "decision": "RETRY_WITH_PARAMS",
                "reason": "Increase cluster size to handle workload"
            },
            {
                "error": "OutOfMemoryError in shuffle operation",
                "context": {"retry_count": 0, "executor_memory": "4g"},
                "decision": "RETRY_WITH_PARAMS",
                "reason": "Increase executor memory from 4g to 8g"
            }
        ]
    }
    
    # Save history
    with open("data/run_history.json", "w") as f:
        json.dump(sample_history, f, indent=2)
    
    print("✅ Sample run history created")
    
    # Prepare training data
    ai_client = AzureOpenAIClient()
    db_connector = DatabricksConnector()
    email_notifier = EmailNotifier()
    decision_engine = ErrorDecisionEngine(ai_client)
    
    agent = DatabricksAgent(
        azure_openai_client=ai_client,
        databricks_connector=db_connector,
        email_notifier=email_notifier,
        error_decision_engine=decision_engine
    )
    
    example_count = agent.prepare_training_data(
        run_history_file="data/run_history.json",
        output_file="data/training_data.jsonl"
    )
    
    print(f"✅ Created {example_count} training examples")
    print(f"✅ Training data saved to data/training_data.jsonl")
    print("=" * 60)
    
    return example_count

# Run this: python -c "from setup_guide import prepare_fine_tuning_data; prepare_fine_tuning_data()"

# ============================================================================
# STEP 10: START FINE-TUNING JOB
# ============================================================================

def start_fine_tuning():
    """Start fine-tuning the error handling model."""
    from src.databricks_agent import DatabricksAgent
    from src.azure_openai_client import AzureOpenAIClient
    from src.databricks_connector import DatabricksConnector
    from src.email_notifier import EmailNotifier
    from src.error_decision_engine import ErrorDecisionEngine
    
    print("\nStarting Fine-Tuning Job...")
    print("=" * 60)
    
    ai_client = AzureOpenAIClient()
    db_connector = DatabricksConnector()
    email_notifier = EmailNotifier()
    decision_engine = ErrorDecisionEngine(ai_client)
    
    agent = DatabricksAgent(
        azure_openai_client=ai_client,
        databricks_connector=db_connector,
        email_notifier=email_notifier,
        error_decision_engine=decision_engine
    )
    
    job_id = agent.fine_tune_error_model(
        training_data_path="data/training_data.jsonl",
        model_name="gpt-4",
        suffix="error-handler-v1"
    )
    
    print(f"✅ Fine-tuning job started: {job_id}")
    print("This may take 10-30 minutes to complete")
    print("=" * 60)
    
    return job_id

# Run this: python -c "from setup_guide import start_fine_tuning; start_fine_tuning()"

# ============================================================================
# STEP 11: MONITOR FINE-TUNING STATUS
# ============================================================================

def check_fine_tuning_status(job_id: str):
    """Check status of fine-tuning job."""
    from src.databricks_agent import DatabricksAgent
    from src.azure_openai_client import AzureOpenAIClient
    from src.databricks_connector import DatabricksConnector
    from src.email_notifier import EmailNotifier
    from src.error_decision_engine import ErrorDecisionEngine
    
    print(f"\nChecking Fine-Tuning Status: {job_id}")
    print("=" * 60)
    
    ai_client = AzureOpenAIClient()
    db_connector = DatabricksConnector()
    email_notifier = EmailNotifier()
    decision_engine = ErrorDecisionEngine(ai_client)
    
    agent = DatabricksAgent(
        azure_openai_client=ai_client,
        databricks_connector=db_connector,
        email_notifier=email_notifier,
        error_decision_engine=decision_engine
    )
    
    status = agent.get_fine_tune_status(job_id)
    
    print(f"Job ID: {status['job_id']}")
    print(f"Status: {status['status']}")
    print(f"Model: {status.get('model', 'In progress...')}")
    print(f"Created: {status['created_at']}")
    
    if status.get('error'):
        print(f"Error: {status['error']}")
    
    print("=" * 60)
    
    return status

# Run this: python -c "from setup_guide import check_fine_tuning_status; check_fine_tuning_status('job-id-here')"

# ============================================================================
# QUICK START SUMMARY
# ============================================================================

QUICK_START = """
QUICK START GUIDE
=================

1. Install dependencies:
   pip install -r requirements.txt

2. Create .env file with credentials:
   cp .env.example .env
   # Edit .env with your actual credentials

3. Test configuration:
   python -c "from setup_guide import test_configuration; test_configuration()"

4. Test connections:
   python -c "from setup_guide import test_all_connections; test_all_connections()"

5. Run basic monitoring:
   python -c "from setup_guide import run_basic_monitoring; run_basic_monitoring()"

6. Deploy to Databricks:
   - Upload notebooks/databricks_agent_runner.py to Databricks
   - Create a scheduled job (every 30 minutes recommended)

7. Monitor results:
   - Check Databricks job runs page
   - Check email for escalations
   - Review logs in /tmp/databricks_agent.log

NEXT STEPS
==========

- Review DATABRICKS_AGENT_GUIDE.md for detailed documentation
- Customize config/databricks_agent.yaml for your environment
- Set up fine-tuning with your historical decision data
- Create dashboards to track agent performance

TROUBLESHOOTING
===============

Issue: Azure OpenAI connection fails
Solution: Verify AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT in .env

Issue: Databricks connection fails
Solution: Verify DATABRICKS_HOST and DATABRICKS_TOKEN, check token expiration

Issue: Email not sending
Solution: Use app-specific password for Gmail, test with test_connection()

Issue: Agent not finding failed jobs
Solution: Check job IDs are correct, verify jobs exist in your workspace

SUPPORT
=======

For issues or questions:
1. Check the DATABRICKS_AGENT_GUIDE.md
2. Review example notebooks in examples/
3. Check logs: tail -f /tmp/databricks_agent.log
4. Verify all environment variables are set correctly
"""

if __name__ == "__main__":
    print(QUICK_START)
