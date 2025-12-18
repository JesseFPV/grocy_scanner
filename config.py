"""Configuration management for Intake."""
import json
import os
from typing import Optional, Dict


class Config:
    """Handles configuration loading and saving."""
    
    CONFIG_FILE = "config.json"
    
    def __init__(self):
        self.host: Optional[str] = None
        self.api_key: Optional[str] = None
        self.load()
    
    def load(self) -> bool:
        """Load configuration from config.json if it exists."""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.host = data.get('host', '').strip()
                    self.api_key = data.get('api_key', '').strip()
                    if self.host and self.api_key:
                        return True
            except (json.JSONDecodeError, KeyError, IOError) as e:
                print(f"Error loading config: {e}")
        return False
    
    def save(self, host: str, api_key: str) -> bool:
        """Save configuration to config.json."""
        try:
            # Normalize host URL (add https:// if no protocol)
            host = host.strip()
            if not host.startswith(('http://', 'https://')):
                host = f"https://{host}"
            
            data = {
                'host': host.rstrip('/'),
                'api_key': api_key.strip()
            }
            
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.host = data['host']
            self.api_key = data['api_key']
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if configuration is complete."""
        return bool(self.host and self.api_key)
    
    def get_dict(self) -> Dict[str, str]:
        """Get configuration as dictionary."""
        return {
            'host': self.host or '',
            'api_key': self.api_key or ''
        }

