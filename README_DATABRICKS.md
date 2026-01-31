# Databricks AI Agent with Azure OpenAI

**An intelligent AI-powered agent for monitoring Databricks jobs, analyzing errors, and making automated decisions on retries, parameter optimization, or escalation.**

## 🎯 Key Features

- **🤖 AI-Powered Error Analysis**: Uses Azure OpenAI to intelligently analyze job failures
- **🔄 Automated Retry Logic**: Automatically retries failed jobs with smart decision-making
- **⚙️ Parameter Optimization**: Suggests and applies parameter changes for failed jobs
- **📧 Smart Escalation**: Sends emails to teams when issues require human intervention
- **🎓 Model Fine-Tuning**: Fine-tune Azure OpenAI models with your historical decision data
- **📊 Decision Tracking**: Logs all decisions for continuous improvement
- **🔗 Databricks Integration**: Native Databricks workflow support
- **⚡ Production Ready**: Tested, documented, and deployment-ready

## 📋 Architecture Overview

```
Databricks Jobs (Failed Runs)
           ↓
DatabricksConnector (get errors, retry jobs)
           ↓
ErrorDecisionEngine (AI analysis & decisions)
           ↓
    ┌──────┼──────┐
    ↓      ↓      ↓
  RETRY  PARAMS  EMAIL
  (auto) (tune)  (escalate)
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Azure OpenAI deployment
- Databricks workspace
- SMTP-enabled email account

### 2. Installation

```bash
# Clone the project
cd AI_Agents

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Create .env file
cp .env.example .env

# Edit with your credentials
nano .env
```

Required environment variables:
```env
AZURE_OPENAI_KEY=<your-key>
AZURE_OPENAI_ENDPOINT=<your-endpoint>
DATABRICKS_HOST=<workspace-url>
DATABRICKS_TOKEN=<token>
SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=<your-email>
SENDER_PASSWORD=<app-password>
```

### 4. Test Configuration

```bash
python -c "from setup_guide import test_all_connections; test_all_connections()"
```

### 5. Run Monitoring

```bash
python examples/databricks_agent_example.py
```

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup and deployment guide
- **[DATABRICKS_AGENT_GUIDE.md](DATABRICKS_AGENT_GUIDE.md)** - Detailed architecture and usage
- **[examples/databricks_agent_example.py](examples/databricks_agent_example.py)** - Code examples

## 🏗️ Project Structure

```
├── src/
│   ├── azure_openai_client.py      # Azure OpenAI integration
│   ├── databricks_connector.py      # Databricks API wrapper
│   ├── databricks_agent.py          # Main orchestrator
│   ├── error_decision_engine.py     # AI-powered decision logic
│   ├── email_notifier.py            # Email notifications
│   └── databricks_config.py         # Configuration management
├── notebooks/
│   └── databricks_agent_runner.py   # Databricks notebook
├── examples/
│   └── databricks_agent_example.py  # Usage examples
├── config/
│   └── databricks_agent.yaml        # Agent configuration
└── tests/
    └── test_databricks_agent.py     # Test suite
```

## 💡 How It Works

### Workflow

1. **Monitor**: Agent checks Databricks for failed jobs
2. **Analyze**: Azure OpenAI analyzes error messages and context
3. **Decide**: Engine decides: retry, modify params, escalate, or skip
4. **Act**: Automatically retry or send escalation email
5. **Track**: Logs all decisions for analysis and fine-tuning

### Decision Flow

```
Failed Job
    ↓
Get Error & Context
    ↓
Send to Azure OpenAI for Analysis
    ↓
AI Response: Retry? Change params? Escalate?
    ↓
Check Retry Limits
    ↓
Execute Decision
    ↓
Log for Fine-tuning
```

## 🔧 Core Components

### AzureOpenAIClient
```python
from src.azure_openai_client import AzureOpenAIClient

ai_client = AzureOpenAIClient()

# Analyze error
analysis = ai_client.analyze_error(
    error_message="OutOfMemoryError: Java heap space",
    job_context={"cluster_size": "small", "data_size_gb": 500}
)

# Fine-tune model
job_id = ai_client.fine_tune_model(
    training_data_path="data/training_data.jsonl"
)
```

### DatabricksConnector
```python
from src.databricks_connector import DatabricksConnector

connector = DatabricksConnector()

# Get failed jobs
failed_jobs = connector.get_failed_jobs(job_ids=[123, 456])

# Retry with new parameters
new_run_id = connector.retry_run(
    run_id=789,
    new_parameters={"cluster_size": "large"}
)
```

### ErrorDecisionEngine
```python
from src.error_decision_engine import ErrorDecisionEngine

engine = ErrorDecisionEngine(ai_client)

