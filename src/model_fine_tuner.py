"""Model fine-tuning utilities for Azure OpenAI"""

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelFineTuner:
    """Utilities for fine-tuning Azure OpenAI models"""

    def __init__(self, azure_client):
        """Initialize fine-tuner
        
        Args:
            azure_client: AzureOpenAIClient instance
        """
        self.azure_client = azure_client

    def prepare_training_data(
        self,
        error_samples: List[Dict[str, Any]],
        output_file: str
    ) -> bool:
        """Prepare training data for fine-tuning
        
        Args:
            error_samples: List of error samples with decisions
            output_file: Path to save training data
            
        Returns:
            True if successful
        """
        try:
            training_data = []
            
            for sample in error_samples:
                training_example = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert DevOps engineer analyzing job failures."
                        },
                        {
                            "role": "user",
                            "content": f"Analyze this error: {sample.get('error_message')}\n\nContext: {json.dumps(sample.get('context', {}))}"
                        },
                        {
                            "role": "assistant",
                            "content": json.dumps({
                                "recommendation": sample.get("decision"),
                                "error_category": sample.get("error_category"),
                                "root_cause": sample.get("root_cause"),
                                "reason": sample.get("reason")
                            })
                        }
                    ]
                }
                training_data.append(training_example)
            
            # Save to JSONL format
            with open(output_file, "w") as f:
                for example in training_data:
                    f.write(json.dumps(example) + "\n")
            
            logger.info(f"Training data prepared: {len(training_data)} examples saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            return False

    def collect_feedback(
        self,
        decision_id: str,
        original_decision: str,
        actual_outcome: str,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Collect feedback on model decisions for continuous improvement
        
        Args:
            decision_id: Unique ID of the decision
            original_decision: The decision made by the model
            actual_outcome: What actually happened
            feedback: Optional user feedback
            
        Returns:
            Feedback record
        """
        feedback_record = {
            "decision_id": decision_id,
            "timestamp": datetime.utcnow().isoformat(),
            "original_decision": original_decision,
            "actual_outcome": actual_outcome,
            "feedback": feedback,
            "useful": original_decision == actual_outcome
        }
        
        logger.info(f"Feedback collected for decision {decision_id}: useful={feedback_record['useful']}")
        return feedback_record

    def analyze_model_performance(self, feedback_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze model performance based on collected feedback
        
        Args:
            feedback_records: List of feedback records
            
        Returns:
            Performance metrics
        """
        if not feedback_records:
            return {"error": "No feedback records provided"}
        
        total = len(feedback_records)
        useful = sum(1 for r in feedback_records if r.get("useful"))
        accuracy = (useful / total * 100) if total > 0 else 0
        
        # Group by decision type
        decision_stats = {}
        for record in feedback_records:
            decision = record.get("original_decision")
            if decision not in decision_stats:
                decision_stats[decision] = {"total": 0, "correct": 0}
            
            decision_stats[decision]["total"] += 1
            if record.get("useful"):
                decision_stats[decision]["correct"] += 1
        
        performance = {
            "total_decisions": total,
            "correct_decisions": useful,
            "accuracy_percentage": round(accuracy, 2),
            "decision_breakdown": {}
        }
        
        for decision, stats in decision_stats.items():
            accuracy_for_decision = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            performance["decision_breakdown"][decision] = {
                "total": stats["total"],
                "correct": stats["correct"],
                "accuracy": round(accuracy_for_decision, 2)
            }
        
        logger.info(f"Model performance analyzed: {accuracy}% accuracy")
        return performance

    def generate_improvement_recommendations(
        self,
        performance_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for model improvement
        
        Args:
            performance_metrics: Performance metrics from analyze_model_performance
            
        Returns:
            List of recommendations
        """
        recommendations = []
        accuracy = performance_metrics.get("accuracy_percentage", 0)
        
        if accuracy < 70:
            recommendations.append(
                "Model accuracy is below 70%. Consider retraining with more recent data or adjusting error classification rules."
            )
        
        decision_breakdown = performance_metrics.get("decision_breakdown", {})
        for decision, stats in decision_breakdown.items():
            if stats.get("accuracy", 0) < 60:
                recommendations.append(
                    f"Decision '{decision}' has low accuracy ({stats['accuracy']}%). Review training data for this decision type."
                )
        
        if accuracy > 85:
            recommendations.append(
                "Model is performing well. Continue collecting feedback to maintain performance."
            )
        
        return recommendations
