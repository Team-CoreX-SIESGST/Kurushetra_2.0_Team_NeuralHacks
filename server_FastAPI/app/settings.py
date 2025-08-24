import os
import psutil
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator, root_validator
from typing import Optional, List, Dict, Any
from enum import Enum
import secrets
from pathlib import Path

class EnvironmentType(str, Enum):
    """Environment types for the application."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class LogLevel(str, Enum):
    """Available logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Settings(BaseSettings):
    """Enhanced application settings with validation and type safety."""
    
    # Environment configuration
    environment: EnvironmentType = Field(default=EnvironmentType.DEVELOPMENT, description="Application environment")
    debug: bool = Field(default=True, description="Enable debug mode")
    testing: bool = Field(default=False, description="Enable testing mode")
    
    # Server configuration
    server_host: str = Field(default="0.0.0.0", description="Server host")
    server_port: int = Field(default=8001, ge=1024, le=65535, description="Server port")
    server_workers: int = Field(default=1, ge=1, le=8, description="Number of worker processes")
    
    # Database settings
    mongodb_url: str = Field(default="", description="MongoDB connection URL")
    mongodb_database: str = Field(default="omnisearch", description="MongoDB database name")
    mongodb_timeout: int = Field(default=10000, description="MongoDB connection timeout in ms")
    
    # Authentication settings
    access_token_secret: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="JWT access token secret"
    )
    refresh_token_secret: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="JWT refresh token secret"
    )
    access_token_expire_minutes: int = Field(default=30, ge=1, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(default=7, ge=1, description="Refresh token expiration in days")
    
    # Cloudinary settings (optional for demo)
    cloudinary_cloud_name: str = "demo_cloud_name"
    cloudinary_api_key: str = "demo_api_key"
    cloudinary_api_secret: str = "demo_api_secret"
    
    # S3 settings (optional)
    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "omnisea-uploads"
    storage_type: str = "local"  # 'local' or 's3'
    
    # Redis settings (optional, for future use)
    redis_url: str = "redis://localhost:6379/0"
    
    # === GEMINI-ONLY SETTINGS ===
    
    # Gemini AI settings (optional for demo, but required for full functionality)
    gemini_api_key: str = ""
    
    # Enhanced document processing settings
    enhanced_processing_enabled: bool = True
    gemini_timeout_seconds: int = 30
    web_search_max_results: int = 10
    
    # File processing limits
    max_file_size: int = 10485760       # 10MB in bytes
    max_file_size_mb: int = 10          # For convenience
    
    # Rate limiting settings
    rate_limit_requests_per_minute: int = 20
    rate_limit_requests_per_hour: int = 100
    rate_limit_uploads_per_minute: int = 3
    rate_limit_uploads_per_hour: int = 10
    rate_limit_concurrent_uploads_per_user: int = 2
    rate_limit_max_global_uploads: int = 5
    rate_limit_max_file_size_mb: int = 10
    
    # Auth settings
    auth_public_key_url: str = ""
    
    # Application mode
    demo_mode: str = "true"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
    def get_available_ram_mb(self) -> int:
        """Get available RAM in MB."""
        try:
            return int(psutil.virtual_memory().available / (1024 * 1024))
        except:
            return 4096  # Default assumption
    
    def is_low_resource_system(self) -> bool:
        """Check if this is a low resource system."""
        return self.get_available_ram_mb() < 4096  # 4GB threshold
    
    def get_gemini_config(self) -> dict:
        """Get Gemini-specific configuration."""
        return {
            'api_key': self.gemini_api_key,
            'timeout_seconds': self.gemini_timeout_seconds,
            'web_search_max_results': self.web_search_max_results,
            'enhanced_processing_enabled': self.enhanced_processing_enabled
        }
    
    def get_resource_summary(self) -> dict:
        """Get a summary of current resource settings and system state."""
        return {
            'system': {
                'available_ram_mb': self.get_available_ram_mb(),
                'cpu_cores': psutil.cpu_count(logical=True),
                'is_low_resource': self.is_low_resource_system()
            },
            'gemini': self.get_gemini_config(),
            'limits': {
                'max_file_size_mb': self.max_file_size_mb,
                'max_ram_threshold_mb': 4096
            },
            'modes': {
                'demo_mode': self.demo_mode
            }
        }

settings = Settings()
