"""Databricks API client using PAT tokens"""

import logging
import json
from typing import Optional, Dict, Any, List
import requests
from requests.auth import HTTPBasicAuth

from .config import DatabricksConfig

logger = logging.getLogger(__name__)


class DatabricksClient:
    """Client for interacting with Databricks API using PAT tokens"""

    def __init__(self, config: DatabricksConfig):
        """Initialize Databricks client
        
        Args:
            config: Databricks configuration with PAT token
        """
        self.config = config
        self.base_url = f"{config.workspace_url}/api/2.1"
        # PAT token is used directly in headers
        self.headers = {
            "Authorization": f"Bearer {config.pat_token}",
            "Content-Type": "application/json"
        }

    def get_job_run(self, run_id: int) -> Dict[str, Any]:
        """Get details of a job run
        
        Args:
            run_id: The job run ID
            
        Returns:
            Job run details
        """
        try:
            response = requests.get(
                f"{self.base_url}/jobs/runs/get",
                headers=self.headers,
                params={"run_id": run_id},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching job run {run_id}: {str(e)}")
            return {"error": str(e)}

    def get_job_run_output(self, run_id: int) -> Dict[str, Any]:
        """Get output of a job run
        
        Args:
            run_id: The job run ID
            
        Returns:
            Job run output and logs
        """
        try:
            response = requests.get(
                f"{self.base_url}/jobs/runs/get-output",
                headers=self.headers,
                params={"run_id": run_id},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching output for run {run_id}: {str(e)}")
            return {"error": str(e)}

    def submit_job_run(self, job_id: int, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Submit a job run
        
        Args:
            job_id: The job ID to run
            parameters: Optional parameters for the job
            
        Returns:
            Response with run_id
        """
        try:
            payload = {
                "job_id": job_id,
            }
            if parameters:
                payload["notebook_params"] = parameters
            
            response = requests.post(
                f"{self.base_url}/jobs/run-now",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Job run submitted: {result.get('run_id')}")
            return result
        except Exception as e:
            logger.error(f"Error submitting job run: {str(e)}")
            return {"error": str(e)}

    def cancel_job_run(self, run_id: int) -> bool:
        """Cancel a job run
        
        Args:
            run_id: The job run ID to cancel
            
        Returns:
            True if successful
        """
        try:
            response = requests.post(
                f"{self.base_url}/jobs/runs/cancel",
                headers=self.headers,
                json={"run_id": run_id},
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"Job run {run_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling job run {run_id}: {str(e)}")
            return False

    def list_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent jobs
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of jobs
        """
        try:
            response = requests.get(
                f"{self.base_url}/jobs/list",
                headers=self.headers,
                params={"limit": limit},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("jobs", [])
        except Exception as e:
            logger.error(f"Error listing jobs: {str(e)}")
            return []

    def get_cluster_info(self, cluster_id: str) -> Dict[str, Any]:
        """Get cluster information
        
        Args:
            cluster_id: The cluster ID
            
        Returns:
            Cluster information
        """
        try:
            response = requests.get(
                f"{self.base_url}/clusters/get",
                headers=self.headers,
                params={"cluster_id": cluster_id},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching cluster info: {str(e)}")
            return {"error": str(e)}

    def get_workspace_status(self) -> bool:
        """Check if workspace is accessible
        
        Returns:
            True if workspace is accessible
        """
        try:
            response = requests.get(
                f"{self.base_url}/workspace/get-status",
                headers=self.headers,
                params={"path": "/"},
                timeout=30
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error checking workspace status: {str(e)}")
            return False

    def execute_sql_query(self, query: str, warehouse_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute SQL query using SQL Warehouse
        
        Args:
            query: SQL query to execute
            warehouse_id: Optional warehouse ID
            
        Returns:
            Query execution status
        """
        try:
            payload = {
                "statement": query,
            }
            if warehouse_id:
                payload["warehouse_id"] = warehouse_id
            
            response = requests.post(
                f"{self.base_url}/sql/statements",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error executing SQL query: {str(e)}")
            return {"error": str(e)}
