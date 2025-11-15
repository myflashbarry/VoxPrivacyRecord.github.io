"""Configuration module for the backend."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    api_cors_origins: str = "*"  # Comma-separated list of origins
    
    # File paths
    base_dir: Path = Path(__file__).parent
    recordings_dir: Path = base_dir / "recordings"
    db_path: Path = base_dir / "db.sqlite3"
    
    # JSONL data files (auto-detect: Docker vs local)
    # In Docker: /app/source/ (copied by Dockerfile)
    # In local: ../source/ (relative to backend/)
    _source_dir_docker: Path = base_dir / "source"
    _source_dir_local: Path = base_dir.parent / "source"
    
    @property
    def source_dir(self) -> Path:
        # Check if Docker source exists, otherwise use local
        if self._source_dir_docker.exists():
            return self._source_dir_docker
        return self._source_dir_local
    
    @property  
    def zh_jsonl_path(self) -> Path:
        return self.source_dir / "deepseek_secret_filter_results_filtered_zh.jsonl"
    
    @property
    def en_jsonl_path(self) -> Path:
        return self.source_dir / "deepseek_secret_filter_results_filtered_en.jsonl"
    
    # Task quotas
    zh_pairs_quota: int = 20
    en_pairs_quota: int = 20
    zh_extra_quota: int = 10
    en_extra_quota: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.api_cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.api_cors_origins.split(",")]
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.recordings_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()

