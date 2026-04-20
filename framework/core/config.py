# framework/core/config.py

import os
from typing import Dict, Any

class IBMiConfig:
    """Configuration wrapper for IBM i connection settings."""
    
    def __init__(self, host: str, port: int = 23, ssl: bool = False):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.map_value = 285
