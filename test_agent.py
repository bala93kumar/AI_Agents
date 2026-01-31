"""Unit tests for the AI Agent components"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

from src.config import AgentConfig, AzureOpenAIConfig, DatabricksConfig, EmailConfig
from src.error_decision_engine import ErrorDecisionEngine, DecisionAction
from src.model_fine_tuner import ModelFineTuner


class TestErrorDecisionEngine(unittest.TestCase):
    """Tests for error decision engine"""
    
    def setUp(self):
        self.engine = ErrorDecisionEngine(max_retries=3)
    
    def test_timeout_error_should_retry(self):
        """Test that timeout errors recommend retry"""
        decision = self.engine.make_decision(
            error_message="Job execution timed out after 3600 seconds",
            job_context={"job_id": 123, "attempt_number": 1}
        )
        
        self.assertEqual(decision["action"], DecisionAction.RETRY)
        self.assertEqual(decision["error_category"], "timeout")
    
    def test_permission_error_should_notify(self):
        """Test that permission errors recommend notification"""
        decision = self.engine.make_decision(
            error_message="Permission denied: Access to file denied",
            job_context={"job_id": 123, "attempt_number": 1}
        )
        
        self.assertEqual(decision["action"], DecisionAction.SEND_EMAIL)
        self.assertEqual(decision["error_category"], "permission")
    
    def test_resource_error_should_retry_with_params(self):
        """Test that resource errors recommend retry with params"""
        decision = self.engine.make_decision(
            error_message="Out of memory error",
            job_context={"job_id": 123, "attempt_number": 1}
        )
        
        self.assertEqual(decision["action"], DecisionAction.RETRY_WITH_NEW_PARAMS)
        self.assertEqual(decision["error_category"], "resource")
    
    def test_max_retries_exceeded(self):
        """Test that retry is escalated when max retries reached"""
        decision = self.engine.make_decision(
            error_message="Job execution timed out",
            job_context={"job_id": 123, "attempt_number": 3}
        )
        
        # Should be escalated to email even though it's a timeout
        self.assertEqual(decision["action"], DecisionAction.SEND_EMAIL)
    
    def test_llm_analysis_integration(self):
        """Test integration with LLM analysis"""
        llm_analysis = {
            "recommendation": "RETRY_WITH_NEW_PARAMS",
            "error_category": "resource",
            "root_cause": "Insufficient memory allocation",
            "reason": "Increasing memory will likely fix the issue",
            "severity": "high",
            "suggested_params": {"memory_gb": 16}
        }
        
        decision = self.engine.make_decision(
            error_message="Out of memory",
            job_context={"job_id": 123, "attempt_number": 1},
            llm_analysis=llm_analysis
        )
        
        self.assertEqual(decision["action"], DecisionAction.RETRY_WITH_NEW_PARAMS)
        self.assertEqual(decision["suggested_params"], {"memory_gb": 16})


class TestModelFineTuner(unittest.TestCase):
    """Tests for model fine-tuning utilities"""
    
    def setUp(self):
        self.mock_azure_client = Mock()
        self.tuner = ModelFineTuner(self.mock_azure_client)
    
    def test_performance_calculation(self):
        """Test model performance analysis"""
        feedback_records = [
            {"useful": True},
            {"useful": True},
            {"useful": False},
            {"useful": True},
        ]
        
        performance = self.tuner.analyze_model_performance(feedback_records)
        
        self.assertEqual(performance["total_decisions"], 4)
        self.assertEqual(performance["correct_decisions"], 3)
        self.assertEqual(performance["accuracy_percentage"], 75.0)
    
    def test_improvement_recommendations(self):
        """Test improvement recommendations"""
        performance = {
            "accuracy_percentage": 65.0,
            "decision_breakdown": {
                "retry": {"accuracy": 50},
                "send_email": {"accuracy": 80}
            }
        }
        
        recommendations = self.tuner.generate_improvement_recommendations(performance)
        
        self.assertGreater(len(recommendations), 0)
        # Should recommend training improvement
        self.assertTrue(any("retraining" in r.lower() or "accuracy" in r.lower() for r in recommendations))


class TestConfig(unittest.TestCase):
    """Tests for configuration loading"""
    
    @patch.dict('os.environ', {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'DATABRICKS_WORKSPACE_URL': 'https://test.databricks.com',
        'DATABRICKS_PAT_TOKEN': 'test-token'
    })
    def test_config_from_env(self):
        """Test loading config from environment"""
        config = AgentConfig.from_env()
        
        self.assertEqual(config.azure_openai.api_key, 'test-key')
        self.assertEqual(config.databricks.pat_token, 'test-token')


if __name__ == "__main__":
    unittest.main()
