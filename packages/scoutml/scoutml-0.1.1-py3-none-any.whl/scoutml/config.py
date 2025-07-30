"""Configuration management for ScoutML client."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration class for ScoutML client."""
    
    def __init__(self):
        # Load from .env file if it exists
        load_dotenv()
        
        # API settings
        self.api_key = os.getenv("SCOUTML_API_KEY")
        self.api_url = os.getenv("SCOUTML_API_URL", "http://0.0.0.0:8000")
        
        # Default settings
        self.default_limit = 20
        self.default_timeout = 60  # Increased timeout for complex operations
        self.max_retries = 3
        
        # Output settings
        self.default_output_format = "table"
        self.table_max_width = 120
        
        # Cache settings
        self.cache_dir = Path.home() / ".scoutml" / "cache"
        self.cache_ttl = 3600  # 1 hour
        
    @property
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)
    
    @property
    def headers(self) -> dict:
        """Get API request headers."""
        if not self.api_key:
            raise ValueError("API key not configured. Set SCOUTML_API_KEY environment variable.")
        
        return {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ScoutML-CLI/0.1.0"
        }
    
    def get_endpoint(self, path: str) -> str:
        """Get full API endpoint URL."""
        return f"{self.api_url.rstrip('/')}/{path.lstrip('/')}"
    
    def save_api_key(self, api_key: str):
        """Save API key to .env file."""
        env_path = Path(".env")
        
        # Read existing content
        content = []
        if env_path.exists():
            with open(env_path, "r") as f:
                content = f.readlines()
        
        # Update or add API key
        found = False
        for i, line in enumerate(content):
            if line.startswith("SCOUTML_API_KEY="):
                content[i] = f"SCOUTML_API_KEY={api_key}\n"
                found = True
                break
        
        if not found:
            content.append(f"SCOUTML_API_KEY={api_key}\n")
        
        # Write back
        with open(env_path, "w") as f:
            f.writelines(content)
        
        # Update current config
        self.api_key = api_key
        
        return True