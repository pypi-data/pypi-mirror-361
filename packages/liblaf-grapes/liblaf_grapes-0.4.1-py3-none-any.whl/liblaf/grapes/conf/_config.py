import enum
import sys
from pathlib import Path

import platformdirs
import pydantic
import pydantic_settings as ps


def joblib_memory_location() -> Path:
    return platformdirs.user_cache_path(appname="joblib")


def log_file() -> Path:
    entrypoint: Path = Path(sys.argv[0])
    return entrypoint.parent / "run.log"


class LogLevel(enum.StrEnum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Config(ps.BaseSettings):
    model_config = ps.SettingsConfigDict(env_prefix="PLAYGROUND_")

    joblib_memory_bytes_limit: int | str | None = pydantic.Field(default="1G")

    joblib_memory_location: Path = pydantic.Field(
        default_factory=joblib_memory_location
    )

    log_file: Path | None = pydantic.Field(default=None)

    log_level: LogLevel = pydantic.Field(default=LogLevel.INFO)


config = Config()
