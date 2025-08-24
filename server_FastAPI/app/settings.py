from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # MongoDB settings
    mongodb_url: str
    server_port: int = 8000
    
    # Authentication settings
    access_token_secret: str
    refresh_token_secret: str
    
    # Cloudinary settings
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    
    # S3 settings
    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "omnisea-uploads"
    storage_type: str = "local"  # 'local' or 's3'
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    
    # Vector database settings
    vector_db_type: str = "faiss"
    huggingface_api_token: str = ""
    
    # OpenAI settings (for fallback)
    openai_api_key: str = ""
    
    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    llama_local_path: str = ""
    
    # Auth settings
    auth_public_key_url: str = ""
    
    # Application mode
    demo_mode: str = "true"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # 👈 Add this to ignore extra fields
    )

settings = Settings()