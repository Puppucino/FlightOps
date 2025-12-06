"""
Application Configuration Settings
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./flight_delays.db"
    
    # CORS - accepts comma-separated string or list
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173"
    
    # External API Keys (loaded from .env file)
    # Note: AviationWeather.gov API does NOT require an API key
    WEATHER_API_KEY: str = ""  # Not currently used - AviationWeather API is public
    AVIATION_API_KEY: str = ""  # For adsbdb.com or other aviation APIs (if needed)
    DEEPSEEK_API_KEY: str = ""  # Required for AI agent features
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"  # Using deepseek-chat for best balance
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v if isinstance(v, list) else [v]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

