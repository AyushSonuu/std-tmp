from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str

    # Settings for creating the first superuser
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    # Payment provider settings
    RAZORPAY_KEY_ID: str | None = None
    RAZORPAY_KEY_SECRET: str | None = None
    DEFAULT_PAYMENT_PROVIDER: str = "razorpay"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
