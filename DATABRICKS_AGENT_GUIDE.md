# Databricks AI Agent with Azure OpenAI

## Overview

This solution provides an intelligent AI agent for monitoring Databricks jobs, analyzing failures with Azure OpenAI, and making automated decisions on retry, parameter adjustment, or escalation.

## Architecture

```
┌─────────────────────┐
│  Databricks Jobs    │
│  (Failed Runs)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│        DatabricksConnector                      │
│  - Get failed jobs                              │
│  - Get run details & errors                     │
│  - Retry with new parameters                    │
└──────────┬──────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│    ErrorDecisionEngine                          │
│  - Send error to Azure OpenAI for analysis      │
│  - Track retry attempts                         │
│  - Make decision: RETRY / RETRY_WITH_PARAMS /   │
│    ESCALATE_EMAIL / SKIP                        │
└──────────┬──────────────────────────────────────┘
           │
     ┌─────┴─────────────────────┬─────────────┐
     ▼                           ▼             ▼
┌─────────────┐        ┌──────────────────┐  ┌──────────────┐
│ DatabricksConn  │        │  EmailNotifier   │  │ AzureOpenAI  │
│ - Retry      │        │  - Send emails   │  │ - Fine-tune  │
└─────────────┘        └──────────────────┘  └──────────────┘
```

## Key Components

### 1. AzureOpenAIClient (`azure_openai_client.py`)
- Connects to Azure OpenAI API
- Analyzes job errors with AI
- Supports model fine-tuning

### 2. DatabricksConnector (`databricks_connector.py`)
- Manages Databricks workspace connections
- Retrieves failed jobs and run details
- Executes retries with optional parameter changes

### 3. ErrorDecisionEngine (`error_decision_engine.py`)
- Uses AI to analyze errors
- Tracks retry attempts and limits
- Makes intelligent decisions

### 4. EmailNotifier (`email_notifier.py`)
- Sends escalation emails
- Provides failure summaries
- Supports SMTP-based delivery

### 5. DatabricksAgent (`databricks_agent.py`)
- Orchestrates all components
- Monitors jobs continuously
- Supports model fine-tuning

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Update `requirements.txt` with:

```
azure-identity>=1.15.0
azure-ai-openai>=1.3.0
databricks-sdk>=0.3.0
openai>=1.3.0
pyyaml>=6.0
python-dotenv>=0.19.0
pytest>=7.0.0
```

### 2. Configure Environment Variables

Create a `.env` file:

```
# Azure OpenAI
AZURE_OPENAI_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4  # or your deployment name

# Databricks
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-databricks-token

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com  # or your SMTP server
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password  # Use app-specific password for Gmail

# Optional
MAX_RETRY_ATTEMPTS=3
RETRY_WITH_PARAMS_ATTEMPTS=2
```

### 3. Get Credentials

**Azure OpenAI:**
1. Create resource in Azure Portal
2. Get API key and endpoint from "Keys and Endpoint"
3. Create deployment (e.g., "gpt-4")

**Databricks:**
1. Generate PAT in Databricks workspace
2. Profile → User Settings → Access Tokens

**SMTP/Email:**
- Gmail: Use app-specific password
- Corporate: Get SMTP credentials from IT

## Usage Examples

### Basic Job Monitoring

```python
from src.azure_openai_client import AzureOpenAIClient
from src.databricks_connector import DatabricksConnector
from src.databricks_agent import DatabricksAgent
from src.email_notifier import EmailNotifier
from src.error_decision_engine import ErrorDecisionEngine

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

# Monitor jobs
summary = agent.monitor_jobs(
    job_ids=[123, 456],
    escalation_emails=["team@example.com"]
)
```

### Error Analysis Example

```python
# Analyze specific error
error_message = "OutOfMemoryError: Java heap space"
job_context = {
    "job_id": 123,
    "run_id": 456,
    "cluster_size": "small",
    "data_size_gb": 500
}

decision = decision_engine.analyze_and_decide(
    error_message=error_message,
    job_context=job_context
)

print(f"Decision: {decision['decision']}")
print(f"Reason: {decision['reason']}")
if decision.get('suggested_params'):
    print(f"Suggested params: {decision['suggested_params']}")
```

