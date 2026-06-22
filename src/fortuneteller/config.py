"""Central typed configuration so paths aren't hard-coded.

Downstream modules import the module-level ``settings`` singleton rather than
repeating path strings. Override any field via an ``FT_``-prefixed environment
variable (e.g. ``FT_DB_PATH``) or a local ``.env`` file.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_path: Path = Path("data/fortuneteller.duckdb")
    seed_dir: Path = Path("data/seed")
    schema_path: Path = Path("schema.sql")

    model_config = SettingsConfigDict(env_prefix="FT_", env_file=".env")


settings = Settings()
