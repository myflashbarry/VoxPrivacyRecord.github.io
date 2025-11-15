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
    
    # Use persistent disk if available (Render: /app/data), otherwise local
    data_dir: Path = Path("/app/data") if Path("/app/data").exists() else base_dir
    
    recordings_dir: Path = data_dir / "recordings"
    db_path: Path = data_dir / "db.sqlite3"
    
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
    zh_nobody_quota: int = 5
    zh_onlyme_quota: int = 5
    zh_pairs_quota: int = 20
    zh_extra_quota: int = 10
    en_nobody_quota: int = 5
    en_onlyme_quota: int = 5
    en_pairs_quota: int = 20
    en_extra_quota: int = 10
    
    # Instruction TXT files
    @property
    def zh_nobody_txt(self) -> Path:
        return self.source_dir / "instruction_zh_nobody.txt"
    
    @property
    def zh_onlyme_txt(self) -> Path:
        return self.source_dir / "instruction_zh_onlyme.txt"
    
    @property
    def en_nobody_txt(self) -> Path:
        return self.source_dir / "instruction_en_nobody.txt"
    
    @property
    def en_onlyme_txt(self) -> Path:
        return self.source_dir / "instruction_en_onlyme.txt"
    
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

