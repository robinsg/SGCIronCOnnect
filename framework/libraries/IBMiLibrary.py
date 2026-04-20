# framework/libraries/IBMiLibrary.py

from typing import Optional, Dict, Any
from robot.api import logger
from ..core.terminal_driver import TmuxDriver
from ..core.base_screen import BaseScreen

class IBMiLibrary:
    """
    Robot Framework Library for IBM i (TN5250) automation.
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.driver: Optional[TmuxDriver] = None
        self.current_screen: Optional[BaseScreen] = None

    def initialize_connection(self, host: str, port: int = 23, ssl: bool = False):
        """Initialises the tmux/tn5250 session."""
        self.driver = TmuxDriver(host=host, port=port, ssl=ssl)
        self.driver.start_session()
        logger.info(f"Initialised connection to {host}:{port} (SSL={ssl})")

    def verify_and_interact_with_screen(self, config_path: str, screen_key: str, data: Optional[Dict] = None):
        """Verifies screen and optionally fills fields."""
        if not self.driver:
            raise RuntimeError("Driver not initialised.")
        
        screen = BaseScreen(self.driver, config_path, screen_key)
        screen.verify()
        self.current_screen = screen
        
        if data:
            for field, value in data.items():
                screen.fill_field(field, value)
        
        logger.info(f"Verified and interacted with screen: {screen.screen_name}")

    def get_screen_handler_result(self, handler_name: str) -> Dict:
        """Retrieves result from last executed screen handler."""
        if not self.current_screen:
            raise RuntimeError("No screen context.")
        
        result = self.current_screen.get_handler_result(handler_name)
        if result is None:
            raise KeyError(f"Handler result '{handler_name}' not found")
        
        return result

    def close_connection(self):
        """Closes the tmux session."""
        if self.driver:
            self.driver.stop_session()
            self.driver = None
