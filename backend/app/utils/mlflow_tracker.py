import os
import logging
from typing import Dict, Any

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentiment_platform.mlflow")

class MLflowTracker:
    """
    Coordinates MLflow experiment tracking.
    Handles parameters and performance metric logging with a graceful fallback if MLflow is not running.
    """
    
    @staticmethod
    def log_run(experiment_name: str, run_name: str, params: Dict[str, Any], metrics: Dict[str, float]):
        try:
            import mlflow
            
            # Load tracking URI from environment
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlruns")
            mlflow.set_tracking_uri(tracking_uri)
            
            # Set experiment
            mlflow.set_experiment(experiment_name)
            
            with mlflow.start_run(run_name=run_name):
                # Log hyperparameters/architectures
                for param_key, param_val in params.items():
                    mlflow.log_param(param_key, param_val)
                    
                # Log metrics
                for metric_key, metric_val in metrics.items():
                    mlflow.log_metric(metric_key, metric_val)
                    
                logger.info(f"MLflow: Logged run '{run_name}' under experiment '{experiment_name}' to {tracking_uri}.")
                
        except Exception as e:
            logger.warning(f"MLflow tracking is offline or failed to log run ({e}). Continuing run execution.")
