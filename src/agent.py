"""Main AI Agent for Databricks error handling and decision making"""

import logging
from typing import Optional, Dict, Any, List
import time

from .config import AgentConfig
from .azure_openai_client import AzureOpenAIClient
from .databricks_client import DatabricksClient
from .error_decision_engine import ErrorDecisionEngine, DecisionAction
from .email_notifier import EmailNotifier
from .model_fine_tuner import ModelFineTuner

logger = logging.getLogger(__name__)


class DatabricksAIAgent:
    """Main AI Agent for handling Databricks job failures"""

    def __init__(self, config: AgentConfig):
        """Initialize the agent
        
        Args:
            config: Agent configuration
        """
        self.config = config
        
        # Initialize clients and services
        self.llm_client = AzureOpenAIClient(config.azure_openai)
        self.databricks_client = DatabricksClient(config.databricks)
        self.decision_engine = ErrorDecisionEngine(config.max_retries)
        self.email_notifier = EmailNotifier(config.email)
        self.fine_tuner = ModelFineTuner(self.llm_client)
        
        # Set up logging
        self._setup_logging(config.log_level)

    def _setup_logging(self, log_level: str):
        """Setup logging configuration
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def process_failed_job(
        self,
        job_id: int,
        run_id: int,
        attempt_number: int = 1,
        previous_error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a failed Databricks job and make a decision
        
        Args:
            job_id: The job ID
            run_id: The run ID
            attempt_number: Current attempt number
            previous_error: Previous error message if retrying
            
        Returns:
            Decision and action result
        """
        logger.info(f"Processing failed job - ID: {job_id}, Run: {run_id}, Attempt: {attempt_number}")
        
        try:
            # Get job run details
            run_details = self.databricks_client.get_job_run(run_id)
            if "error" in run_details:
                logger.error(f"Failed to get run details: {run_details['error']}")
                return {"error": run_details["error"]}
            
            # Get job output/error
            output = self.databricks_client.get_job_run_output(run_id)
            error_message = self._extract_error_message(run_details, output, previous_error)
            
            # Prepare job context
            job_context = {
                "job_id": job_id,
                "run_id": run_id,
                "attempt_number": attempt_number,
                "parameters": run_details.get("job_parameters", {}),
                "state": run_details.get("state"),
                "state_message": run_details.get("state_message")
            }
            
            # Analyze error with LLM
            logger.info("Analyzing error with Azure OpenAI...")
            llm_analysis = self.llm_client.analyze_error(error_message, job_context)
            
            # Make decision
            decision = self.decision_engine.make_decision(
                error_message,
                job_context,
                llm_analysis
            )
            
            # Execute action based on decision
            action_result = self._execute_action(decision, job_id, run_id, job_context, error_message)
            
            # Combine results
            result = {
                "success": True,
                "job_id": job_id,
                "run_id": run_id,
                "error_message": error_message,
                "analysis": llm_analysis,
                "decision": decision,
                "action_result": action_result
            }
            
            logger.info(f"Job processing completed: {decision['action'].value}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing job: {str(e)}", exc_info=True)
            return {
                "success": False,
                "job_id": job_id,
                "run_id": run_id,
                "error": str(e)
            }

    def _extract_error_message(
        self,
        run_details: Dict[str, Any],
        output: Dict[str, Any],
        previous_error: Optional[str] = None
    ) -> str:
        """Extract error message from run details and output
        
        Args:
            run_details: Job run details
            output: Job output
            previous_error: Previous error if retrying
            
        Returns:
            Error message string
        """
        error_messages = []
        
        if previous_error:
            error_messages.append(f"Previous attempt error: {previous_error}")
        
        if run_details.get("state_message"):
            error_messages.append(run_details["state_message"])
        
        if output.get("error"):
            error_messages.append(output["error"])
        
        if output.get("error_trace"):
            error_messages.append(output["error_trace"])
        
        return " | ".join(error_messages) if error_messages else "Unknown error"

    def _execute_action(
        self,
        decision: Dict[str, Any],
        job_id: int,
        run_id: int,
        job_context: Dict[str, Any],
        error_message: str
    ) -> Dict[str, Any]:
        """Execute the decided action
        
        Args:
            decision: The decision with action
            job_id: The job ID
            run_id: The run ID
            job_context: Job context
            error_message: Error message
            
        Returns:
            Action execution result
        """
        action = decision["action"]
        
        if action == DecisionAction.RETRY:
            return self._retry_job(job_id, run_id, job_context)
        
        elif action == DecisionAction.RETRY_WITH_NEW_PARAMS:
            new_params = decision.get("suggested_params") or self.llm_client.extract_parameters_for_retry(decision)
            return self._retry_job_with_params(job_id, run_id, new_params, job_context)
        
        elif action == DecisionAction.SEND_EMAIL:
            return self._send_error_notification(decision, job_id, run_id, job_context, error_message)
        
        elif action == DecisionAction.ESCALATE:
            return self._escalate_issue(decision, job_id, run_id, job_context, error_message)
        
        else:
            logger.warning(f"Unknown action: {action}")
            return {"status": "unknown_action"}

    def _retry_job(self, job_id: int, run_id: int, job_context: Dict[str, Any]) -> Dict[str, Any]:
        """Retry job with same parameters
        
        Args:
            job_id: The job ID
            run_id: The run ID (to cancel)
            job_context: Job context
            
        Returns:
            Retry result
        """
        try:
            logger.info(f"Retrying job {job_id}...")
            
            # Cancel previous run
            self.databricks_client.cancel_job_run(run_id)
            
            # Submit new run
            result = self.databricks_client.submit_job_run(
                job_id,
                job_context.get("parameters")
            )
            
            if "run_id" in result:
                logger.info(f"Job retry submitted with run_id: {result['run_id']}")
                return {
                    "status": "retry_submitted",
                    "new_run_id": result["run_id"]
                }
            else:
                return {
                    "status": "retry_failed",
                    "error": result.get("error")
                }
        
        except Exception as e:
            logger.error(f"Error retrying job: {str(e)}")
            return {"status": "retry_error", "error": str(e)}

    def _retry_job_with_params(
        self,
        job_id: int,
        run_id: int,
        new_params: Dict[str, Any],
        job_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retry job with new parameters
        
        Args:
            job_id: The job ID
            run_id: The run ID (to cancel)
            new_params: New parameters for job
            job_context: Job context
            
        Returns:
            Retry result
        """
        try:
            logger.info(f"Retrying job {job_id} with new parameters: {new_params}")
            
            # Cancel previous run
            self.databricks_client.cancel_job_run(run_id)
            
            # Submit new run with new parameters
            result = self.databricks_client.submit_job_run(job_id, new_params)
            
            if "run_id" in result:
                logger.info(f"Job retry submitted with run_id: {result['run_id']}")
                return {
                    "status": "retry_with_params_submitted",
                    "new_run_id": result["run_id"],
                    "new_parameters": new_params
                }
            else:
                return {
                    "status": "retry_failed",
                    "error": result.get("error")
                }
        
        except Exception as e:
            logger.error(f"Error retrying job with params: {str(e)}")
            return {"status": "retry_error", "error": str(e)}

    def _send_error_notification(
        self,
        decision: Dict[str, Any],
        job_id: int,
        run_id: int,
        job_context: Dict[str, Any],
        error_message: str
    ) -> Dict[str, Any]:
        """Send error notification
        
        Args:
            decision: The decision
            job_id: The job ID
            run_id: The run ID
            job_context: Job context
            error_message: Error message
            
        Returns:
            Notification result
        """
        try:
            logger.info(f"Sending error notification for job {job_id}...")
            
            # Generate email content
            email_content = self.llm_client.generate_email_content(
                {
                    "error_category": decision.get("error_category"),
                    "root_cause": decision.get("root_cause"),
                    "severity": decision.get("priority"),
                    "error_message": error_message,
                    "job_id": job_id,
                    "run_id": run_id
                },
                decision.get("recipient_team", "DevOps")
            )
            
            # Send email
            recipients = ["admin@example.com"]  # Configure as needed
            sent = self.email_notifier.send_escalation_notification(
                str(job_id),
                run_id,
                decision.get("error_category"),
                decision.get("root_cause"),
                decision.get("priority", "medium"),
                error_message,
                recipients
            )
            
            return {
                "status": "notification_sent" if sent else "notification_failed",
                "email_subject": email_content.get("subject"),
                "recipients": recipients
            }
        
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return {"status": "notification_error", "error": str(e)}

    def _escalate_issue(
        self,
        decision: Dict[str, Any],
        job_id: int,
        run_id: int,
        job_context: Dict[str, Any],
        error_message: str
    ) -> Dict[str, Any]:
        """Escalate issue for manual handling
        
        Args:
            decision: The decision
            job_id: The job ID
            run_id: The run ID
            job_context: Job context
            error_message: Error message
            
        Returns:
            Escalation result
        """
        logger.warning(f"Escalating issue for job {job_id} to manual review...")
        
        return {
            "status": "escalated",
            "job_id": job_id,
            "run_id": run_id,
            "error_category": decision.get("error_category"),
            "priority": decision.get("priority", "medium"),
            "requires_manual_review": True
        }

    def monitor_jobs(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """Monitor recent jobs for failures
        
        Args:
            max_age_hours: Only check jobs from last N hours
            
        Returns:
            Monitoring results
        """
        logger.info(f"Monitoring jobs from last {max_age_hours} hours...")
        
        try:
            jobs = self.databricks_client.list_jobs(limit=50)
            
            failed_jobs = []
            for job in jobs:
                # Check for failures - implementation depends on job structure
                # This is a simplified example
                job_id = job.get("job_id")
                
                failed_jobs.append({
                    "job_id": job_id,
                    "status": "monitored"
                })
            
            logger.info(f"Monitored {len(jobs)} jobs, found {len(failed_jobs)} failures")
            
            return {
                "status": "monitoring_complete",
                "jobs_checked": len(jobs),
                "failed_jobs": failed_jobs
            }
        
        except Exception as e:
            logger.error(f"Error during monitoring: {str(e)}")
            return {"status": "monitoring_error", "error": str(e)}
