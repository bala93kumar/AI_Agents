# Databricks AI Agent - Complete Solution

## Fresh Clean Implementation

This is a **completely fresh** implementation of an AI Agent for Databricks with Azure OpenAI integration. All notebooks and previous code have been removed.

### ✨ Key Features

✅ **Databricks Integration** - PAT Token-based (no workspace connector library needed)
✅ **Azure OpenAI LLM** - Intelligent error analysis with GPT-4
✅ **Automated Decision Making** - Retry, retry with new params, or escalate
✅ **Error Pattern Recognition** - Pre-built patterns for common errors
✅ **Email Notifications** - Professional notifications for escalations
✅ **Model Fine-Tuning** - Continuous learning from decisions
✅ **Comprehensive Testing** - Unit tests included
✅ **Production Ready** - Logging, error handling, extensible design

---

## 📂 Project Structure

```
src/
├── agent.py                    # Main orchestrator (all logic here)
├── config.py                   # Configuration from environment
├── databricks_client.py         # Databricks API (PAT tokens)
├── azure_openai_client.py      # Azure OpenAI integration
├── error_decision_engine.py    # Error analysis & decision logic
├── email_notifier.py           # Email notifications
└── model_fine_tuner.py         # Model training utilities

Documentation/
├── README.md                   # Complete guide (start here)
├── QUICK_START.md             # 5-minute setup guide
├── ARCHITECTURE.md            # System design & data flow
└── .env.example               # Configuration template

Tests/
└── test_agent.py              # Unit tests (run with pytest)

Examples/
└── example_usage.py           # Usage examples
```

---

## 🚀 Quick Start (Copy-Paste)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your credentials

# 3. Run
python example_usage.py
```

---

## 🔧 Core Components

### 1. **Agent** (`src/agent.py`)
Main orchestrator that processes failed Databricks jobs:
- Retrieves job failure details from Databricks
- Analyzes error with both pattern matching and Azure OpenAI LLM
- Makes automated decision (retry, retry with new params, send email)
- Executes action and logs results

### 2. **Databricks Client** (`src/databricks_client.py`)
Direct Databricks API integration using Personal Access Tokens:
- No external SDKs needed - just `requests`
- Uses standard HTTP Bearer token authentication
- Methods: get_job_run, submit_job_run, cancel_job_run, list_jobs, etc.

### 3. **Azure OpenAI Client** (`src/azure_openai_client.py`)
Intelligent error analysis using GPT-4:
- Analyzes error messages contextually
- Suggests retry parameters if needed
- Generates professional email content
- Returns structured JSON responses

### 4. **Error Decision Engine** (`src/error_decision_engine.py`)
Smart decision making logic:
- Pre-trained pattern recognition for 6 error categories
- Integrates LLM analysis with pattern results
- Enforces retry limits (default: 3 attempts)
- Escalates after max retries

### 5. **Email Notifier** (`src/email_notifier.py`)
Professional email notifications:
- SMTP-based (works with Gmail, Office365, etc.)
- Sends escalation alerts with full error context
- Retry notifications
- Formatted for readability

### 6. **Model Fine-Tuner** (`src/model_fine_tuner.py`)
Continuous learning from decisions:
- Prepares training data in OpenAI format
- Collects feedback on decision quality
- Analyzes accuracy metrics
- Generates improvement recommendations

---

## 📊 Decision Flow

```
Job Fails
  ↓
Extract Error Message
  ↓
Pattern Engine (6 categories)
  ↓
Azure OpenAI Analysis (LLM)
  ↓
Decision Engine (combine)
  ↓
Action:
  ├─ RETRY (timeout)
  ├─ RETRY_WITH_NEW_PARAMS (resource issue)
  ├─ SEND_EMAIL (permission/syntax error)
  ├─ ESCALATE (max retries exceeded)
  └─ IGNORE (expected error)
```

---

## 🎯 Error Categories

| Error Type | Pattern Match | LLM Analysis | Action |
|-----------|---------------|--------------|--------|
| **Timeout** | "timeout" | Confirms transient | RETRY |
| **Resource** | "memory", "disk" | Suggests param increase | RETRY_PARAMS |
| **Permission** | "denied", "unauthorized" | Explains permission issue | EMAIL |
| **Syntax** | "syntax error", "invalid" | Details code issue | EMAIL |
| **Network** | "connection", "refused" | Confirms transient | RETRY |
| **Data** | "not found", "missing" | Identifies data problem | EMAIL |

---

## 🔐 Configuration

### Environment Variables

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Databricks (PAT Token)
DATABRICKS_WORKSPACE_URL=https://xxx.cloud.databricks.com
DATABRICKS_PAT_TOKEN=dapi...

# Email (Optional)
EMAIL_ENABLED=true
EMAIL_SENDER=alerts@company.com
EMAIL_PASSWORD=app-specific-password

# Settings
LOG_LEVEL=INFO
MAX_RETRIES=3
```