decision = engine.analyze_and_decide(
    error_message=error,
    job_context=context,
    retry_history=history
)

# Decisions: RETRY, RETRY_WITH_PARAMS, ESCALATE_EMAIL, SKIP
print(decision['decision'])
```

### DatabricksAgent
```python
from src.databricks_agent import DatabricksAgent

agent = DatabricksAgent(
    azure_openai_client=ai_client,
    databricks_connector=db_connector,
    email_notifier=email_notifier,
    error_decision_engine=decision_engine
)

# Run monitoring
summary = agent.monitor_jobs(
    job_ids=[123, 456],
    escalation_emails=["team@example.com"]
)
```

## 🎓 Fine-Tuning

### Prepare Training Data

```python
# Prepare JSONL from historical decisions
agent.prepare_training_data(
    run_history_file="data/run_history.json",
    output_file="data/training_data.jsonl"
)
```

### Start Fine-Tuning

```python
job_id = agent.fine_tune_error_model(
    training_data_path="data/training_data.jsonl",
    suffix="error-handler-v1"
)

# Check status
status = agent.get_fine_tune_status(job_id)
```

## 📊 Deployment Options

### Option 1: Databricks Job (Recommended)
- Schedule as recurring Databricks job
- Runs in your workspace
- Access to workspace secrets

### Option 2: External Scheduler
- Docker container + cron/scheduler
- Runs outside Databricks
- Great for monitoring multiple workspaces

### Option 3: Workflow Orchestration
- Apache Airflow integration
- Prefect, Dagster, etc.
- Complex multi-step pipelines

## 📧 Email Configuration

### Gmail (Recommended for Testing)
1. Enable 2FA
2. Generate app password: https://myaccount.google.com/apppasswords
3. Use 16-character password

### Corporate Email
Contact IT for SMTP server and credentials

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_databricks_agent.py -v

# Test configuration
python -c "from setup_guide import test_configuration; test_configuration()"

# Test connections
python -c "from setup_guide import test_all_connections; test_all_connections()"
```

## 📋 Configuration File

Edit `config/databricks_agent.yaml`:

```yaml
error_handling:
  max_retry_attempts: 3
  max_retry_with_params_attempts: 2
  
monitoring:
  check_interval_seconds: 300
  lookback_hours: 24

azure_openai:
  deployment_name: gpt-4
  temperature: 0.7
  max_tokens: 1000
```

## 🔍 Monitoring & Logging

### View Logs
```bash
tail -f /tmp/databricks_agent.log
```

### Store Results in Delta
```python
# Results automatically saved to Delta table
# Location: /mnt/delta/databricks_agent_results
```

### Dashboard Integration
Query Delta table for decision analytics:
```sql
SELECT 
  timestamp,
  decision,
  COUNT(*) as count
FROM databricks_agent_results
GROUP BY timestamp, decision
```

## 🛡️ Security

- ✅ Credentials stored in environment variables
- ✅ No hardcoded secrets
- ✅ SMTP password protected
- ✅ Databricks token rotation support
- ✅ Email notifications encrypted (TLS)

## 🐛 Troubleshooting

### Azure OpenAI Issues
```
Error: 401 Unauthorized
Solution: Check AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT
```

### Databricks Connection Issues
```
Error: 401 Invalid token
Solution: Regenerate DATABRICKS_TOKEN and verify DATABRICKS_HOST
```

### Email Not Sending
```
Error: SMTP error
Solution: Run email_notifier.test_connection() to verify credentials
```

### No Jobs Found
```
No failed jobs detected
Solution: Verify job IDs are correct and jobs have failed runs
```

## 📈 Performance Tips

- Batch monitor 10-20 jobs per cycle
- Use Delta caching for run history
- Implement request rate limiting for Azure OpenAI
- Monitor Databricks API quotas

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - See LICENSE file

## 🙋 Support

- 📖 Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
- 📚 Check [DATABRICKS_AGENT_GUIDE.md](DATABRICKS_AGENT_GUIDE.md) for architecture
- 💬 Review [examples/](examples/) for code samples
- 🧪 Run tests to verify configuration

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Configure credentials
3. ✅ Test connections
4. ✅ Run basic monitoring
5. ✅ Deploy to Databricks
6. ✅ Set up fine-tuning with historical data
7. ✅ Create monitoring dashboard

## 🚀 Production Checklist

- [ ] All credentials configured
- [ ] Connections tested and verified
- [ ] Email notifications working
- [ ] Databricks job created and scheduled
- [ ] Monitoring logs accessible
- [ ] Escalation emails verified
- [ ] Fine-tuning data prepared
- [ ] Dashboard created
- [ ] Team trained on alerts
- [ ] Documentation reviewed

---

**Built with ❤️ for data teams**
