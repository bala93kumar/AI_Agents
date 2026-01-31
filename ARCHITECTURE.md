# Databricks AI Agent - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATABRICKS WORKSPACE                             │
│                    (Job Failures Detected)                              │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    AI AGENT (Main Orchestrator)                         │
│                     src/agent.py                                        │
│                                                                         │
│  ┌─ process_failed_job()                                              │
│  │  ├─ Get job run details (Databricks Client)                        │
│  │  ├─ Extract error message                                          │
│  │  ├─ Analyze with Pattern Engine                                    │
│  │  ├─ Analyze with Azure OpenAI LLM                                  │
│  │  ├─ Make decision (Decision Engine)                                │
│  │  └─ Execute action                                                 │
│  │                                                                     │
│  └─ monitor_jobs()                                                     │
│     └─ Check recent jobs for failures                                 │
└────┬────────────────┬────────────────┬────────────────┬─────────────────┘
     │                │                │                │
     ▼                ▼                ▼                ▼
┌─────────────┐┌──────────────┐┌──────────────┐┌───────────────┐
│ DATABRICKS  ││  AZURE       ││   DECISION   ││    EMAIL      │
│  CLIENT     ││  OPENAI      ││   ENGINE     ││  NOTIFIER     │
│             ││  CLIENT      ││              ││               │
│ PAT Token   ││              ││ Error        ││ SMTP Config   │
│ Based       ││ GPT-4 Model  ││ Pattern      ││ Professional  │
│ API Calls   ││ Error        ││ Analysis     ││ Email Gen     │
│             ││ Analysis     ││ LLM Results  ││               │
│ - Get Runs  ││ Param Gen    ││ Retry Logic  ││ - Send Errors │
│ - Submit    ││ Email Gen    ││ Escalation   ││ - Retry       │
│ - Cancel    ││              ││              ││ - Escalation  │
│ - List      ││              ││              ││               │
└─────────────┘└──────────────┘└──────────────┘└───────────────┘
                                      │
                                      ▼
                          ┌──────────────────────────┐
                          │  DECISION ACTIONS        │
                          │                          │
                          │ 1. RETRY (same params)   │
                          │ 2. RETRY_WITH_NEW_PARAMS │
                          │ 3. SEND_EMAIL            │
                          │ 4. ESCALATE              │
                          │ 5. IGNORE                │
                          └──────────────────────────┘
                                      │
                                      ▼
                          ┌──────────────────────────┐
                          │  MODEL FINE-TUNER        │
                          │  src/model_fine_tuner.py │
                          │                          │
                          │ - Training Data Prep     │
                          │ - Feedback Collection    │
                          │ - Performance Analysis   │
                          │ - Recommendations        │
                          └──────────────────────────┘
```

## Component Details

### 1. Configuration Layer (`src/config.py`)

Manages all configuration from environment variables:

```python
AgentConfig (main)
├── AzureOpenAIConfig
├── DatabricksConfig (PAT Token)
├── EmailConfig
└── System settings (log_level, max_retries)
```

**PAT Token Approach:**
- No workspace connector library needed
- Direct HTTP API calls
- Standard Authorization header: `Bearer {PAT_TOKEN}`
- Simpler dependency management
- Easier deployment

### 2. Databricks Client (`src/databricks_client.py`)

Direct API integration using PAT tokens:

```
Request Flow:
1. Client receives job failure
2. Makes REST API call to Databricks
3. Uses Bearer token for authentication
4. Returns structured response
5. Agent processes result

Key Methods:
- get_job_run()              # Get run details
- get_job_run_output()       # Get run output/errors
- submit_job_run()           # Submit new run with params
- cancel_job_run()           # Cancel failed run
- list_jobs()                # List recent jobs
- execute_sql_query()        # Run SQL on warehouse
```

### 3. Azure OpenAI Client (`src/azure_openai_client.py`)

LLM-powered error analysis:

```
Analysis Flow:
1. Receive error message + context
2. Send to Azure OpenAI GPT-4
3. Receive structured JSON response
4. Extract analysis components:
   - Error category
   - Root cause
   - Recommendation (retry/retry_with_params/email)
   - Suggested parameters
   - Severity level
