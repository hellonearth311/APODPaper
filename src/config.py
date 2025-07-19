"""
Configuration management for APODPaper
"""
import os
import json
from datetime import datetime


class Config:
    def __init__(self):
        self.appdata_local = os.getenv('LOCALAPPDATA')
        self.apod_folder = os.path.join(self.appdata_local, 'apodpaper')
        self.config_path = os.path.join(self.apod_folder, 'config.json')
        self.ensure_folder_exists()
    
    def ensure_folder_exists(self):
        """Ensure the apod folder exists"""
        os.makedirs(self.apod_folder, exist_ok=True)
    
    def get_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except:
            return {
                "NASA_API_KEY": "DEMO_KEY", 
                "last_update": "", 
                "auto_update": True,
                "update_frequency": "daily",
                "image_quality": "hd"
            }
    
    def save_config(self, config_data):
        """Save configuration to file"""
        with open(self.config_path, "w") as f:
            json.dump(config_data, f, indent=2)
    
    def get_api_key(self):
        """Get the NASA API key from config"""
        config = self.get_config()
        return config.get("NASA_API_KEY", "DEMO_KEY")
    
    def set_api_key(self, api_key):
        """Set the NASA API key in config"""
        config = self.get_config()
        config["NASA_API_KEY"] = api_key
        config["last_update"] = ""
        self.save_config(config)
    
    def is_valid_api_key(self, api_key):
        """Check if API key is valid (not DEMO_KEY)"""
        return api_key != "DEMO_KEY"
    
    def update_last_update(self):
        """Update the last update timestamp"""
        config = self.get_config()
        config["last_update"] = datetime.now().strftime("%Y-%m-%d")
        self.save_config(config)
    
    def toggle_auto_update(self):
        """Toggle automatic updates on/off"""
        config = self.get_config()
        config["auto_update"] = not config.get("auto_update", True)
        self.save_config(config)
        return config["auto_update"]
