# _ IMPORTS
from pydantic_settings import BaseSettings, SettingsConfigDict


# _ Main class
class Settings(BaseSettings):
    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore")

    DATABASE_URL:str=""
    JWT_SECRET:str=""
    JWT_ALGORITHM:str="HS256"
    JWT_EXPIRE_MINUTES:int=60

    def validate_required(self)->None:
        if not self.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not configured")
        if not self.JWT_SECRET:
            raise RuntimeError("JWT_SECRET is not configured")


settings=Settings()
settings.validate_required()
