from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


API_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = API_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: Literal["development", "test", "staging", "production"] = "development"
    APP_VERSION: str = "0.1.0"
    BUILD_ID: str = "local"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    FRONTEND_ORIGINS: str = ""
    TRUSTED_HOSTS: str = "127.0.0.1,localhost,testserver"
    TRUST_PROXY_HEADERS: bool = False
    DOCS_ENABLED: bool | None = None
    LOG_LEVEL: str = "INFO"
    AI_ANALYSIS_ENABLED: bool = True
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    IDEMPOTENCY_RETENTION_SECONDS: int = 3600
    SCANNER_BATCH_SIZE: int = 100
    SCANNER_MODE: Literal["local", "oneshot"] = "local"
    RENTCAST_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_VISION_MODEL: str = "gpt-5.4-mini"
    OPENAI_VISION_TIMEOUT_SECONDS: float = 60
    PHOTO_ANALYSIS_MAX_BATCH_SIZE: int = 12
    PHOTO_ANALYSIS_CONCURRENCY: int = 3
    PHOTO_REPAIR_COST_ASSUMPTIONS_JSON: str = ""
    COMPARABLE_MIN_SALES: int = 3
    COMPARABLE_MIN_RENTALS: int = 3
    COMPARABLE_MAX_DISTANCE_MILES: float = 25
    COMPARABLE_MAX_SALE_AGE_DAYS: int = 730
    COMPARABLE_MAX_RENTAL_AGE_DAYS: int = 365
    COMPARABLE_OUTLIER_DEVIATION: float = 0.6
    STRATEGY_WHOLESALE_ASSIGNMENT_FEE_TARGET: float = 15000
    STRATEGY_WHOLESALE_BUYER_DISCOUNT_PERCENTAGE: float = 0.70
    STRATEGY_WHOLETAIL_LIGHT_REHAB_ALLOWANCE: float = 15000
    STRATEGY_PURCHASE_CLOSING_COST_PERCENTAGE: float = 0.02
    STRATEGY_RESALE_CLOSING_COST_PERCENTAGE: float = 0.02
    STRATEGY_AGENT_DISPOSITION_PERCENTAGE: float = 0.06
    STRATEGY_MONTHLY_HOLDING_COST_ALLOWANCE: float = 2500
    STRATEGY_FLIP_HOLDING_PERIOD_MONTHS: int = 6
    STRATEGY_WHOLETAIL_HOLDING_PERIOD_MONTHS: int = 3
    STRATEGY_RENTAL_VACANCY_PERCENTAGE: float = 0.05
    STRATEGY_RENTAL_MANAGEMENT_PERCENTAGE: float = 0.08
    STRATEGY_RENTAL_MAINTENANCE_PERCENTAGE: float = 0.08
    STRATEGY_RENTAL_CAPITAL_RESERVE_PERCENTAGE: float = 0.05
    STRATEGY_MINIMUM_DESIRED_FLIP_MARGIN: float = 0.15
    STRATEGY_MINIMUM_DESIRED_RENTAL_CAP_RATE: float = 0.06
    STRATEGY_MINIMUM_WHOLESALE_SPREAD: float = 10000
    OFFER_WHOLESALE_BUYER_DISCOUNT_PERCENTAGE: float = 0.70
    OFFER_ASSIGNMENT_FEE_TARGET: float = 15000
    OFFER_DESIRED_WHOLESALE_SPREAD: float = 15000
    OFFER_DESIRED_FLIP_PROFIT_PERCENTAGE: float = 0.15
    OFFER_MINIMUM_FLIP_PROFIT_DOLLARS: float = 30000
    OFFER_WHOLETAIL_TARGET_MARGIN: float = 0.10
    OFFER_PURCHASE_CLOSING_COST_PERCENTAGE: float = 0.02
    OFFER_RESALE_CLOSING_COST_PERCENTAGE: float = 0.02
    OFFER_DISPOSITION_AGENT_PERCENTAGE: float = 0.06
    OFFER_HOLDING_COST_ALLOWANCE: float = 15000
    OFFER_WHOLETAIL_LIGHT_REHAB_ALLOWANCE: float = 15000
    OFFER_RENTAL_MINIMUM_CAP_RATE: float = 0.06
    OFFER_RENTAL_VACANCY_PERCENTAGE: float = 0.05
    OFFER_RENTAL_MANAGEMENT_PERCENTAGE: float = 0.08
    OFFER_RENTAL_MAINTENANCE_PERCENTAGE: float = 0.08
    OFFER_RENTAL_RESERVE_PERCENTAGE: float = 0.05
    OFFER_NEGOTIATION_BUFFER_PERCENTAGE: float = 0.05
    OFFER_ROUNDING_INCREMENT: float = 1000
    FINANCING_MIN_DSCR: float = 1.25
    FINANCING_MIN_CASH_ON_CASH_RETURN: float = 0.08
    FINANCING_MAX_LTV: float = 0.80
    FINANCING_MAX_LTC: float = 0.90
    FINANCING_MAX_BREAK_EVEN_OCCUPANCY: float = 0.85
    FINANCING_MAX_RATE_STRESS: float = 0.01
    FINANCING_MIN_RESERVE_MONTHS: float = 6
    NOTIFICATION_FOLLOW_UP_DUE_SOON_DAYS: int = 3
    NOTIFICATION_DEADLINE_DUE_SOON_DAYS: int = 7
    NOTIFICATION_OFFER_EXPIRATION_WARNING_HOURS: int = 48
    NOTIFICATION_STALE_LEAD_DAYS: int = 7
    NOTIFICATION_STALE_LEAD_DAYS_JSON: str = ""
    NOTIFICATION_UNDER_CONTRACT_CRITICAL_WINDOW_DAYS: int = 3
    NOTIFICATION_SCAN_INTERVAL_SECONDS: int = 300
    COMMUNICATIONS_ENABLED: bool = False
    EMAIL_PROVIDER: str = "console"
    SMS_PROVIDER: str = "console"
    ALLOW_CONSOLE_DELIVERY: bool = False
    COMMUNICATION_BUSINESS_NAME: str = "Property Intelligence"
    COMMUNICATION_SMS_OPT_OUT_TEXT: str = "Reply STOP to opt out."
    AUTH_REQUIRED: bool = True
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    @property
    def is_deployed(self) -> bool:
        return self.APP_ENV in {"staging", "production"}

    @property
    def docs_enabled(self) -> bool:
        if self.DOCS_ENABLED is not None:
            return self.DOCS_ENABLED
        return self.APP_ENV in {"development", "test"}

    @property
    def frontend_origins(self) -> list[str]:
        configured = [value.strip().rstrip("/") for value in self.FRONTEND_ORIGINS.split(",") if value.strip()]
        if configured:
            return configured
        if self.APP_ENV in {"development", "test"}:
            return ["http://localhost:5173", "http://127.0.0.1:5173"]
        return []

    @property
    def trusted_hosts(self) -> list[str]:
        return [value.strip() for value in self.TRUSTED_HOSTS.split(",") if value.strip()]

    def validation_errors(self) -> list[str]:
        required = {
            "APP_ENV": self.APP_ENV,
            "API_HOST": self.API_HOST,
            "API_PORT": self.API_PORT,
            "SUPABASE_URL": self.SUPABASE_URL,
            "SUPABASE_ANON_KEY": self.SUPABASE_ANON_KEY,
            "SUPABASE_SERVICE_ROLE_KEY": self.SUPABASE_SERVICE_ROLE_KEY,
            "LOG_LEVEL": self.LOG_LEVEL,
        }
        if self.is_deployed:
            required["FRONTEND_ORIGINS"] = self.FRONTEND_ORIGINS
        if self.AI_ANALYSIS_ENABLED:
            required["OPENAI_API_KEY"] = self.OPENAI_API_KEY
        errors = [f"{name} is required." for name, value in required.items() if value is None or str(value).strip() == ""]
        placeholders = ("your-", "replace-", "example", "changeme", "<", ">")
        if self.is_deployed:
            for name, value in required.items():
                normalized = str(value).strip().lower()
                if normalized and any(marker in normalized for marker in placeholders):
                    errors.append(f"{name} contains a placeholder value.")
            if any(origin == "*" for origin in self.frontend_origins):
                errors.append("FRONTEND_ORIGINS cannot contain '*' when credentials are enabled.")
            if self.COMMUNICATIONS_ENABLED and (self.EMAIL_PROVIDER == "console" or self.SMS_PROVIDER == "console"):
                errors.append("Console communication providers cannot be enabled in staging or production.")
        if self.NOTIFICATION_SCAN_INTERVAL_SECONDS < 1:
            errors.append("NOTIFICATION_SCAN_INTERVAL_SECONDS must be positive.")
        if self.SCANNER_BATCH_SIZE < 1:
            errors.append("SCANNER_BATCH_SIZE must be positive.")
        return errors

    def validate_runtime(self) -> None:
        errors = self.validation_errors()
        if errors:
            raise RuntimeError("Invalid application configuration: " + " ".join(errors))


@lru_cache
def get_settings() -> Settings:
    return Settings()
