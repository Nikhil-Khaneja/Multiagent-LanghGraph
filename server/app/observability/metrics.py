import time
from typing import Dict, Any

class MetricsCollector:
    """
    Collects observability metrics across the workflow.
    In a real system, this would push to Prometheus/DataDog.
    """
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "latency_ms": [],
            "ingestion_events": 0
        }
        
    def record_request(self, success: bool, latency_ms: float):
        self.metrics["total_requests"] += 1
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
            
        self.metrics["latency_ms"].append(latency_ms)
        # Keep only last 100 for memory
        if len(self.metrics["latency_ms"]) > 100:
            self.metrics["latency_ms"].pop(0)

    def record_ingestion(self):
        self.metrics["ingestion_events"] += 1
        
    def get_summary(self) -> dict:
        avg_latency = 0.0
        if self.metrics["latency_ms"]:
            avg_latency = sum(self.metrics["latency_ms"]) / len(self.metrics["latency_ms"])
            
        return {
            "total_requests": self.metrics["total_requests"],
            "success_rate": (self.metrics["successful_requests"] / max(1, self.metrics["total_requests"])) * 100,
            "avg_latency_ms": round(avg_latency, 2),
            "total_ingested_events": self.metrics["ingestion_events"]
        }

metrics_collector = MetricsCollector()
