import logging
import os

from logstash import LogstashFormatterVersion1, TCPLogstashHandler

LOGSTASH_HOST: str = os.getenv("LOGSTASH_HOST", "logstash")
LOGSTASH_PORT: int = int(os.getenv("LOGSTASH_PORT", "5000"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")


def get_logger(name: str = "patronx") -> logging.LoggerAdapter:
    """Return a configured logger with optional Logstash integration."""

    logger = logging.getLogger(name)
    environment = os.getenv("ENVIRONMENT", ENVIRONMENT)
    if logger.handlers:
        return logging.LoggerAdapter(logger, {"environment": environment})

    level = logging.getLevelName(LOG_LEVEL.upper())
    logger.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        )
    )
    logger.addHandler(stream_handler)

    try:
        logstash_handler = TCPLogstashHandler(
            LOGSTASH_HOST,
            LOGSTASH_PORT,
            version=1,
        )
        logstash_handler.setFormatter(LogstashFormatterVersion1())
        logger.addHandler(logstash_handler)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to configure Logstash handler: %s", exc)

    return logging.LoggerAdapter(logger, {"environment": environment})