# framework/screens/login_screen.py

from ..core.base_screen import BaseScreen
from ..core.terminal_driver import TmuxDriver

class LoginScreen(BaseScreen):
    """
    Sign On screen implementation.
    """
    def __init__(self, driver: TmuxDriver):
        # Path to YAML config
        config_path = "framework/config/login_screen.yaml"
        super().__init__(driver, config_path, "login_screen")

    def login(self, username: str, password: str):
        """Helper method specifically for login logic."""
        self.verify()
        self.fill_field("user", username)
        self.fill_field("password", password)
        self.press_key("Enter")
