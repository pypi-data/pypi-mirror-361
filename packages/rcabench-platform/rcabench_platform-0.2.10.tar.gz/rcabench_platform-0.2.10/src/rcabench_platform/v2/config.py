from dataclasses import dataclass
from pathlib import Path
from contextlib import contextmanager
import os


@dataclass(kw_only=True)
class Config:
    data: Path
    output: Path
    temp: Path

    base_url: str


_DEFAULT_DATA_ROOT = Path(os.getenv("DATA_ROOT", "data/rcabench-platform-v2"))
_DEFAULT_OUTPUT_ROOT = Path(os.getenv("OUTPUT_ROOT", "output/rcabench-platform-v2"))
_DEFAULT_TEMP_ROOT = Path(os.getenv("TEMP_ROOT", "temp"))

_DEV_CONFIG = Config(
    data=_DEFAULT_DATA_ROOT,
    output=_DEFAULT_OUTPUT_ROOT,
    temp=_DEFAULT_TEMP_ROOT,
    base_url="https://10.10.10.161:8082",
)

_PROD_CONFIG = Config(
    data=_DEFAULT_DATA_ROOT,
    output=_DEFAULT_OUTPUT_ROOT,
    temp=_DEFAULT_TEMP_ROOT,
    base_url="http://10.10.10.220:32080",
)

CONFIG_CLASSES = {
    "dev": _DEV_CONFIG,
    "prod": _PROD_CONFIG,
}


def _get_config() -> Config:
    env = os.getenv("ENV_MODE", "prod").lower()
    return CONFIG_CLASSES.get(env, _PROD_CONFIG)


_CONFIG = None


def get_config() -> Config:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = _get_config()
    return _CONFIG


def set_config(config: Config):
    global _CONFIG
    _CONFIG = config


@contextmanager
def current_config(config: Config):
    global _CONFIG

    old_config = _CONFIG
    _CONFIG = config

    try:
        yield
    finally:
        _CONFIG = old_config