```

### 4. Error Decision Engine (`src/error_decision_engine.py`)

Intelligent decision making:

```
Decision Process:
1. Pattern-based error classification
   ├─ Timeout → RETRY
   ├─ Resource → RETRY_WITH_NEW_PARAMS
   ├─ Permission → SEND_EMAIL
   ├─ Syntax → SEND_EMAIL
   ├─ Network → RETRY
   └─ Data → SEND_EMAIL

2. LLM analysis integration
   └─ May override pattern decision

3. Retry limit enforcement
   ├─ Check attempt_number < max_retries
   └─ Escalate if limit reached

4. Result combination
   └─ Return final decision with all context
```

### 5. Email Notifier (`src/email_notifier.py`)

Professional email notifications:

```
SMTP Integration:
- Gmail, Office365, or custom SMTP
- TLS/SSL support
- Authentication with credentials
- HTML + Text support

Email Types:
- Error escalation
- Retry notifications
- Professional formatting
- Rich error context
```

### 6. Model Fine-Tuner (`src/model_fine_tuner.py`)

Continuous learning and improvement:

```
Workflow:
1. Collect historical decisions
2. Prepare JSONL training data
3. Submit to Azure OpenAI for fine-tuning
4. Gather feedback on decisions
5. Analyze accuracy metrics
6. Generate improvement recommendations

Output:
- Accuracy percentage
- Decision-type breakdown
- Improvement suggestions
- Retraining guidance
```

## Data Flow Examples

### Example 1: Simple Timeout (Retry)

```
Job Fails with "timeout" error
    ↓
get_job_run() → Extract error message
    ↓
Pattern Engine → Matches "timeout" keyword
    ↓
LLM Analysis → "error_category: timeout, recommendation: retry"
    ↓
Decision Engine → ACTION: RETRY (same parameters)
    ↓
submit_job_run(job_id, original_params)
    ↓
Log decision + new run_id
```

### Example 2: Resource Issue (Retry with Params)

```
Job Fails with "out of memory" error
    ↓
get_job_run() + get_job_run_output()
    ↓
Pattern Engine → Matches "memory" keyword
    ↓
LLM Analysis → {
    "error_category": "resource",
    "recommendation": "RETRY_WITH_NEW_PARAMS",
    "suggested_params": {
        "memory_mb": 8192,
        "executor_cores": 4
    }
}
    ↓
Decision Engine → ACTION: RETRY_WITH_NEW_PARAMS
    ↓
submit_job_run(job_id, new_params)
    ↓
Send retry notification email
```

### Example 3: Permission Error (Escalate)

```
Job Fails with "permission denied" error
    ↓
get_job_run() + get_job_run_output()
    ↓
Pattern Engine → Matches "permission" keyword
    ↓
LLM Analysis → {
    "error_category": "permission",
    "recommendation": "SEND_EMAIL",
    "severity": "critical"
}
    ↓
Decision Engine → ACTION: SEND_EMAIL
    ↓
generate_email_content() (with LLM)
    ↓
send_escalation_notification(recipients)
    ↓
Log escalation + email sent
```

## Error Categories and Handling

| Category | Pattern | LLM Response | Action | Max Attempts |
|----------|---------|--------------|--------|--------------|
| Timeout | "timeout" | Confirm timeout | RETRY | Yes (then EMAIL) |
| Resource | "memory", "disk" | Suggest params | RETRY_PARAMS | Yes (then EMAIL) |
| Permission | "denied", "unauthorized" | Explain issue | EMAIL | 1 (no retry) |
| Syntax | "syntax error", "invalid" | Detail issue | EMAIL | 1 (no retry) |
| Network | "connection", "refused" | Confirm transient | RETRY | Yes (then EMAIL) |
| Data | "not found", "missing" | Identify data issue | EMAIL | 1 (no retry) |

## Configuration Example

```yaml
# Environment Variables (in .env)

