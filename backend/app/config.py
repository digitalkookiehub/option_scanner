from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Upstox API Configuration
    UPSTOX_API_KEY: str = ""
    UPSTOX_API_SECRET: str = ""
    UPSTOX_REDIRECT_URL: str = ""
    UPSTOX_TOKEN_URL: str = "https://api.upstox.com/v2/login/authorization/token"
    UPSTOX_BASE_URL: str = "https://api.upstox.com"

    # Database
    DATABASE_URL: str = "postgresql://screener:screener123@localhost:5434/stock_screener"

    # App Settings
    AUTO_REFRESH_INTERVAL: int = 60
    MAX_PARALLEL_WORKERS: int = 50
    API_TIMEOUT: int = 5

    # Trading Settings
    DEFAULT_PROFIT_TARGET_PCT: float = 2.5
    DEFAULT_BUY_BUFFER_PCT: float = 0.2

    # Derived URLs (computed from base)
    @property
    def HISTORICAL_CANDLE_V2_URL(self) -> str:
        return f"{self.UPSTOX_BASE_URL}/v2/historical-candle"

    @property
    def INTRADAY_CANDLE_V2_URL(self) -> str:
        return f"{self.UPSTOX_BASE_URL}/v2/historical-candle/intraday"

    @property
    def OPTION_CONTRACT_URL(self) -> str:
        return f"{self.UPSTOX_BASE_URL}/v2/option/contract"

    @property
    def OPTION_CHAIN_URL(self) -> str:
        return f"{self.UPSTOX_BASE_URL}/v2/option/chain"

    @property
    def USER_PROFILE_URL(self) -> str:
        return f"{self.UPSTOX_BASE_URL}/v2/user/profile"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
