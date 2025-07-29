"""Configuration for the CHIME logging system."""

import os

DEFAULT_LOKI_URL = "https://frb.chimenet.ca/loki/loki/api/v1/push"
DEFAULT_LOKI_TENANT = "CHIME"

LOKI_AUTH = (
    (
        os.getenv("CHIME_LOGGER_LOKI_USER"),
        os.getenv("CHIME_LOGGER_LOKI_PASSWORD"),
    )
    if os.getenv("CHIME_LOGGER_LOKI_USER") and os.getenv("CHIME_LOGGER_LOKI_PASSWORD")
    else None
)

# TODO: Allow pushing to multiple Loki instances
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {"format": "[ pipeline=%(pipeline)s event=%(event)s ] %(message)s"},
    },
    "filters": {
        "add_pipeline_filter": {"()": "chime_logger.filters.PipelineFilter"},
        "add_event_filter": {"()": "chime_logger.filters.EventFilter"},
    },
    "handlers": {
        "loki": {
            "()": "chime_logger.handlers.LokiHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filters": ["add_pipeline_filter", "add_event_filter"],
            "url": os.getenv("CHIME_LOGGER_LOKI_URL", DEFAULT_LOKI_URL),
            "auth": LOKI_AUTH,
            "headers": {
                "X-Scope-OrgID": os.getenv(
                    "CHIME_LOGGER_LOKI_TENANT", DEFAULT_LOKI_TENANT
                )
            },
            "version": "2",
        },
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "handlers": ["loki"],
            "filters": ["add_pipeline_filter", "add_event_filter"],
            "respect_handler_level": True,
        },
    },
    "loggers": {
        "CHIME": {"level": "INFO", "handlers": ["queue_handler"], "propagate": False}
    },
}
