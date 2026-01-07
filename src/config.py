class WiFiConfig:
    """Configuration constants for WiFi connection and AP mode."""
    # Maximum number of connection attempts before entering FAIL state
    MAX_RETRIES = 5
    
    # Time (seconds) to wait for connection per attempt
    CONNECT_TIMEOUT = 15
    
    # Time (seconds) to wait between retries in CONNECTING state
    RETRY_DELAY = 2
    
    # Time (seconds) to wait in FAIL state before trying again (Auto-recovery)
    FAIL_RECOVERY_DELAY = 30
    
    # Interval (seconds) to check connection health in CONNECTED state
    HEALTH_CHECK_INTERVAL = 2
    
    # AP Mode Settings for Provisioning
    AP_SSID = "Picore-W-Setup"
    AP_PASSWORD = "password123" # Default secure password
    AP_IP = "192.168.4.1"