## Decision Logic

The agent makes decisions based on:

1. **Error Analysis**: AI analyzes error messages and patterns
2. **Retry History**: Tracks previous attempts to avoid infinite loops
3. **Limits**: Respects max retry attempts before escalation
4. **Context**: Considers job parameters and cluster configuration

### Decision Types

| Decision | Action | When Used |
|----------|--------|-----------|
| `RETRY` | Retry with same parameters | Transient failures (timeouts, network) |
| `RETRY_WITH_PARAMS` | Retry with modified parameters | Resource issues (memory, CPU) |
| `ESCALATE_EMAIL` | Send email to team | Persistent failures, infrastructure issues |
| `SKIP` | Skip job | Handled elsewhere or no action needed |

## Fine-Tuning the Model

### Prepare Training Data

```python
# Create JSONL training file from historical decisions
agent.prepare_training_data(
    run_history_file="data/run_history.json",
    output_file="data/training_data.jsonl"
)
```

Training data format (JSONL):
```json
{"messages": [
    {"role": "system", "content": "You are an error analysis AI..."},
    {"role": "user", "content": "Error: OutOfMemory..."},
    {"role": "assistant", "content": "{\"decision\": \"RETRY_WITH_PARAMS\", \"reason\": \"...\" }"}
]}
```

### Start Fine-Tuning Job

```python
job_id = agent.fine_tune_error_model(
    training_data_path="data/training_data.jsonl",
    model_name="gpt-4",
    suffix="error-handler-v1"
)

# Check status
status = agent.get_fine_tune_status(job_id)
print(status)
```

## Deployment in Databricks

### Option 1: Databricks Jobs

Create a Databricks job that runs the agent periodically:

```python
# job_runner.py - Run in Databricks
from src.databricks_agent import DatabricksAgent
from src.azure_openai_client import AzureOpenAIClient
from src.databricks_connector import DatabricksConnector
from src.email_notifier import EmailNotifier
from src.error_decision_engine import ErrorDecisionEngine

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

# Run monitoring
summary = agent.monitor_jobs(
    escalation_emails=["data-team@company.com"]
)
```

### Option 2: Databricks Workflows

Set up scheduled workflow to check jobs every 30 minutes.

### Option 3: External Scheduler

Run as Docker container with cron or similar scheduling.

## Monitoring and Logging

View logs in Databricks:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Or use Delta tables to track decisions:

```python
# Log decisions to Delta table
summary_df = spark.createDataFrame([summary['actions']['escalated']])
summary_df.write.mode("append").option("mergeSchema", "true").save("/delta/agent_decisions")
```

## Best Practices

1. **Test Email Configuration**: Use `email_notifier.test_connection()` before deployment
2. **Monitor Fine-Tuning**: Check job status regularly
3. **Adjust Retry Limits**: Based on your job patterns
4. **Keep History**: Store decisions for fine-tuning future models
5. **Alert on Escalations**: Set up notifications when emails are sent
6. **Regular Reviews**: Analyze decision effectiveness monthly

## Troubleshooting

### Azure OpenAI Errors
- Check API key and endpoint
- Verify deployment name matches
- Ensure quota not exceeded

### Databricks Connection Issues
- Validate workspace URL and token
- Check network/firewall settings
- Verify token hasn't expired

### Email Not Sending
- Test SMTP configuration
- For Gmail, use app-specific password
- Check spam folder for test emails

## Performance Considerations

- Batch job monitoring to reduce API calls
- Cache run history to speed up analysis
- Consider rate limiting for Azure OpenAI
- Monitor Databricks API quotas

## Security Notes

- Never commit credentials to version control
- Use environment variables or secrets management
- Rotate tokens regularly
- Audit email escalations

## Future Enhancements

- [ ] WebSocket support for real-time monitoring
- [ ] Custom webhook integration
- [ ] Slack notifications
- [ ] Dashboard for decision history
- [ ] A/B testing different decision strategies
- [ ] Integration with incident management systems
