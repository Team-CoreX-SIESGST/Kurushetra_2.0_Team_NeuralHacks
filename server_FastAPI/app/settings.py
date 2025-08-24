import os
import psutil
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # MongoDB settings (optional for demo)
    mongodb_url: str = ""
    server_port: int = 8000
    
    # Authentication settings (optional for demo)
    access_token_secret: str = "demo_access_token_secret_for_testing_only"
    refresh_token_secret: str = "demo_refresh_token_secret_for_testing_only"
    
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
