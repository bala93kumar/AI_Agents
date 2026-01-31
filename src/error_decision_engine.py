"""Decision engine for handling job errors"""

import logging
import json
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DecisionAction(Enum):
    """Actions the decision engine can recommend"""
    RETRY = "retry"
    RETRY_WITH_NEW_PARAMS = "retry_with_new_params"
    SEND_EMAIL = "send_email"
    ESCALATE = "escalate"
    IGNORE = "ignore"


class ErrorDecisionEngine:
    """Engine for deciding how to handle job failures"""

    def __init__(self, max_retries: int = 3):
        """Initialize decision engine
        
        Args:
            max_retries: Maximum number of retry attempts
        """
        self.max_retries = max_retries
        self.error_patterns = {
            "timeout": {
                "keywords": ["timeout", "timed out", "deadline exceeded"],
                "action": DecisionAction.RETRY,
                "priority": "medium"
            },
            "resource": {
                "keywords": ["out of memory", "disk space", "resource exhausted", "insufficient resources"],
                "action": DecisionAction.RETRY_WITH_NEW_PARAMS,
                "priority": "high"
            },
            "permission": {
                "keywords": ["permission denied", "access denied", "unauthorized", "forbidden"],
                "action": DecisionAction.SEND_EMAIL,
                "priority": "critical"
            },
            "syntax": {
                "keywords": ["syntax error", "invalid", "parse error", "compilation failed"],
                "action": DecisionAction.SEND_EMAIL,
                "priority": "critical"
            },
            "network": {
                "keywords": ["connection refused", "network error", "timeout", "connection reset"],
                "action": DecisionAction.RETRY,
                "priority": "high"
            },
            "data": {
                "keywords": ["no such file", "file not found", "not found", "does not exist"],
                "action": DecisionAction.SEND_EMAIL,
                "priority": "critical"
            }
        }

    def make_decision(
        self,
        error_message: str,
        job_context: Dict[str, Any],
        llm_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a decision based on error and context
        
        Args:
            error_message: The error message
            job_context: Context about the job
            llm_analysis: Optional analysis from LLM
            
        Returns:
            Decision with action and parameters
        """
        # Start with pattern-based analysis
        pattern_result = self._analyze_error_pattern(error_message)
        
        # Combine with LLM analysis if available
        if llm_analysis:
            decision = self._combine_analyses(pattern_result, llm_analysis, job_context)
        else:
            decision = self._build_decision(pattern_result, job_context)
        
        # Check retry limits
        attempt_number = job_context.get("attempt_number", 1)
        if attempt_number >= self.max_retries and decision["action"] in [
            DecisionAction.RETRY,
            DecisionAction.RETRY_WITH_NEW_PARAMS
        ]:
            logger.warning(f"Max retries ({self.max_retries}) reached, escalating to email")
            decision["action"] = DecisionAction.SEND_EMAIL
            decision["reason"] = f"Max retries ({self.max_retries}) exceeded"
        
        decision["timestamp"] = datetime.utcnow().isoformat()
        decision["attempt_number"] = attempt_number
        
        logger.info(f"Decision made: {decision['action'].value}")
        return decision

    def _analyze_error_pattern(self, error_message: str) -> Dict[str, Any]:
        """Analyze error message against known patterns
        
        Args:
            error_message: The error message
            
        Returns:
            Analysis result
        """
        error_lower = error_message.lower()
        
        for error_type, pattern in self.error_patterns.items():
            for keyword in pattern["keywords"]:
                if keyword in error_lower:
                    return {
                        "error_type": error_type,
                        "action": pattern["action"],
                        "priority": pattern["priority"],
                        "matched_keyword": keyword
                    }
        
        # Default for unknown errors
        return {
            "error_type": "unknown",
            "action": DecisionAction.SEND_EMAIL,
            "priority": "medium",
            "matched_keyword": None
        }

    def _combine_analyses(
        self,
        pattern_result: Dict[str, Any],
        llm_analysis: Dict[str, Any],
        job_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine pattern-based and LLM analysis
        
        Args:
            pattern_result: Result from pattern analysis
            llm_analysis: Result from LLM analysis
            job_context: Job context
            
        Returns:
            Combined decision
        """
        # LLM analysis takes precedence if it has strong confidence
        if llm_analysis.get("recommendation"):
            try:
                action = DecisionAction[llm_analysis["recommendation"].upper()]
            except (KeyError, ValueError):
                action = pattern_result["action"]
        else:
            action = pattern_result["action"]
        
        decision = {
            "action": action,
            "error_category": llm_analysis.get("error_category", pattern_result["error_type"]),
            "root_cause": llm_analysis.get("root_cause", "Unknown"),
            "reason": llm_analysis.get("reason", pattern_result["matched_keyword"] or "Pattern matched"),
            "priority": llm_analysis.get("severity", pattern_result["priority"]).lower(),
            "suggested_params": llm_analysis.get("suggested_params"),
            "recipient_team": llm_analysis.get("recipient_team", "DevOps"),
        }
        
        return decision

    def _build_decision(self, pattern_result: Dict[str, Any], job_context: Dict[str, Any]) -> Dict[str, Any]:
        """Build decision from pattern analysis alone
        
        Args:
            pattern_result: Result from pattern analysis
            job_context: Job context
            
        Returns:
            Decision
        """
        return {
            "action": pattern_result["action"],
            "error_category": pattern_result["error_type"],
            "root_cause": pattern_result.get("matched_keyword", "Unknown error pattern"),
            "reason": f"Matched pattern: {pattern_result['matched_keyword']}",
            "priority": pattern_result["priority"],
            "suggested_params": None,
            "recipient_team": "DevOps",
        }

    def should_retry_immediately(self, decision: Dict[str, Any]) -> bool:
        """Check if we should retry immediately
        
        Args:
            decision: The decision
            
        Returns:
            True if should retry immediately
        """
        return decision["action"] in [
            DecisionAction.RETRY,
            DecisionAction.RETRY_WITH_NEW_PARAMS
        ]

    def should_notify(self, decision: Dict[str, Any]) -> bool:
        """Check if we should send notification
        
        Args:
            decision: The decision
            
        Returns:
            True if should send notification
        """
        return decision["action"] in [
            DecisionAction.SEND_EMAIL,
            DecisionAction.ESCALATE
        ]
