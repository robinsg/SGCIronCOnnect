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

    def verify_screen(self, config_path: str, screen_key: str):
        """Verifies the current screen against its YAML definition."""
        if not self.driver:
            raise RuntimeError("Driver not initialised.")
        
        screen = BaseScreen(self.driver, config_path, screen_key)
        screen.verify()
        self.current_screen = screen
        logger.info(f"Successfully verified screen: {screen.screen_name}")

    def type_text(self, field_name: str, value: str):
        """Types text into a defined field without sending Enter."""
        if not self.current_screen:
            raise RuntimeError("No active screen context. Call 'Verify Screen' first.")
        self.current_screen.fill_field(field_name, value)
        logger.info(f"Typed '{value}' into field '{field_name}'")

    def press_key(self, key_name: str):
        """Sends a control key like Enter, F3, F12, PgUp, PgDn, or FieldExit."""
        if not self.driver:
            raise RuntimeError("Driver not initialised.")
        
        # 'FieldExit' is often a combination or specific sequence in tn5250
        # Here we use the driver's send_keys mapping
        self.driver.send_keys(key_name, enter=True)
        logger.info(f"Pressed control key: {key_name}")

    def bypass_optional_screen(self, config_path: str, screen_key: str, control_key: str = "Enter"):
        """
        Checks if an optional screen is present; if so, sends the control key to bypass it.
        Does nothing if the screen is not detected.
        """
        if not self.driver:
            raise RuntimeError("Driver not initialised.")
        
        screen = BaseScreen(self.driver, config_path, screen_key)
        if screen.matches():
            logger.info(f"Optional screen '{screen_key}' detected. Bypassing with '{control_key}'...")
            self.driver.send_keys(control_key, enter=True)
        else:
            logger.info(f"Optional screen '{screen_key}' not detected. Continuing...")

    def handle_optional_signon_info(self):
        """
        Specific keyword to handle the IBM i Sign-on Information screen if it appears.
        """
        config = "framework/config/signon_info_screen.yaml"
        self.bypass_optional_screen(config, "signon_info", "Enter")

    def close_connection(self):
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
