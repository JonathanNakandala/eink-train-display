"""
Ensure that libraries that log are also captured by structlog
"""
import logging
import structlog


def setup_logging():
    """
    Setup standard logging to go through structlog.
    """
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,  # Decide which log levels to process.
            structlog.stdlib.add_logger_name,  # Add the logger name to the event dict.
            structlog.stdlib.add_log_level,  # Add the log level to the event dict.
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,  # Collect exception info.
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True)
        )
    )
    root_logger.addHandler(handler)
