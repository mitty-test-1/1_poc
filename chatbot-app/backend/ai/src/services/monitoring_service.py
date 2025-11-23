import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import threading
import json
from collections import defaultdict, deque

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Metric:
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    metric_type: MetricType

class MonitoringService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.alerts = []
        self.thresholds = {
            "ai_response_time": 2000.0,  # ms
            "ai_accuracy": 0.85,  # percentage
            "error_rate": 0.05,  # percentage
            "throughput": 100  # requests per minute
        }
        self.is_monitoring = False
        self.monitoring_thread = None
        self.ai_metrics = {}
        self.service_metrics = {}
        
    async def start_monitoring(self, interval: int = 60):
        """Start AI service monitoring"""
        try:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(interval,),
                daemon=True
            )
            self.monitoring_thread.start()
            self.logger.info(f"Started AI service monitoring with {interval}s interval")
            
        except Exception as e:
            self.logger.error(f"Error starting AI service monitoring: {e}")
    
    async def stop_monitoring(self):
        """Stop AI service monitoring"""
        try:
            self.is_monitoring = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
            self.logger.info("Stopped AI service monitoring")
            
        except Exception as e:
            self.logger.error(f"Error stopping AI service monitoring: {e}")
    
    def _monitoring_loop(self, interval: int):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect AI-specific metrics
                self._collect_ai_metrics()
                
                # Check thresholds
                self._check_thresholds()
                
                # Sleep for interval
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in AI monitoring loop: {e}")
                time.sleep(interval)
    
    def _collect_ai_metrics(self):
        """Collect AI service performance metrics"""
        try:
            timestamp = datetime.utcnow()
            
            # AI processing metrics
            ai_metrics = {
                "response_time": self._get_average_response_time(),
                "accuracy": self._get_current_accuracy(),
                "error_rate": self._get_error_rate(),
                "throughput": self._get_throughput(),
                "model_performance": self._get_model_performance(),
                "resource_usage": self._get_resource_usage()
            }
            
            # Store metrics
            for metric_name, value in ai_metrics.items():
                metric = Metric(
                    name=f"ai_{metric_name}",
                    value=value,
                    timestamp=timestamp,
                    tags={"service": "ai"},
                    metric_type=MetricType.GAUGE
                )
                self.metrics_history[metric.name].append(metric)
            
            self.ai_metrics = ai_metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting AI metrics: {e}")
    
    def _get_average_response_time(self) -> float:
        """Calculate average AI response time"""
        # Mock implementation - in real scenario, this would query actual metrics
        return 150.0  # ms
    
    def _get_current_accuracy(self) -> float:
        """Get current AI model accuracy"""
        # Mock implementation - in real scenario, this would query model performance
        return 0.92  # 92% accuracy
    
    def _get_error_rate(self) -> float:
        """Calculate AI service error rate"""
        # Mock implementation - in real scenario, this would query error logs
        return 0.02  # 2% error rate
    
    def _get_throughput(self) -> float:
        """Calculate AI service throughput"""
        # Mock implementation - in real scenario, this would query request logs
        return 75  # requests per minute
    
    def _get_model_performance(self) -> Dict[str, float]:
        """Get model performance metrics"""
        # Mock implementation - in real scenario, this would query model metrics
        return {
            "nlp_accuracy": 0.95,
            "intent_recognition": 0.88,
            "sentiment_analysis": 0.91,
            "response_generation": 0.89
        }
    
    def _get_resource_usage(self) -> Dict[str, float]:
        """Get AI service resource usage"""
        # Mock implementation - in real scenario, this would query system metrics
        return {
            "cpu_usage": 45.2,  # percentage
            "memory_usage": 62.8,  # percentage
            "gpu_usage": 78.5,  # percentage
            "disk_usage": 34.1  # percentage
        }
    
    def _check_thresholds(self):
        """Check if metrics exceed thresholds"""
        try:
            issues = []
            
            # Check response time
            if self.ai_metrics.get("response_time", 0) > self.thresholds["ai_response_time"]:
                issues.append({
                    "metric": "response_time",
                    "value": self.ai_metrics["response_time"],
                    "threshold": self.thresholds["ai_response_time"],
                    "severity": "warning"
                })
            
            # Check accuracy
            if self.ai_metrics.get("accuracy", 0) < self.thresholds["ai_accuracy"]:
                issues.append({
                    "metric": "accuracy",
                    "value": self.ai_metrics["accuracy"],
                    "threshold": self.thresholds["ai_accuracy"],
                    "severity": "critical"
                })
            
            # Check error rate
            if self.ai_metrics.get("error_rate", 0) > self.thresholds["error_rate"]:
                issues.append({
                    "metric": "error_rate",
                    "value": self.ai_metrics["error_rate"],
                    "threshold": self.thresholds["error_rate"],
                    "severity": "critical"
                })
            
            # Check throughput
            if self.ai_metrics.get("throughput", 0) < self.thresholds["throughput"] * 0.5:
                issues.append({
                    "metric": "throughput",
                    "value": self.ai_metrics["throughput"],
                    "threshold": self.thresholds["throughput"] * 0.5,
                    "severity": "warning"
                })
            
            # Create alerts for issues
            for issue in issues:
                alert = {
                    "id": f"ai_{issue['metric']}_{int(time.time())}",
                    "timestamp": datetime.utcnow(),
                    "metric": issue["metric"],
                    "value": issue["value"],
                    "threshold": issue["threshold"],
                    "severity": issue["severity"],
                    "service": "ai",
                    "message": f"AI {issue['metric']} is {issue['value']} (threshold: {issue['threshold']})"
                }
                self.alerts.append(alert)
                self.logger.warning(f"AI Alert: {alert['message']}")
                
        except Exception as e:
            self.logger.error(f"Error checking thresholds: {e}")
    
    def record_ai_request(self, request_type: str, response_time: float, 
                         success: bool, model_used: str):
        """Record an AI request for metrics"""
        try:
            timestamp = datetime.utcnow()
            
            # Record request metrics
            request_metric = Metric(
                name="ai_requests",
                value=1,
                timestamp=timestamp,
                tags={
                    "request_type": request_type,
                    "model": model_used,
                    "success": str(success)
                },
                metric_type=MetricType.COUNTER
            )
            self.metrics_history[request_metric.name].append(request_metric)
            
            # Record response time
            response_metric = Metric(
                name="ai_response_time",
                value=response_time,
                timestamp=timestamp,
                tags={
                    "request_type": request_type,
                    "model": model_used
                },
                metric_type=MetricType.HISTOGRAM
            )
            self.metrics_history[response_metric.name].append(response_metric)
            
        except Exception as e:
            self.logger.error(f"Error recording AI request: {e}")
    
    def record_ai_accuracy(self, model: str, task: str, accuracy: float):
        """Record AI model accuracy"""
        try:
            timestamp = datetime.utcnow()
            
            accuracy_metric = Metric(
                name="ai_accuracy",
                value=accuracy,
                timestamp=timestamp,
                tags={
                    "model": model,
                    "task": task
                },
                metric_type=MetricType.GAUGE
            )
            self.metrics_history[accuracy_metric.name].append(accuracy_metric)
            
        except Exception as e:
            self.logger.error(f"Error recording AI accuracy: {e}")
    
    def get_ai_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get AI metrics for the specified time period"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            metrics_data = {
                "period": f"Last {hours} hours",
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {},
                "alerts": [alert for alert in self.alerts if alert["timestamp"] >= cutoff_time]
            }
            
            # Collect AI metrics
            for metric_name, metrics in self.metrics_history.items():
                if metric_name.startswith("ai_"):
                    period_metrics = []
                    for metric in metrics:
                        if metric.timestamp >= cutoff_time:
                            period_metrics.append({
                                "name": metric.name,
                                "value": metric.value,
                                "timestamp": metric.timestamp.isoformat(),
                                "tags": metric.tags
                            })
                    
                    if period_metrics:
                        metrics_data["metrics"][metric_name] = period_metrics
            
            return metrics_data
            
        except Exception as e:
            self.logger.error(f"Error getting AI metrics: {e}")
            return {"error": str(e)}
    
    def update_thresholds(self, new_thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Update monitoring thresholds"""
        try:
            self.thresholds.update(new_thresholds)
            self.logger.info(f"Updated AI monitoring thresholds: {new_thresholds}")
            return {"success": True, "message": "Thresholds updated successfully"}
            
        except Exception as e:
            self.logger.error(f"Error updating thresholds: {e}")
            return {"success": False, "message": str(e)}
    
    def get_ai_health_status(self) -> Dict[str, Any]:
        """Get overall AI service health status"""
        try:
            status = "healthy"
            issues = []
            
            # Check response time
            if self.ai_metrics.get("response_time", 0) > self.thresholds["ai_response_time"]:
                issues.append("high_response_time")
                status = "degraded"
            
            # Check accuracy
            if self.ai_metrics.get("accuracy", 0) < self.thresholds["ai_accuracy"]:
                issues.append("low_accuracy")
                status = "critical"
            
            # Check error rate
            if self.ai_metrics.get("error_rate", 0) > self.thresholds["error_rate"]:
                issues.append("high_error_rate")
                status = "critical"
            
            return {
                "status": status,
                "issues": issues,
                "metrics": self.ai_metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting AI health status: {e}")
            return {"status": "unknown", "error": str(e)}
    
    def export_metrics(self, format: str = "json", hours: int = 24) -> Dict[str, Any]:
        """Export AI metrics in specified format"""
        try:
            metrics_data = self.get_ai_metrics(hours)
            
            if format.lower() == "json":
                return metrics_data
            else:
                # For other formats, return the data structure that can be converted
                return {"data": metrics_data, "format": format}
                
        except Exception as e:
            self.logger.error(f"Error exporting AI metrics: {e}")
            return {"error": str(e)}