"""
Nexus Warmup Engine — Observability Module
Structured logging, distributed tracing, and metrics.
"""
import logging
import json
import time
import uuid
from contextlib import asynccontextmanager
from functools import wraps
from datetime import datetime, timezone


# ─────────────────────────────────────────────
# 1. STRUCTURED LOGGER
# ─────────────────────────────────────────────

class StructuredFormatter(logging.Formatter):
    """JSON-structured log formatter for production observability."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Attach trace context if available
        if hasattr(record, "trace_id"):
            log_entry["trace_id"] = record.trace_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "account_id"):
            log_entry["account_id"] = record.account_id
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms
        if hasattr(record, "extra_data"):
            log_entry["context"] = record.extra_data
            
        # Attach exception info
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }
        
        return json.dumps(log_entry)


def setup_structured_logging(level=logging.INFO):
    """Configure structured JSON logging for the entire application."""
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())
    
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)
    
    # Silence noisy libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


# ─────────────────────────────────────────────
# 2. DISTRIBUTED TRACING (lightweight)
# ─────────────────────────────────────────────

class TraceContext:
    """Lightweight distributed trace context."""
    
    def __init__(self, trace_id: str = None, parent_span: str = None):
        self.trace_id = trace_id or uuid.uuid4().hex[:16]
        self.span_id = uuid.uuid4().hex[:8]
        self.parent_span = parent_span
        self.start_time = time.perf_counter()
        self.attributes = {}
    
    def set_attribute(self, key: str, value):
        self.attributes[key] = value
    
    @property
    def duration_ms(self):
        return round((time.perf_counter() - self.start_time) * 1000, 2)
    
    def to_dict(self):
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span": self.parent_span,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
        }


# ─────────────────────────────────────────────
# 3. METRICS COLLECTOR (in-memory, exportable)
# ─────────────────────────────────────────────

class MetricsCollector:
    """Collects application metrics for health monitoring and alerting."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # Counters
        self.requests_total = 0
        self.requests_failed = 0
        self.emails_sent = 0
        self.emails_failed = 0
        self.ai_generations = 0
        self.ai_failures = 0
        self.stripe_events = 0
        
        # Latency tracking (for percentile calculation)
        self._latencies = []
        self._max_latencies = 1000  # Rolling window
        
        # DB metrics
        self.db_queries = 0
        self.db_slow_queries = 0  # > 500ms
        
        self.started_at = datetime.now(timezone.utc)
    
    def record_request(self, duration_ms: float, success: bool = True):
        self.requests_total += 1
        if not success:
            self.requests_failed += 1
        self._latencies.append(duration_ms)
        if len(self._latencies) > self._max_latencies:
            self._latencies.pop(0)
    
    def record_email(self, success: bool):
        if success:
            self.emails_sent += 1
        else:
            self.emails_failed += 1
    
    def record_ai_call(self, success: bool):
        self.ai_generations += 1
        if not success:
            self.ai_failures += 1
    
    def record_db_query(self, duration_ms: float):
        self.db_queries += 1
        if duration_ms > 500:
            self.db_slow_queries += 1
    
    def get_latency_percentiles(self):
        if not self._latencies:
            return {"p50": 0, "p95": 0, "p99": 0}
        
        sorted_lat = sorted(self._latencies)
        n = len(sorted_lat)
        return {
            "p50": sorted_lat[int(n * 0.50)],
            "p95": sorted_lat[int(n * 0.95)] if n > 1 else sorted_lat[0],
            "p99": sorted_lat[int(n * 0.99)] if n > 1 else sorted_lat[0],
        }
    
    def snapshot(self):
        """Return a full metrics snapshot for the /health/deep endpoint."""
        uptime = (datetime.now(timezone.utc) - self.started_at).total_seconds()
        percentiles = self.get_latency_percentiles()
        error_rate = (self.requests_failed / self.requests_total * 100) if self.requests_total > 0 else 0
        
        return {
            "uptime_seconds": round(uptime),
            "requests": {
                "total": self.requests_total,
                "failed": self.requests_failed,
                "error_rate_pct": round(error_rate, 2),
                "throughput_rpm": round(self.requests_total / max(uptime / 60, 1), 2),
            },
            "latency": {
                "p50_ms": round(percentiles["p50"], 2),
                "p95_ms": round(percentiles["p95"], 2),
                "p99_ms": round(percentiles["p99"], 2),
            },
            "warmup_engine": {
                "emails_sent": self.emails_sent,
                "emails_failed": self.emails_failed,
                "delivery_rate_pct": round(self.emails_sent / max(self.emails_sent + self.emails_failed, 1) * 100, 2),
            },
            "ai": {
                "total_generations": self.ai_generations,
                "failures": self.ai_failures,
                "success_rate_pct": round((self.ai_generations - self.ai_failures) / max(self.ai_generations, 1) * 100, 2),
            },
            "database": {
                "total_queries": self.db_queries,
                "slow_queries": self.db_slow_queries,
            },
        }


# Singleton accessor
metrics = MetricsCollector()