# Azure OpenAI
AZURE_OPENAI_API_KEY=sk-...
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_MODEL=gpt-4

# Databricks PAT Token
DATABRICKS_WORKSPACE_URL=https://xxx.cloud.databricks.com
DATABRICKS_PAT_TOKEN=dapi...  ← Personal Access Token

# Email
EMAIL_ENABLED=true
EMAIL_SENDER=alerts@company.com
EMAIL_PASSWORD=app-specific-password

# Agent
LOG_LEVEL=INFO
MAX_RETRIES=3
```

## Integration Points

### 1. Databricks Webhooks
```python
# Setup webhook in Databricks to POST job failures
@app.route('/webhook/job-failure', methods=['POST'])
def handle_job_failure():
    data = request.json
    result = agent.process_failed_job(
        job_id=data['job_id'],
        run_id=data['run_id']
    )
    return {"status": "processed"}
```

### 2. Scheduled Monitoring
```python
# Run periodically (every 5 minutes)
def monitor_loop():
    result = agent.monitor_jobs(max_age_hours=1)
    for failed_job in result['failed_jobs']:
        agent.process_failed_job(...)
```

### 3. Model Fine-Tuning Pipeline
```python
# Daily/Weekly retraining
def retrain_model():
    # Collect historical decisions
    feedback = load_feedback_from_db()
    
    # Prepare training data
    tuner.prepare_training_data(feedback, "training.jsonl")
    
    # Submit to Azure OpenAI
    job_id = submit_fine_tuning_job("training.jsonl")
    
    # Track performance
    performance = tuner.analyze_model_performance(feedback)
    log_metrics(performance)
```

## Security Considerations

1. **PAT Token Security:**
   - Store in `.env` file (never commit)
   - Rotate regularly
   - Use service principals in production
   - Limited scope tokens (read-only where possible)

2. **Azure OpenAI Security:**
   - Store API key in `.env`
   - Use separate keys per environment
   - Monitor API usage
   - Set rate limits

3. **Email Security:**
   - Use app-specific passwords
   - Never store main credentials
   - Use TLS/SSL for SMTP
   - Restrict sender addresses

4. **Logging:**
   - Don't log sensitive credentials
   - Mask tokens/keys in logs
   - Use proper log levels in production

## Deployment Scenarios

### 1. Local Development
```bash
python -m pip install -r requirements.txt
python example_usage.py
```

### 2. Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/agent.py"]
```

### 3. Kubernetes Pod
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: databricks-ai-agent
spec:
  containers:
  - name: agent
    image: databricks-ai-agent:latest
    env:
    - name: DATABRICKS_PAT_TOKEN
      valueFrom:
        secretKeyRef:
          name: databricks-creds
          key: pat-token
```

### 4. Azure Function
```python
import azure.functions as func
from src.agent import DatabricksAIAgent

def main(req: func.HttpRequest):
    job_id = req.params.get('job_id')
    run_id = req.params.get('run_id')
    result = agent.process_failed_job(job_id, run_id)
    return func.HttpResponse(json.dumps(result))
```

## Monitoring and Logging

```python
# Structured logging
logger.info(f"Job processed: {job_id}, Decision: {decision['action']}", extra={
    "job_id": job_id,
    "run_id": run_id,
    "action": decision['action'],
    "error_category": decision['error_category'],
    "attempt": attempt_number
})

# Metrics to track:
- Total jobs processed
- Decision distribution
- Retry success rate
- Email send rate
- LLM accuracy
- Response time
```

## Performance Characteristics

- **Latency:** 5-15 seconds per job failure processing
- **Throughput:** Processes ~400 jobs/hour (single instance)
- **LLM Cost:** ~$0.01-0.05 per error analysis
- **Storage:** Training data grows ~1MB per 100 decisions
- **Scaling:** Horizontal (multiple instances, job queue)
