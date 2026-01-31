# Implementation Guide - Databricks AI Agent

## What You Have

A **complete, production-ready AI Agent** with 7 core modules:

```
src/
├── agent.py (550+ lines)              # Main orchestrator
├── config.py (100+ lines)             # Configuration management
├── databricks_client.py (250+ lines)  # Databricks API (PAT tokens)
├── azure_openai_client.py (200+ lines) # LLM integration
├── error_decision_engine.py (250+ lines) # Decision logic
├── email_notifier.py (150+ lines)     # Email notifications
└── model_fine_tuner.py (200+ lines)   # Model fine-tuning
```

**Total Code:** ~1600 lines of production-ready Python

---

## Step-by-Step Implementation

### Step 1: Environment Setup (5 minutes)

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration (5 minutes)

```bash
# Copy template
cp .env.example .env

# Edit .env with:
# 1. Azure OpenAI credentials (from Azure Portal)
# 2. Databricks PAT token (from workspace settings)
# 3. Email credentials (optional)
```

### Step 3: Test Configuration (5 minutes)

```python
from src.config import AgentConfig
from src.databricks_client import DatabricksClient

config = AgentConfig.from_env()

# Test Databricks connection
client = DatabricksClient(config.databricks)
if client.get_workspace_status():
    print("✓ Databricks connection works!")
else:
    print("✗ Check DATABRICKS_PAT_TOKEN")

# Test Azure OpenAI
from src.azure_openai_client import AzureOpenAIClient
llm = AzureOpenAIClient(config.azure_openai)
print("✓ Azure OpenAI configured!")
```

### Step 4: First Job Processing (10 minutes)

```python
from src.config import AgentConfig
from src.agent import DatabricksAIAgent

config = AgentConfig.from_env()
agent = DatabricksAIAgent(config)

# Process a failed job (replace with real job/run IDs)
result = agent.process_failed_job(
    job_id=YOUR_JOB_ID,
    run_id=YOUR_RUN_ID,
    attempt_number=1
)

print(f"Status: {result['success']}")
print(f"Decision: {result['decision']['action']}")
print(f"Error: {result['error_message']}")
```

### Step 5: Run Tests (5 minutes)

```bash
python -m pytest test_agent.py -v
```

---

## Integration Paths

### Path A: Webhook Integration (Recommended for Production)

```python
# requirements.txt - add
flask>=2.3.0

# main.py
from flask import Flask, request, jsonify
from src.agent import DatabricksAIAgent
from src.config import AgentConfig
import logging

app = Flask(__name__)
agent = DatabricksAIAgent(AgentConfig.from_env())
logger = logging.getLogger(__name__)

@app.route('/webhook/databricks-job-failure', methods=['POST'])
def handle_job_failure():
    """Webhook endpoint for Databricks job failures"""
    try:
        data = request.json
        
        # Process the failed job
        result = agent.process_failed_job(
            job_id=data['job_id'],
            run_id=data['run_id'],
            attempt_number=data.get('attempt_number', 1)
        )
        
        logger.info(f"Job processed: {result['job_id']}, "
                   f"Decision: {result['decision']['action']}")
        
        return jsonify({
            "status": "processed",
            "decision": result['decision']['action'].value
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing job: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.run(host='0.0.0.0', port=5000)

# Setup Databricks webhook:
# 1. Create webhook in Databricks workspace
# 2. Post URL: https://your-server:5000/webhook/databricks-job-failure
# 3. Events: Job state change → Failed
```

### Path B: Scheduled Monitoring

```python
# monitor.py
import time
import logging
from src.agent import DatabricksAIAgent
from src.config import AgentConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_loop():
    """Monitor jobs continuously"""
    agent = DatabricksAIAgent(AgentConfig.from_env())
    
    while True:
        try:
            # Check jobs from last hour
            result = agent.monitor_jobs(max_age_hours=1)
            
            logger.info(f"Checked {result['jobs_checked']} jobs, "
                       f"Found {len(result['failed_jobs'])} failures")
            
            # Wait 5 minutes before next check
            time.sleep(300)
            
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")
            time.sleep(60)

if __name__ == '__main__':
    monitor_loop()

# Run with:
# python monitor.py
```

### Path C: Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Set environment
ENV LOG_LEVEL=INFO

