"""
Environment Variables and Configuration Checklist
"""

# ============================================================================
# REQUIRED ENVIRONMENT VARIABLES
# ============================================================================

ENVIRONMENT_TEMPLATE = """
# ============================================================================
# DATABRICKS AI AGENT - ENVIRONMENT CONFIGURATION
# ============================================================================
# Copy this file to .env and fill in your actual values
# DO NOT commit .env to version control!

# ============================================================================
# AZURE OPENAI (Required)
# ============================================================================
# Get these from Azure Portal → OpenAI Resource → Keys and Endpoints

AZURE_OPENAI_KEY=your-azure-openai-api-key-here
# Example: 1a2b3c4d5e6f7g8h9i0jk1l2m3n4o5p

AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# Example: https://my-openai-resource.openai.azure.com/

AZURE_OPENAI_DEPLOYMENT=gpt-4
# The name of your deployed model (e.g., gpt-4, gpt-3.5-turbo)

# ============================================================================
# DATABRICKS (Required)
# ============================================================================
# Get from Databricks Workspace → User Settings → Access Tokens

DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
# Example: https://abc123def456.cloud.databricks.com
# Without trailing slash!

DATABRICKS_TOKEN=dapi1a2b3c4d5e6f7g8h9i0jk1l2m3n4o5
# Your Databricks personal access token
# Keep this secret!

# ============================================================================
# EMAIL / SMTP (Required for escalations)
# ============================================================================

SMTP_SERVER=smtp.gmail.com
# Gmail: smtp.gmail.com
# Outlook: smtp-mail.outlook.com
# Corporate: ask your IT department

SENDER_EMAIL=your-email@gmail.com
# The email address sending notifications

SENDER_PASSWORD=xxxx xxxx xxxx xxxx
# For Gmail: app-specific password (16 chars with spaces)
# For others: your email password

# ============================================================================
# ERROR HANDLING (Optional - uses defaults if not set)
# ============================================================================

MAX_RETRY_ATTEMPTS=3
# How many times to retry with same parameters before escalating

RETRY_WITH_PARAMS_ATTEMPTS=2
# How many times to retry with modified parameters before escalating

# ============================================================================
# LOGGING (Optional)
# ============================================================================

LOG_LEVEL=INFO
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

LOG_FILE=/tmp/databricks_agent.log
# Where to store agent logs

# ============================================================================
# OPTIONAL FEATURES
# ============================================================================

# Slack notifications (future feature)
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Custom webhook
# CUSTOM_WEBHOOK_URL=https://your-server.com/webhook

# ============================================================================
# NOTES
# ============================================================================
# - Keep this file secret - it contains credentials
# - Add .env to .gitignore
# - Use environment-specific .env files (.env.prod, .env.dev)
# - Rotate API keys periodically
# - Never hardcode credentials in source code
"""

# ============================================================================
# CONFIGURATION CHECKLIST
# ============================================================================

