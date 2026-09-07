import logging
import os
import sys

from dotenv import load_dotenv


def virtual_environment_is_active() -> bool:
    """Return True when Python runs inside a virtual environment."""
    return sys.prefix != sys.base_prefix


def main() -> None:
    """Load configuration and display safe environment information."""
    load_dotenv()

    app_env = os.getenv("APP_ENV", "development")
    default_log_level = "DEBUG" if app_env == "development" else "INFO"
    log_level = os.getenv("LOG_LEVEL", default_log_level).upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(levelname)s: %(message)s",
    )

    print(f"Python: {sys.version.split()[0]}")
    print(f"Environment: {app_env}")
    print(f"Log level: {log_level}")
    print(f"Virtual environment active: {virtual_environment_is_active()}")


if __name__ == "__main__":
    main()