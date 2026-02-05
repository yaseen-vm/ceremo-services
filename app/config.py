import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "3306"))
    DATABASE_USER: str = os.getenv("DATABASE_USER", "root")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "ceremo_db")

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    REFRESH_TOKEN_EXPIRATION_HOURS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRATION_HOURS", "720")
    )

    MIN_PASSWORD_LENGTH: int = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
    REMEMBER_ME_MULTIPLIER: int = int(os.getenv("REMEMBER_ME_MULTIPLIER", "24"))

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL."""
        return f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"


def get_settings() -> Config:
    return Config()
