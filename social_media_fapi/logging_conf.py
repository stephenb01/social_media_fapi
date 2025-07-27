from logging.config import dictConfig

from social_media_fapi.config import DevConfig, config

def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(name)s:%(lineno)d - %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console"
                }
            },
            "loggers": {
                "social_media_fapi" : {
                    "handlers": ["default"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False # Don't send any loggers up to the root logger # root.social_media_fapi.routers.post
                }
            }
        }
    )