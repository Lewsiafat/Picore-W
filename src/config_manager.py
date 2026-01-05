import json
import os

CONFIG_FILE = "wifi_config.json"

class ConfigManager:
    """
    Manages persistent storage of configuration data using a JSON file on Flash.
    """
    
    @staticmethod
    def load_config():
        """
        Load configuration from the JSON file.
        Returns a dictionary with config data, or None if file doesn't exist or is invalid.
        """
        try:
            # Check if file exists
            try:
                os.stat(CONFIG_FILE)
            except OSError:
                print("ConfigManager: Config file not found.")
                return None
                
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                print(f"ConfigManager: Loaded config: {config}")
                return config
                
        except (ValueError, OSError) as e:
            print(f"ConfigManager: Error loading config: {e}")
            return None

    @staticmethod
    def save_config(ssid, password):
        """
        Save WiFi credentials to the JSON file.
        """
        config_data = {
            "ssid": ssid,
            "password": password
        }
        
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config_data, f)
                print(f"ConfigManager: Saved config for SSID: {ssid}")
            return True
        except OSError as e:
            print(f"ConfigManager: Error saving config: {e}")
            return False

    @staticmethod
    def delete_config():
        """
        Remove the configuration file (Factory Reset).
        """
        try:
            os.remove(CONFIG_FILE)
            print("ConfigManager: Config file deleted.")
            return True
        except OSError:
            print("ConfigManager: No config file to delete.")
            return False
