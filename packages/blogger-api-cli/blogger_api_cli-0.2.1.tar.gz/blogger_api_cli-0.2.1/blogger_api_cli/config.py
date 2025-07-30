import json
import os
import sys


class BloggerConfig:
    """
    A class to manage Blogger API configuration.
    Loads configuration from a JSON file and provides access to the settings.
    """

    def __init__(self, config_path=None):
        """
        Initialize the configuration by loading settings from a JSON file.
        
        Args:
            config_path (str, optional): Path to the configuration file.
                                         If not provided, will look for config.json in the same directory.
        """
        # Default configuration
        self._config = {
            "api_key": "",
            "blog_id": "",
            "base_url": "https://www.googleapis.com/blogger/v3",
            "user_id": "self",
            "blog_url": ""
        }

        # Determine the path to the config file
        if config_path is None:
            # Get the directory where the script is located
            if getattr(sys, 'frozen', False):
                # We're running in a bundle (PyInstaller)
                base_dir = os.path.dirname(sys.executable)
            else:
                # We're running in a normal Python environment
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            config_path = os.path.join(base_dir, 'config.json')
        
        # Load configuration from the JSON file if it exists
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                self._config.update(loaded_config)
        except FileNotFoundError:
            print(f"Warning: Configuration file not found at {config_path}")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in configuration file {config_path}")
        
        # Set API key in environment variable for modules that use it directly
        if self._config["api_key"]:
            os.environ["BLOGGER_API_KEY"] = self._config["api_key"]
    
    @property
    def api_key(self):
        return self._config["api_key"]
    
    @property
    def blog_id(self):
        return self._config["blog_id"]
    
    @property
    def base_url(self):
        return self._config["base_url"]
    
    @property
    def user_id(self):
        return self._config["user_id"]
    
    @property
    def blog_url(self):
        return self._config["blog_url"]