CONFIGURATION_CHECKLIST = """
╔════════════════════════════════════════════════════════════════════════════╗
║         DATABRICKS AI AGENT - CONFIGURATION CHECKLIST                      ║
╚════════════════════════════════════════════════════════════════════════════╝

STEP 1: AZURE OPENAI SETUP
────────────────────────────────────────────────────────────────────────────
☐ Azure subscription active
☐ Azure OpenAI resource created
☐ OpenAI model deployed (gpt-4 recommended)
☐ API key copied to AZURE_OPENAI_KEY
☐ Endpoint URL copied to AZURE_OPENAI_ENDPOINT
☐ Deployment name set in AZURE_OPENAI_DEPLOYMENT

Verification:
  - Can you see the resource in Azure Portal?
  - Does the deployment status show "Succeeded"?
  - Can you copy the Key and Endpoint without errors?


STEP 2: DATABRICKS SETUP
────────────────────────────────────────────────────────────────────────────
☐ Databricks workspace accessible
☐ User account has token creation permissions
☐ Personal access token generated
☐ Workspace URL copied to DATABRICKS_HOST
☐ Token copied to DATABRICKS_TOKEN
☐ You have identified at least one job to monitor

Verification:
  - Can you access your Databricks workspace?
  - Does your token appear in "Active tokens" in User Settings?
  - Can you list your jobs via API? (test in examples)


STEP 3: EMAIL SETUP
────────────────────────────────────────────────────────────────────────────
☐ SMTP server confirmed
☐ Sender email address ready
☐ Authentication method determined:
  
  For Gmail:
  ☐ 2-factor authentication enabled
  ☐ App-specific password generated (myaccount.google.com/apppasswords)
  ☐ 16-character password copied to SENDER_PASSWORD
  
  For Outlook:
  ☐ Password confirmed
  ☐ Password copied to SENDER_PASSWORD
  
  For Corporate Email:
  ☐ IT provided SMTP server
  ☐ IT confirmed credentials
  ☐ Credentials copied to .env file

Verification:
  - Can you send a test email manually from this account?
  - Does the SMTP server accept connections on port 587?


STEP 4: CODE SETUP
────────────────────────────────────────────────────────────────────────────
☐ Python 3.8+ installed
☐ Project directory created/cloned
☐ requirements.txt reviewed
☐ Dependencies installed: pip install -r requirements.txt
☐ .env file created with all credentials
☐ .env file added to .gitignore
☐ .env file NOT committed to git

Verification:
  - Run: python --version (should be 3.8+)
  - Run: pip show azure-identity (should be installed)


STEP 5: CONFIGURATION FILES
────────────────────────────────────────────────────────────────────────────
☐ config/databricks_agent.yaml reviewed
☐ Retry limits configured appropriate for your jobs
☐ Check intervals set (300 seconds = 5 minutes)
☐ Logging level configured (INFO for production)
☐ Escalation email list prepared

Sample configuration locations:
  - Max retries: error_handling.max_retry_attempts
  - Check interval: monitoring.check_interval_seconds
  - Escalation emails: Configure in code or environment


STEP 6: SECURITY VERIFICATION
────────────────────────────────────────────────────────────────────────────
☐ .env file NOT in git repository
☐ No credentials in source code
☐ API keys set with minimal required permissions
☐ Databricks token regenerated if previously exposed
☐ .gitignore includes .env
☐ .env file permissions set to 600 (if on Unix)

Security best practices:
  - Rotate keys/tokens quarterly
  - Use environment variables only
  - Never log sensitive data
  - Review escalation email recipients


STEP 7: TESTING
────────────────────────────────────────────────────────────────────────────
☐ Configuration validated
  Command: python -c "from setup_guide import test_configuration; \
                      test_configuration()"

☐ Connections tested
  Command: python -c "from setup_guide import test_all_connections; \
                      test_all_connections()"

☐ Email connection verified
  Command: python -c "from src.email_notifier import EmailNotifier; \
                      n = EmailNotifier(); print(n.test_connection())"

☐ Databricks jobs visible
  Command: Check Databricks UI - Can you see your jobs?

☐ Azure OpenAI accessible
  Command: python examples/databricks_agent_example.py
           (Should complete without authentication errors)

☐ All tests passing
  Command: pytest tests/test_databricks_agent.py -v


STEP 8: INITIAL MONITORING RUN
────────────────────────────────────────────────────────────────────────────
☐ Run basic monitoring example
  Command: python examples/databricks_agent_example.py

☐ Check console output for:
  ✓ No authentication errors
  ✓ Able to connect to Databricks
  ✓ Found failed jobs (if any)
  ✓ Able to connect to Azure OpenAI
  ✓ Made intelligent decisions

☐ Review logs at /tmp/databricks_agent.log


STEP 9: DATABRICKS DEPLOYMENT
────────────────────────────────────────────────────────────────────────────
☐ Upload notebooks/databricks_agent_runner.py to Databricks
☐ Create new job in Databricks:
  ☐ Name: "AI Agent - Job Monitoring"
  ☐ Type: Notebook
  ☐ Notebook path: /Repos/.../databricks_agent_runner
  ☐ Cluster: Create new or use existing
  ☐ Schedule: Every 30 minutes (adjust as needed)
  ☐ Timeout: 15 minutes
  ☐ Retries: 1

☐ Run job manually to test
☐ Check job run logs for errors
☐ Verify escalation emails being sent


STEP 10: FINE-TUNING SETUP (Optional but Recommended)
────────────────────────────────────────────────────────────────────────────
☐ Collect 50+ historical job failure decisions
☐ Store in data/run_history.json
☐ Prepare training data
  Command: python -c "from setup_guide import prepare_fine_tuning_data; \
                      prepare_fine_tuning_data()"

☐ Start fine-tuning job
  Command: python -c "from setup_guide import start_fine_tuning; \
                      start_fine_tuning()"

☐ Monitor fine-tuning status
☐ Update agent to use fine-tuned model


STEP 11: MONITORING & MAINTENANCE
────────────────────────────────────────────────────────────────────────────
☐ Establish monitoring schedule:
  - Daily: Check Databricks job run logs
  - Weekly: Review escalation emails
  - Monthly: Analyze decision effectiveness
  - Quarterly: Rotate API keys

☐ Set up monitoring dashboard:
  - Query Delta table for decision statistics
  - Create alerts for repeated failures
  - Track model performance

☐ Documentation:
  ☐ Team trained on alert emails
  ☐ Escalation procedures documented
  ☐ Contact info for model fine-tuning


═══════════════════════════════════════════════════════════════════════════════

QUICK VERIFICATION COMMANDS
──────────────────────────────────────────────────────────────────────────────

# Test all components
python -c "from setup_guide import test_all_connections; test_all_connections()"

# Test email
python -c "from src.email_notifier import EmailNotifier; \\
           e = EmailNotifier(); print('Email OK' if e.test_connection() else 'Email FAIL')"

# Test Azure OpenAI
python -c "from src.azure_openai_client import AzureOpenAIClient; \\
           a = AzureOpenAIClient(); print('Azure OpenAI OK')"

# Test Databricks
python -c "from src.databricks_connector import DatabricksConnector; \\
           d = DatabricksConnector(); print('Databricks OK')"

# Run monitoring
python examples/databricks_agent_example.py

# Run tests
pytest tests/test_databricks_agent.py -v


═══════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING QUICK REFERENCE
──────────────────────────────────────────────────────────────────────────────

Problem: "No module named 'azure_identity'"
Solution: pip install azure-identity azure-ai-openai

Problem: "Invalid API key"
Solution: Check AZURE_OPENAI_KEY is correct, not expired

Problem: "Invalid token"
Solution: Regenerate DATABRICKS_TOKEN in workspace settings

Problem: "SMTP auth failed"
Solution: For Gmail, use app-specific password, not account password

Problem: "No failed jobs found"
Solution: Verify job IDs are correct, check if jobs actually failed

Problem: "Email not sending"
Solution: Run email_notifier.test_connection() to debug


═══════════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(ENVIRONMENT_TEMPLATE)
    print("\n" + "="*80 + "\n")
    print(CONFIGURATION_CHECKLIST)
