"""
Application Configuration
Manages all environment variables and settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Sparta AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 10
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: list = [".csv", ".xlsx", ".xls", ".json"]
    UPLOAD_DIR: str = "uploads"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7
    
    # Anthropic (optional)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    
    # AI Code Generation
    DEFAULT_AI_PROVIDER: str = "openai"  # "openai" or "anthropic"
    CODE_GENERATION_TEMPERATURE: float = 0.3  # Lower for more deterministic code
    CODE_GENERATION_MAX_TOKENS: int = 2000
    
    # Conversation Memory
    MAX_CONVERSATION_HISTORY: int = 50
    CONVERSATION_TOKEN_LIMIT: int = 8000
    CONVERSATION_CLEANUP_THRESHOLD: int = 3600  # seconds
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/sparta_ai.log"
    
    # Code Execution
    CODE_TIMEOUT: int = 30  # seconds
    MAX_EXECUTION_MEMORY: int = 512  # MB
    
    # WebSocket
    WS_MESSAGE_QUEUE_SIZE: int = 100
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Initialize settings
settings = Settings(_env_file=".env", _env_file_encoding="utf-8")  # type: ignore


# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
    Path("temp").mkdir(parents=True, exist_ok=True)


ensure_directories()
