"""
Centralised config loader — all values come from environment variables.
NO hardcoded secrets. NO default credentials for live/testnet.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import os


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    log_level: str = "INFO"
    audit_log_enabled: bool = True

    # Database
    database_url: Optional[str] = None

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None

    # Internal API
    execution_core_api_key: Optional[str] = None

    # Supabase JWT
    supabase_jwt_secret: Optional[str] = None

    # Exchange — BTCC (testnet flag enforced programmatically)
    btcc_api_key: Optional[str] = None
    btcc_api_secret: Optional[str] = None
    btcc_testnet: bool = True

    # Exchange — Bitget
    bitget_api_key: Optional[str] = None
    bitget_api_secret: Optional[str] = None
    bitget_passphrase: Optional[str] = None
    bitget_testnet: bool = True

    # CCXT
    ccxt_sandbox_mode: bool = True

    # Kill-switch
    kill_switch_secret: Optional[str] = None
    auto_kill_drawdown_pct: float = 5.0
    auto_kill_loss_usd: float = 1000.0

    # Risk limits
    max_position_size_usd: float = 10000.0
    max_daily_loss_usd: float = 500.0
    max_open_positions: int = 10

    # Services
    prediction_bot_url: str = "http://localhost:8001"
    prediction_bot_api_key: Optional[str] = None
    guardian_bot_url: str = "http://localhost:8002"
    guardian_bot_api_key: Optional[str] = None

    @field_validator("app_env")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "testnet", "production"}
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v

    @property
    def is_live(self) -> bool:
        return self.app_env == "production"

    @property
    def is_testnet(self) -> bool:
        return self.app_env == "testnet"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
