"""Example usage of the Databricks AI Agent"""

import os
import sys
from src.config import AgentConfig
from src.agent import DatabricksAIAgent

# Configure environment variables (or use .env file)
os.environ.setdefault("AZURE_OPENAI_API_KEY", "your-azure-openai-api-key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
os.environ.setdefault("AZURE_OPENAI_MODEL", "gpt-4")

os.environ.setdefault("DATABRICKS_WORKSPACE_URL", "https://your-workspace.cloud.databricks.com")
os.environ.setdefault("DATABRICKS_PAT_TOKEN", "your-pat-token")

os.environ.setdefault("EMAIL_ENABLED", "true")
os.environ.setdefault("EMAIL_SENDER", "your-email@gmail.com")
os.environ.setdefault("EMAIL_PASSWORD", "your-app-password")

os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("MAX_RETRIES", "3")


def example_process_failed_job():
    """Example: Process a failed job"""
    print("=" * 60)
    print("Example: Process Failed Job")
    print("=" * 60)
    
    # Load configuration
    config = AgentConfig.from_env()
    
    # Initialize agent
    agent = DatabricksAIAgent(config)
    
    # Process a failed job
    # In real scenario, these values would come from Databricks webhook or monitoring
    result = agent.process_failed_job(
        job_id=123456,
        run_id=789012,
        attempt_number=1
    )
    
    print("\nProcessing Result:")
    print(f"Success: {result.get('success')}")
    print(f"Decision: {result.get('decision', {}).get('action')}")
    print(f"Error: {result.get('error_message', 'None')}")
    
    return result


def example_retry_job():
    """Example: Retry a job with different parameters"""
    print("\n" + "=" * 60)
    print("Example: Retry Job with New Parameters")
    print("=" * 60)
    
    config = AgentConfig.from_env()
    agent = DatabricksAIAgent(config)
    
    # Simulate a second attempt
    result = agent.process_failed_job(
        job_id=123456,
        run_id=789013,
        attempt_number=2,
        previous_error="Out of memory error on first attempt"
    )
    
    print("\nRetry Result:")
    print(f"Action Result: {result.get('action_result')}")
    
    return result


def example_monitor_jobs():
    """Example: Monitor recent jobs"""
    print("\n" + "=" * 60)
    print("Example: Monitor Recent Jobs")
    print("=" * 60)
    
    config = AgentConfig.from_env()
    agent = DatabricksAIAgent(config)
    
    # Monitor jobs
    monitoring_result = agent.monitor_jobs(max_age_hours=24)
    
    print("\nMonitoring Result:")
    print(f"Status: {monitoring_result.get('status')}")
    print(f"Jobs Checked: {monitoring_result.get('jobs_checked')}")
    
    return monitoring_result


if __name__ == "__main__":
    try:
        # Run examples
        example_process_failed_job()
        example_retry_job()
        example_monitor_jobs()
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
