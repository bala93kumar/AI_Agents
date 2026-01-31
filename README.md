# Databricks AI Agent - Fresh Solution

## Quick Start Guide

### 1. Setup

```bash
# Clone or navigate to project
cd c:\Users\balak\GitProjects\AI_Agents

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

**Required Environment Variables:**

#### Azure OpenAI
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT`: Your deployment name (e.g., gpt-4)

#### Databricks (PAT Token)
- `DATABRICKS_WORKSPACE_URL`: Your Databricks workspace URL
- `DATABRICKS_PAT_TOKEN`: Your Personal Access Token (create in Databricks workspace settings)

#### Email Notifications (Optional)
- `EMAIL_ENABLED`: true/false
- `EMAIL_SENDER`: Your email address
- `EMAIL_PASSWORD`: App-specific password (for Gmail, use app passwords)

### 3. Architecture Overview

```
AI Agent for Databricks
│
├── Azure OpenAI Client
│   ├── Error Analysis (LLM)
│   ├── Parameter Optimization
│   └── Email Content Generation
│
├── Databricks Client (PAT Token)
│   ├── Job Management
│   ├── Run Control
│   └── Cluster Operations
│
├── Error Decision Engine
│   ├── Pattern Recognition
│   ├── LLM Analysis Integration
│   └── Decision Making Logic
│
├── Email Notifier
│   └── Notification Delivery
│
└── Model Fine-Tuner
    ├── Training Data Preparation
    ├── Feedback Collection
    └── Performance Analysis
```

### 4. Core Components

#### **src/agent.py** - Main Agent
Main orchestrator that:
- Monitors Databricks jobs for failures
- Analyzes errors with Azure OpenAI
- Makes automated decisions (retry, retry with new params, send email)
- Executes actions
- Handles escalation

```python
from src.config import AgentConfig
from src.agent import DatabricksAIAgent

config = AgentConfig.from_env()
agent = DatabricksAIAgent(config)

result = agent.process_failed_job(
    job_id=123456,
    run_id=789012,
    attempt_number=1
)
```

#### **src/databricks_client.py** - Databricks Integration (PAT Token)
Direct API calls using Personal Access Token:
- Get job run details
- Submit job runs with parameters
- Cancel runs
- List jobs and clusters
- Execute SQL queries

```python
from src.databricks_client import DatabricksClient
from src.config import DatabricksConfig

config = DatabricksConfig.from_env()
client = DatabricksClient(config)

# Submit a job run
result = client.submit_job_run(job_id=123, parameters={"param": "value"})
```

#### **src/azure_openai_client.py** - LLM Integration
Azure OpenAI for intelligent error analysis:
- Analyze errors and suggest actions
- Generate optimized parameters for retry
- Create professional email notifications

```python
from src.azure_openai_client import AzureOpenAIClient
from src.config import AzureOpenAIConfig

config = AzureOpenAIConfig.from_env()
client = AzureOpenAIClient(config)

analysis = client.analyze_error(
    error_message="Out of memory error",
    job_context={"job_id": 123}
)
```

#### **src/error_decision_engine.py** - Decision Logic
Makes decisions on how to handle errors:
- Pattern-based error classification
- LLM analysis integration
- Retry logic with max attempt limits
- Escalation handling

```python
from src.error_decision_engine import ErrorDecisionEngine

engine = ErrorDecisionEngine(max_retries=3)

decision = engine.make_decision(
    error_message="Timeout error",
    job_context={"job_id": 123, "attempt_number": 1},
    llm_analysis=analysis
)
```

#### **src/email_notifier.py** - Notifications
Sends email notifications for errors:
- Error escalation emails
- Retry notifications
- Professional formatting

```python
from src.email_notifier import EmailNotifier

notifier.send_escalation_notification(
    job_id="123",
    run_id=789012,
    error_category="resource",
    root_cause="Out of memory",
    priority="high",
    error_message="...",
    recipients=["team@example.com"]
)
```

#### **src/model_fine_tuner.py** - Continuous Improvement
Fine-tune the AI model with feedback:
- Prepare training data from historical decisions
- Collect feedback on decisions
- Analyze model performance
- Generate improvement recommendations

```python
from src.model_fine_tuner import ModelFineTuner

tuner = ModelFineTuner(azure_client)

# Prepare training data
tuner.prepare_training_data(error_samples, "training.jsonl")

# Analyze performance
performance = tuner.analyze_model_performance(feedback_records)
recommendations = tuner.generate_improvement_recommendations(performance)
```

### 5. Decision Flow

