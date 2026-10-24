"""
TITAN Inventory API - Structured JSON Logging
Provides standardized structured JSON output with context and correlation ID support.
"""

import sys
import logging
try:
    from pythonjsonlogger.json import JsonFormatter
except ImportError:
    from pythonjsonlogger.jsonlogger import JsonFormatter
from contextvars import ContextVar

# ContextVar for request-level correlation tracking
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="system")


class TitanJsonFormatter(JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["service"] = "inventory-api"
        log_record["level"] = record.levelname
        log_record["correlation_id"] = correlation_id_ctx.get()
        if "timestamp" not in log_record:
            log_record["timestamp"] = self.formatTime(record, self.datefmt)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("titan.inventory")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = TitanJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s %(correlation_id)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = setup_logging()
