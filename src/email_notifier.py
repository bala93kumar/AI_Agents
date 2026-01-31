"""Email notification service"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional

from .config import EmailConfig

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Service for sending email notifications"""

    def __init__(self, config: EmailConfig):
        """Initialize email notifier
        
        Args:
            config: Email configuration
        """
        self.config = config

    def send_error_notification(
        self,
        subject: str,
        body: str,
        recipients: List[str],
        error_details: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Send error notification email
        
        Args:
            subject: Email subject
            body: Email body
            recipients: List of recipient email addresses
            error_details: Optional error details to include
            attachments: Optional list of file paths to attach
            
        Returns:
            True if email sent successfully
        """
        if not self.config.enabled:
            logger.warning("Email notifications are disabled")
            return False

        if not recipients:
            logger.warning("No recipients specified for email notification")
            return False

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.config.sender_email
            message["To"] = ", ".join(recipients)

            # Add body
            body_with_details = body
            if error_details:
                body_with_details += self._format_error_details(error_details)

            message.attach(MIMEText(body_with_details, "plain"))

            # Connect and send
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.sender_email, self.config.sender_password)
                server.send_message(message)

            logger.info(f"Email sent to {', '.join(recipients)}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check sender email and password.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

    def send_retry_notification(
        self,
        job_id: str,
        run_id: int,
        attempt_number: int,
        error_message: str,
        recipients: Optional[List[str]] = None
    ) -> bool:
        """Send notification about job retry
        
        Args:
            job_id: The job ID
            run_id: The run ID
            attempt_number: Current attempt number
            error_message: Error message
            recipients: Optional recipients, defaults to admin team
            
        Returns:
            True if sent successfully
        """
        if recipients is None:
            recipients = ["admin@example.com"]

        subject = f"Job Retry Initiated - Job ID: {job_id}, Attempt: {attempt_number}"
        body = f"""
Job Retry Notification

Job ID: {job_id}
Run ID: {run_id}
Attempt Number: {attempt_number}
Status: Retrying

Previous Error:
{error_message}

The system has automatically initiated a retry based on error analysis.

---
Automated by AI Agent
"""

        return self.send_error_notification(subject, body, recipients)

    def send_escalation_notification(
        self,
        job_id: str,
        run_id: int,
        error_category: str,
        root_cause: str,
        priority: str,
        error_message: str,
        recipients: Optional[List[str]] = None
    ) -> bool:
        """Send escalation notification
        
        Args:
            job_id: The job ID
            run_id: The run ID
            error_category: Category of error
            root_cause: Root cause analysis
            priority: Priority level
            error_message: Full error message
            recipients: Optional recipients
            
        Returns:
            True if sent successfully
        """
        if recipients is None:
            recipients = ["devops@example.com"]

        subject = f"[{priority.upper()}] Job Failed - Escalation Required - Job ID: {job_id}"
        
        body = f"""
Job Failure Escalation

Priority: {priority}
Job ID: {job_id}
Run ID: {run_id}

Error Category: {error_category}
Root Cause: {root_cause}

Error Details:
{error_message}

The system has exhausted retry attempts and escalation is required for manual intervention.

Please take appropriate action to resolve this issue.

---
Automated by AI Agent
"""

        error_details = {
            "error_category": error_category,
            "root_cause": root_cause,
            "priority": priority,
            "error_message": error_message
        }

        return self.send_error_notification(subject, body, recipients, error_details)

    def _format_error_details(self, error_details: Dict[str, Any]) -> str:
        """Format error details for email body
        
        Args:
            error_details: Error details dictionary
            
        Returns:
            Formatted string
        """
        formatted = "\n\nDetailed Error Information:\n"
        formatted += "-" * 40 + "\n"
        
        for key, value in error_details.items():
            formatted += f"{key.replace('_', ' ').title()}: {value}\n"
        
        return formatted

    def send_test_email(self, recipient: str) -> bool:
        """Send a test email
        
        Args:
            recipient: Recipient email address
            
        Returns:
            True if successful
        """
        subject = "Test Email from AI Agent"
        body = "This is a test email to verify email notification configuration."
        return self.send_error_notification(subject, body, [recipient])