### Creating a Databricks PAT Token

1. Go to Databricks workspace
2. Click your profile → **User Settings**
3. **Developer** tab → **Access tokens**
4. **Generate new token**
5. Copy and save in `.env`

---

## 💡 Usage Examples

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

print(result['decision']['action'])  # What action was taken
```

### Monitor Jobs
```python
monitoring = agent.monitor_jobs(max_age_hours=24)
```

### Collect Feedback
```python
from src.model_fine_tuner import ModelFineTuner

tuner = ModelFineTuner(agent.llm_client)
feedback = tuner.collect_feedback(
    decision_id="dec_123",
    original_decision="retry",
    actual_outcome="success"
)
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest test_agent.py -v

# Run specific test
python -m pytest test_agent.py::TestErrorDecisionEngine -v

# With coverage
python -m pytest test_agent.py --cov=src
```

---

## 🌐 Integration Options

### 1. Databricks Webhook
```python
@app.route('/webhook', methods=['POST'])
def handle_failure():
    data = request.json
    result = agent.process_failed_job(
        job_id=data['job_id'],
        run_id=data['run_id']
    )
    return result
```

### 2. Scheduled Monitoring
```python
# Run every 5 minutes
while True:
    result = agent.monitor_jobs(max_age_hours=1)
    time.sleep(300)
```

### 3. Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "src/agent.py"]
```

### 4. Azure Function / Lambda
```python
def main(req):
    result = agent.process_failed_job(...)
    return func.HttpResponse(json.dumps(result))
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | **Start here** - Complete guide & architecture |
| [QUICK_START.md](QUICK_START.md) | 5-minute setup & common patterns |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Detailed system design & data flows |
| [example_usage.py](example_usage.py) | Code examples |
| [.env.example](.env.example) | Configuration template |

---

## ✅ Implementation Checklist

- [x] Databricks client with PAT token authentication
- [x] Azure OpenAI LLM integration
- [x] Error pattern recognition engine
- [x] Decision making logic with retry limits
- [x] Email notification system
- [x] Model fine-tuning utilities
- [x] Comprehensive error handling
- [x] Unit tests
- [x] Configuration management
- [x] Complete documentation
- [x] Usage examples
- [x] Quick start guide

---

## 🔍 Key Advantages

✅ **No External SDKs** - Just REST API with PAT tokens
✅ **Lightweight** - Minimal dependencies (openai, requests, python-dotenv)
✅ **Intelligent** - LLM-powered error analysis with GPT-4
✅ **Flexible** - Pattern-based + LLM analysis hybrid approach
✅ **Extensible** - Easy to add new error patterns or actions
✅ **Observable** - Comprehensive logging throughout
✅ **Testable** - Full test coverage with mocks
✅ **Production-Ready** - Error handling, retry logic, escalation
✅ **Trainable** - Continuous learning from feedback
✅ **Well-Documented** - Multiple documentation files

---

## 🚦 Next Steps

1. **Configure environment** - Copy `.env.example` to `.env`
2. **Test locally** - Run `python example_usage.py`
3. **Set up webhook** - Integrate with Databricks
4. **Monitor** - Check logs for decisions
5. **Train model** - Collect feedback to improve
6. **Automate** - Deploy as service/function

---

## 📞 Support

For issues:
1. Check [QUICK_START.md](QUICK_START.md) troubleshooting section
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design
3. Check logs: `export LOG_LEVEL=DEBUG`
4. Run tests: `python -m pytest test_agent.py -v`

---

## 📝 Summary

This is a **complete, production-ready AI agent** for:
- ✅ Detecting Databricks job failures
- ✅ Analyzing errors intelligently (pattern + LLM)
- ✅ Making automated decisions
- ✅ Retrying with optimized parameters
- ✅ Escalating critical issues via email
- ✅ Learning from feedback to improve

All using **clean, simple, dependency-light code** with **PAT token authentication** to Databricks.

**Get started in 5 minutes - see [QUICK_START.md](QUICK_START.md)**

