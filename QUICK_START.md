# Quick Start - Databricks AI Agent

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env File
```bash
cp .env.example .env
```

Fill in your credentials:
- **Azure OpenAI:** Get from Azure Portal
- **Databricks:** Workspace URL + PAT Token
- **Email:** (Optional) SMTP credentials

### 3. Test Configuration
```python
from src.config import AgentConfig

config = AgentConfig.from_env()
print(f"✓ Azure OpenAI: {config.azure_openai.deployment_name}")
print(f"✓ Databricks: {config.databricks.workspace_url}")
print(f"✓ Email: {config.email.enabled}")
```

### 4. Create Databricks PAT Token

1. Log into Databricks workspace
2. Click profile → **User Settings**
3. **Developer** tab → **Access tokens**
4. **Generate new token**
5. Copy token to `.env` → `DATABRICKS_PAT_TOKEN`

### 5. Run Agent
```bash
python example_usage.py
```

---

## Common Usage Patterns

### Process a Failed Job
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

print(f"Decision: {result['decision']['action']}")
print(f"Analysis: {result['analysis']}")
```

### Integrate with Databricks Webhook
```python
from flask import Flask, request
from src.agent import DatabricksAIAgent
from src.config import AgentConfig

app = Flask(__name__)
agent = DatabricksAIAgent(AgentConfig.from_env())

@app.route('/databricks-webhook', methods=['POST'])
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

### Monitor Recent Jobs
```python
result = agent.monitor_jobs(max_age_hours=24)
print(f"Checked: {result['jobs_checked']} jobs")
print(f"Failed: {len(result['failed_jobs'])} jobs")
```

### Collect Feedback for Model Training
```python
from src.model_fine_tuner import ModelFineTuner

tuner = ModelFineTuner(agent.llm_client)

# After a decision is made and outcome is known
feedback = tuner.collect_feedback(
    decision_id="dec_123",
    original_decision="retry",
    actual_outcome="success",  # or "failure"
    feedback="Decision was correct"
)

# Analyze performance
performance = tuner.analyze_model_performance([feedback])
print(f"Accuracy: {performance['accuracy_percentage']}%")
```

---

## Decision Actions

When a job fails, the agent can take these actions:

| Action | When | Example |
|--------|------|---------|
| **RETRY** | Transient error | Timeout, network error |
| **RETRY_WITH_NEW_PARAMS** | Resource issue | Out of memory → increase memory |
| **SEND_EMAIL** | Manual review needed | Permission error, syntax error |
| **ESCALATE** | Multiple failures | Max retries exceeded |
| **IGNORE** | Expected error | Deprecated function warning |

---

## Error Patterns

The agent automatically recognizes these error types:

```
TIMEOUT
├─ Keywords: timeout, timed out, deadline exceeded
├─ Action: RETRY
└─ Success Rate: ~70-80%

RESOURCE
├─ Keywords: memory, disk space, out of (resource)
├─ Action: RETRY_WITH_NEW_PARAMS
└─ Success Rate: ~60-70%

PERMISSION
├─ Keywords: permission, denied, unauthorized
├─ Action: SEND_EMAIL (needs manual fix)
└─ Manual Action Required

SYNTAX
├─ Keywords: syntax error, invalid, compilation
├─ Action: SEND_EMAIL (needs code fix)
└─ Manual Action Required

NETWORK
├─ Keywords: connection, refused, network error
├─ Action: RETRY
└─ Success Rate: ~80-90%

DATA
├─ Keywords: not found, no such file, missing
├─ Action: SEND_EMAIL (needs data fix)
└─ Manual Action Required
```

---

## Configuration Reference

### Environment Variables

```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_MODEL=gpt-4

# Databricks (PAT Token)
DATABRICKS_WORKSPACE_URL=https://xxx.cloud.databricks.com
DATABRICKS_PAT_TOKEN=dapi...

# Email (Optional)
EMAIL_ENABLED=true
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SENDER=your-email@example.com
EMAIL_PASSWORD=app-password

# Agent Settings
LOG_LEVEL=INFO
MAX_RETRIES=3
```

---

## Testing

```bash
# Run all tests
python -m pytest test_agent.py -v

# Run specific test class
python -m pytest test_agent.py::TestErrorDecisionEngine -v

# Run with coverage
python -m pytest test_agent.py --cov=src
```

---

## Troubleshooting

### "Authentication failed"
- Check `DATABRICKS_PAT_TOKEN` is correct
- Check `AZURE_OPENAI_API_KEY` is valid
- Verify tokens aren't expired

### "Connection refused"
- Verify `DATABRICKS_WORKSPACE_URL` format
- Check firewall/VPN access
- Confirm Databricks workspace is running

### "Email not sending"
- Enable: `EMAIL_ENABLED=true`
- For Gmail: Use app-specific password
- Check SMTP settings match your provider

### "LLM not responding"
- Verify Azure OpenAI endpoint is correct
- Check deployment name matches your setup
- Verify API version is supported

### "Job not found"
- Confirm job ID exists in workspace
- Check job hasn't been deleted
- Verify workspace URL is correct

---

## Logging

View detailed logs:

```bash
# Increase log level
export LOG_LEVEL=DEBUG
python example_usage.py

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

Key log patterns to look for:
```
INFO: Error analysis completed: retry
INFO: Decision made: RETRY
INFO: Job retry submitted with run_id: 123456
INFO: Email sent to [recipients]
```

---

## Next Steps

1. **Set up webhook:** Integrate with Databricks to auto-process failures
2. **Monitor:** Set up dashboard to track agent decisions
3. **Train model:** Collect feedback to improve decision accuracy
4. **Automate:** Run agent on a schedule or via job triggers
5. **Integrate:** Connect to incident management systems (PagerDuty, etc.)

---

## Files Reference

| File | Purpose |
|------|---------|
| `src/agent.py` | Main agent orchestrator |
| `src/config.py` | Configuration management |
| `src/databricks_client.py` | Databricks API (PAT tokens) |
| `src/azure_openai_client.py` | Azure OpenAI integration |
| `src/error_decision_engine.py` | Decision making logic |
| `src/email_notifier.py` | Email notifications |
| `src/model_fine_tuner.py` | Model training utilities |
| `example_usage.py` | Usage examples |
| `test_agent.py` | Unit tests |
| `README.md` | Full documentation |
| `ARCHITECTURE.md` | System design |
| `.env.example` | Configuration template |
