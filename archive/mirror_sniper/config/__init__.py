"""Configuration loading for MirrorSniper."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    url: str = "sqlite+aiosqlite:///./mirror_sniper.db"
    echo: bool = False


class RpcConfig(BaseModel):
    primary: str = "https://api.mainnet-beta.solana.com"
    backup: str | None = None
    http_url: str = "https://api.mainnet-beta.solana.com"
    ws_url: str = "wss://api.mainnet-beta.solana.com"
    timeout_seconds: float = 15.0


class HeliusConfig(BaseModel):
    base_url: str = "https://api.helius.xyz"
    webhook_path: str = "/webhook/helius"


class WalletConfig(BaseModel):
    min_sol_balance: float = 0.01


class ExecutionConfig(BaseModel):
    max_slippage_bps: int = 100
    priority_fee_multiplier: float = 1.5
    simulation_required: bool = True
    confirmation_timeout: int = 60
    max_retries: int = 3


class RiskConfig(BaseModel):
    execution_mode: str = "paper"
    max_position_size_sol: float = 1.0
    max_daily_loss_sol: float = 2.0
    stop_loss_percent: float = 15.0
    take_profit_percent: float = 35.0
    min_target_wallet_win_rate: float = 0.50
    min_target_wallet_profit_factor: float = 1.2


class TradingConfig(BaseModel):
    execution_mode: str = "paper"
    trading_enabled: bool = True
    slippage_bps: int = 150
    default_buy_size_sol: float = 0.25
    max_parallel_trades: int = 5
    poll_interval_seconds: float = 1.0


class TelegramAlertConfig(BaseModel):
    enabled: bool = False
    bot_token: str | None = None
    chat_id: str | None = None


class DiscordAlertConfig(BaseModel):
    enabled: bool = False
    webhook_url: str | None = None


class AlertsConfig(BaseModel):
    telegram: TelegramAlertConfig = Field(default_factory=TelegramAlertConfig)
    discord: DiscordAlertConfig = Field(default_factory=DiscordAlertConfig)


class AppConfig(BaseModel):
    app_name: str = "MirrorSniper"
    environment: str = "development"
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    rpc: RpcConfig = Field(default_factory=RpcConfig)
    helius: HeliusConfig = Field(default_factory=HeliusConfig)
    wallet: WalletConfig = Field(default_factory=WalletConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    trading: TradingConfig = Field(default_factory=TradingConfig)
    alerts: AlertsConfig = Field(default_factory=AlertsConfig)
    tracked_wallets: list[dict[str, str]] = Field(default_factory=list)


class Secrets(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MIRROR_",
        env_file=(".env", "config/secrets.env"),
        extra="ignore",
    )

    database_url: str | None = None
    solana_private_key: str | None = None
    solana_public_key: str | None = None
    helius_api_key: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None


class Settings(BaseModel):
    app: AppConfig
    secrets: Secrets


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Settings file not found: {path}")
    content = yaml.safe_load(path.read_text(encoding="utf-8"))
    if content is None:
        return {}
    if not isinstance(content, dict):
        raise ValueError("settings.yaml must define a top-level mapping")
    return content


def load_settings(config_path: str | Path | None = None) -> Settings:
    path = Path(config_path) if config_path else Path(__file__).with_name("settings.yaml")
    app_config = AppConfig.model_validate(_load_yaml(path))
    secrets = Secrets()

    if app_config.rpc.primary and not app_config.rpc.http_url:
        app_config.rpc.http_url = app_config.rpc.primary
    if app_config.rpc.http_url and not app_config.rpc.primary:
        app_config.rpc.primary = app_config.rpc.http_url

    if secrets.database_url:
        app_config.database.url = secrets.database_url
    if secrets.telegram_bot_token and not app_config.alerts.telegram.bot_token:
        app_config.alerts.telegram.bot_token = secrets.telegram_bot_token
    if secrets.telegram_chat_id and not app_config.alerts.telegram.chat_id:
        app_config.alerts.telegram.chat_id = secrets.telegram_chat_id

    return Settings(app=app_config, secrets=secrets)