# Run agent
CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t databricks-ai-agent .
docker run -e DATABRICKS_PAT_TOKEN=$DATABRICKS_PAT_TOKEN \
           -e AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
           databricks-ai-agent
```

### Path D: Azure Function

```python
import azure.functions as func
from src.agent import DatabricksAIAgent
from src.config import AgentConfig
import json
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function handler"""
    try:
        req_body = req.get_json()
        
        config = AgentConfig.from_env()
        agent = DatabricksAIAgent(config)
        
        result = agent.process_failed_job(
            job_id=req_body['job_id'],
            run_id=req_body['run_id'],
            attempt_number=req_body.get('attempt_number', 1)
        )
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500
        )
```

### Path E: Kubernetes Pod

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: databricks-ai-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: databricks-ai-agent
  template:
    metadata:
      labels:
        app: databricks-ai-agent
    spec:
      containers:
      - name: agent
        image: databricks-ai-agent:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABRICKS_PAT_TOKEN
          valueFrom:
            secretKeyRef:
              name: databricks-creds
              key: pat-token
        - name: AZURE_OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: azure-openai-creds
              key: api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: databricks-ai-agent
spec:
  selector:
    app: databricks-ai-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

---

## Advanced Usage

### Custom Error Patterns

```python
# Add custom error pattern
from src.error_decision_engine import ErrorDecisionEngine

engine = ErrorDecisionEngine()

# Add new pattern
engine.error_patterns["custom_error"] = {
    "keywords": ["custom_keyword", "my_error"],
    "action": DecisionAction.RETRY,
    "priority": "high"
}
```

### Model Fine-Tuning

```python
from src.model_fine_tuner import ModelFineTuner
import json

tuner = ModelFineTuner(agent.llm_client)

# Prepare training data from historical decisions
error_samples = [
    {
        "error_message": "timeout error",
        "context": {"job_id": 123},
        "decision": "retry",
        "error_category": "timeout",
        "root_cause": "Job took too long"
    },
    # ... more samples
]

# Create training file
tuner.prepare_training_data(error_samples, "training.jsonl")

# Collect feedback
feedback_records = []
for decision in historical_decisions:
    feedback = tuner.collect_feedback(
        decision_id=decision['id'],
        original_decision=decision['action'],
        actual_outcome=decision['actual_result'],
        feedback=decision['feedback']
    )
    feedback_records.append(feedback)

# Analyze performance
performance = tuner.analyze_model_performance(feedback_records)
print(f"Accuracy: {performance['accuracy_percentage']}%")

# Get recommendations
recommendations = tuner.generate_improvement_recommendations(performance)
for rec in recommendations:
    print(f"- {rec}")
```

### Custom Actions

```python
# Extend the agent with custom actions
from src.agent import DatabricksAIAgent

class CustomAgent(DatabricksAIAgent):
    def _execute_action(self, decision, job_id, run_id, job_context, error_message):
        """Override to add custom actions"""
        
        if decision['action'].value == 'custom_action':
            return self._handle_custom_action(
                job_id, error_message, job_context
            )
        
        return super()._execute_action(
            decision, job_id, run_id, job_context, error_message
        )
    
    def _handle_custom_action(self, job_id, error_message, context):
        """Custom action handler"""
        # Your custom logic here
        return {"status": "custom_action_executed"}
```

---

## Monitoring & Observability

### Structured Logging

```python
import json
from pythonjsonlogger import jsonlogger

# Configure JSON logging for production
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# All logs will be JSON formatted for easy parsing
# Usage: logger.info("Job processed", extra={"job_id": 123, "status": "success"})
```

### Metrics to Track

```python
# Track these metrics in your monitoring system
metrics = {
    "total_jobs_processed": 1000,
    "retry_count": 300,
    "retry_success_rate": 0.75,
    "email_sent_count": 200,
    "llm_accuracy": 0.82,
    "average_processing_time_ms": 8500,
    "error_categories": {
        "timeout": 300,
        "resource": 250,
        "permission": 150,
        "syntax": 100,
        "network": 150,
        "data": 50
    }
}
```

### Dashboard Example (Prometheus/Grafana)

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
job_processed = Counter('databricks_jobs_processed', 'Total jobs processed')
retry_count = Counter('databricks_retries', 'Total retry attempts')
processing_time = Histogram('databricks_processing_seconds', 'Processing time')
llm_accuracy = Gauge('databricks_llm_accuracy', 'LLM accuracy percentage')

# Usage
job_processed.inc()
with processing_time.time():
    result = agent.process_failed_job(...)
llm_accuracy.set(82.5)
```

---

## Troubleshooting Guide

### Issue: PAT Token Not Working

```python
# Debug
from src.databricks_client import DatabricksClient
import requests

client = DatabricksClient(config.databricks)

# Test connection
try:
    response = requests.get(
        f"{client.base_url}/workspace/get-status",
        headers=client.headers,
        params={"path": "/"},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Fix:
# 1. Verify PAT token format: dapi[a-z0-9]{32}
# 2. Check token not expired
# 3. Regenerate token if needed
# 4. Verify workspace URL format
```

### Issue: Azure OpenAI Not Responding

```python
# Debug
from src.azure_openai_client import AzureOpenAIClient

client = AzureOpenAIClient(config.azure_openai)

try:
    analysis = client.analyze_error(
        "Test error message",
        {"job_id": 0}
    )
    print(f"Analysis: {analysis}")
except Exception as e:
    print(f"Error: {e}")

# Fix:
# 1. Verify endpoint format: https://xxx.openai.azure.com/
# 2. Check deployment name (not model name)
# 3. Verify API version: 2024-02-15-preview
# 4. Test with curl:
#    curl -X POST https://your-resource.openai.azure.com/openai/deployments/your-deployment/chat/completions \
#      -H "api-key: your-key" \
#      -H "Content-Type: application/json" \
#      -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

### Issue: Email Not Sending

```python
# Debug
from src.email_notifier import EmailNotifier

notifier = EmailNotifier(config.email)

# Test
success = notifier.send_test_email("recipient@example.com")
if not success:
    print("Email sending failed")

# Fix:
# 1. For Gmail: Use app-specific password (not account password)
# 2. Check SMTP settings:
#    - Gmail: smtp.gmail.com:587 (TLS)
#    - Office365: smtp.office365.com:587 (TLS)
# 3. Enable SMTP if disabled in your email provider
# 4. Check firewall (port 587)
```

---

## Performance Tuning

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
import logging

def process_jobs_parallel(job_ids, max_workers=5):
    """Process multiple jobs in parallel"""
    agent = DatabricksAIAgent(AgentConfig.from_env())
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        
        for job_id, run_id in job_ids:
            future = executor.submit(
                agent.process_failed_job,
                job_id=job_id,
                run_id=run_id
            )
            futures.append(future)
        
        results = []
        for future in futures:
            try:
                result = future.result(timeout=30)
                results.append(result)
            except Exception as e:
                logging.error(f"Error: {e}")
        
        return results
```

### Caching

```python
from functools import lru_cache
from src.error_decision_engine import ErrorDecisionEngine

# Cache pattern analysis
@lru_cache(maxsize=1000)
def analyze_error_pattern(error_message):
    engine = ErrorDecisionEngine()
    return engine._analyze_error_pattern(error_message)
```

---

## Next Steps Checklist

- [ ] Complete Step 1-5 above
- [ ] Choose integration path (A, B, C, D, or E)
- [ ] Deploy and test
- [ ] Set up monitoring
- [ ] Collect feedback for model training
- [ ] Configure alerts
- [ ] Document custom patterns/actions
- [ ] Set up CI/CD pipeline
- [ ] Schedule model retraining
- [ ] Monitor costs (Azure OpenAI API calls)

---

## Support & Debugging

1. **Check logs:** `export LOG_LEVEL=DEBUG`
2. **Run tests:** `python -m pytest test_agent.py -v`
3. **Verify config:** `python -c "from src.config import AgentConfig; c = AgentConfig.from_env(); print(c)"`
4. **Test components:** See troubleshooting guide above
5. **Read docs:** See README.md, ARCHITECTURE.md

---

## Production Checklist

- [ ] Environment variables configured (no hardcoding)
- [ ] .env file added to .gitignore
- [ ] Logging configured properly
- [ ] Error handling in place
- [ ] Tests passing (pytest)
- [ ] Documentation updated
- [ ] Credentials rotated
- [ ] Rate limits configured
- [ ] Monitoring set up
- [ ] Backup plan for failures
- [ ] Disaster recovery tested
- [ ] Security review completed
