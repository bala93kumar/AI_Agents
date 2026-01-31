"""Azure OpenAI client for LLM interactions"""

import json
import logging
from typing import Optional, Dict, Any
from openai import AzureOpenAI

from .config import AzureOpenAIConfig

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """Client for interacting with Azure OpenAI models"""

    def __init__(self, config: AzureOpenAIConfig):
        """Initialize Azure OpenAI client
        
        Args:
            config: Azure OpenAI configuration
        """
        self.config = config
        self.client = AzureOpenAI(
            api_key=config.api_key,
            api_version=config.api_version,
            azure_endpoint=config.azure_endpoint,
        )

    def analyze_error(self, error_message: str, job_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze error using LLM and suggest actions
        
        Args:
            error_message: The error message from failed job
            job_context: Context about the job (parameters, attempts, etc.)
            
        Returns:
            Dictionary with analysis and recommended action
        """
        prompt = self._build_error_analysis_prompt(error_message, job_context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert DevOps engineer analyzing job failures. Provide structured analysis in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            logger.info(f"Error analysis completed: {analysis.get('recommendation')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error during LLM analysis: {str(e)}")
            return {
                "error": str(e),
                "recommendation": "send_email",
                "reason": "LLM analysis failed, manual review needed"
            }

    def _build_error_analysis_prompt(self, error_message: str, job_context: Dict[str, Any]) -> str:
        """Build prompt for error analysis"""
        return f"""
Analyze this job failure and provide a recommended action:

Error Message:
{error_message}

Job Context:
- Job ID: {job_context.get('job_id', 'unknown')}
- Attempt Number: {job_context.get('attempt_number', 1)}
- Previous Attempts: {job_context.get('previous_attempts', [])}
- Job Parameters: {json.dumps(job_context.get('parameters', {}), indent=2)}

Respond in JSON format with these fields:
{{
    "error_category": "string - categorize the error (timeout, resource, syntax, permission, etc.)",
    "root_cause": "string - brief explanation of the root cause",
    "recommendation": "string - one of: retry, retry_with_new_params, send_email",
    "reason": "string - explanation for the recommendation",
    "suggested_params": "object - if retry_with_new_params, suggest new parameters",
    "recipient_team": "string - if send_email, which team should be notified",
    "severity": "string - critical, high, medium, or low"
}}
"""

    def extract_parameters_for_retry(self, error_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and validate parameters for retry
        
        Args:
            error_analysis: Output from analyze_error
            
        Returns:
            New parameters for retry
        """
        suggested_params = error_analysis.get("suggested_params", {})
        if isinstance(suggested_params, str):
            try:
                suggested_params = json.loads(suggested_params)
            except json.JSONDecodeError:
                logger.warning("Could not parse suggested parameters")
                suggested_params = {}
        
        return suggested_params

    def generate_email_content(self, error_info: Dict[str, Any], recipient_team: str) -> Dict[str, str]:
        """Generate email content for error notification
        
        Args:
            error_info: Information about the error
            recipient_team: Team to notify
            
        Returns:
            Dictionary with subject and body
        """
        prompt = f"""
Generate a professional email for this job failure:

Error Category: {error_info.get('error_category')}
Root Cause: {error_info.get('root_cause')}
Severity: {error_info.get('severity')}
Error Message: {error_info.get('error_message')}
Job ID: {error_info.get('job_id')}

Create email in JSON format with 'subject' and 'body' fields. Keep it concise and actionable.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional technical writer. Generate concise, actionable emails."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            email_content = json.loads(response.choices[0].message.content)
            return email_content
            
        except Exception as e:
            logger.error(f"Error generating email content: {str(e)}")
            return {
                "subject": f"Job Failure Alert - Immediate Action Required",
                "body": f"Job failed with error. Please review and take action.\n\nError: {error_info.get('error_message', 'Unknown')}"
            }
