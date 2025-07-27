from logging.config import dictConfig

from social_media_fapi.config import DevConfig, config


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-"
                    # So the () above acts like the folloiwng:
                    # filter = asgi_correlation_id.CorrelationIdFilter(uuid_length=8, default_value="-")
                }
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s"
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    # "%(asctime)s.%(msec)03dZ  - Is the ISO standard for the date/time.
                    # "format": "%(asctime)s.%(msecs)03dZ | %(levelname)-8s | [%(correlation_id)s] %(name)s:%(lineno)d - %(message)s"  # The -8s means pad with up to 8 characters so it is always 8 characters long.         
                    # For the json output all we need are the fields in the format.
                    "format": "%(asctime)s %(msecs)03d %(levelname)-8s %(correlation_id)s %(name)s:%(lineno)d %(message)s"        
                }
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id"]
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "social_media_fapi.log",
                    "maxBytes": 1024 * 1024 * 1, # 1MB size
                    "backupCount": 2, # It will delete the old files when the number of files get to this count.
                    "encoding": "utf8",
                    "filters": ["correlation_id"]
                }
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default", "rotating_file"],
                    "level": "INFO"
                },
                "social_media_fapi" : {
                    "handlers": ["default", "rotating_file"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False # Don't send any loggers up to the root logger # root.social_media_fapi.routers.post
                },
                "databases": {
                    "handlers": ["default"],
                    "level": "WARNING"
                },
                "aiosqlite": {
                    "handlers": ["default"],
                    "level": "WARNING"
                },
            }
        }
    )