```
Job Failure Detected
    ↓
Extract Error Message
    ↓
Analyze with Pattern Engine
    ↓
Analyze with Azure OpenAI LLM
    ↓
Decision Engine (combine analyses)
    ↓
Determine Action:
    ├─ RETRY (simple timeout)
    ├─ RETRY_WITH_NEW_PARAMS (resource issue)
    ├─ SEND_EMAIL (permission, syntax error)
    ├─ ESCALATE (critical, manual review needed)
    └─ IGNORE (acceptable errors)
    ↓
Execute Action & Log Decision
```

### 6. Error Categories

The agent recognizes and handles:

| Error Type | Keywords | Action | Priority |
|-----------|----------|--------|----------|
| **Timeout** | timeout, timed out, deadline exceeded | RETRY | Medium |
| **Resource** | out of memory, disk space, insufficient | RETRY_WITH_NEW_PARAMS | High |
| **Permission** | permission denied, unauthorized | SEND_EMAIL | Critical |
| **Syntax** | syntax error, invalid, compilation failed | SEND_EMAIL | Critical |
| **Network** | connection refused, network error | RETRY | High |
| **Data** | no such file, not found | SEND_EMAIL | Critical |

### 7. Usage Examples

#### Process a Failed Job
```python
result = agent.process_failed_job(
    job_id=123456,
    run_id=789012,
    attempt_number=1
)

print(result['decision']['action'])  # What action was taken
print(result['analysis'])            # LLM analysis results
```

#### Monitor Jobs
```python
monitoring = agent.monitor_jobs(max_age_hours=24)
# Checks last 24 hours of jobs for failures
```

#### Collect Feedback for Model Improvement
```python
feedback = model_tuner.collect_feedback(
    decision_id="dec_123",
    original_decision="retry",
    actual_outcome="retry",
    feedback="Decision was correct"
)
```

### 8. Testing

```bash
# Run unit tests
python -m pytest test_agent.py -v

# Run specific test
python -m pytest test_agent.py::TestErrorDecisionEngine -v
```

### 9. Running the Agent

#### As a Standalone Script
```bash
python example_usage.py
```

#### As a Service (with webhook)
You can integrate this with Databricks webhooks to automatically process job failures:

```python
from flask import Flask, request
from src.agent import DatabricksAIAgent
from src.config import AgentConfig

app = Flask(__name__)
agent = DatabricksAIAgent(AgentConfig.from_env())

@app.route('/webhook/job-failure', methods=['POST'])
def handle_job_failure():
    data = request.json
    result = agent.process_failed_job(
        job_id=data['job_id'],
        run_id=data['run_id']
    )
    return result

if __name__ == '__main__':
    app.run(port=5000)
```

### 10. Logging

Configure logging level via environment variable:

```bash
# Set log level
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR

python example_usage.py
```

### 11. Creating Databricks PAT Token

1. Go to Databricks workspace
2. Click on your profile icon → User settings
3. Go to "Developer" tab
4. Under "Access tokens", click "Generate new token"
5. Copy the token and add to `.env` as `DATABRICKS_PAT_TOKEN`

### 12. Troubleshooting

**Issue: Authentication Failed**
- Verify `DATABRICKS_PAT_TOKEN` is correct and not expired
- Verify `AZURE_OPENAI_API_KEY` is valid

**Issue: Job Not Found**
- Ensure `DATABRICKS_WORKSPACE_URL` is correct
- Check that job ID exists in your workspace

**Issue: Email Not Sending**
- Ensure `EMAIL_ENABLED=true`
- For Gmail, use app-specific password (not regular password)
- Verify SMTP server and port settings

**Issue: LLM Not Responding**
- Check Azure OpenAI endpoint and deployment name
- Verify API key and version are correct

### 13. Next Steps

1. Set up Databricks webhook integration
2. Create monitoring dashboard
3. Train model with historical error data
4. Set up automated model retraining
5. Create incident tracking integration

## Project Structure

```
AI_Agents/
├── src/
│   ├── __init__.py
│   ├── agent.py                    # Main agent
│   ├── config.py                   # Configuration
│   ├── azure_openai_client.py     # LLM integration
│   ├── databricks_client.py        # Databricks API (PAT tokens)
│   ├── error_decision_engine.py    # Decision logic
│   ├── email_notifier.py           # Email notifications
│   └── model_fine_tuner.py         # Fine-tuning utilities
├── example_usage.py                # Usage examples
├── test_agent.py                   # Unit tests
├── requirements.txt                # Dependencies
├── .env.example                    # Example environment variables
└── README.md                       # This file
```

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
