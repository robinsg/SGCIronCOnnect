# framework/screens/hmc_console_screen.py

from ..core.base_screen import BaseScreen
from ..core.terminal_driver import TmuxDriver

class HMCConsoleScreen(BaseScreen):
    """
    Handles HMC Console screen navigation and interactions.
    """

    def __init__(self, driver: TmuxDriver):
        # We'll use a specific config for HMC if needed,
        # but for now we'll inherit and allow dynamic verification.
        self.config_path = "framework/config/hmc_screens.yaml"
        super().__init__(driver, self.config_path, "hmc_login")

    def login(self, username, password):
        """Perform HMC login."""
        self.verify() # Verify we are on hmc_login
        self.fill_field("user", username)
        self.fill_field("password", password)
        self.driver.send_keys("Enter")

    def select_partition(self, partition_name):
        """Select partition from HMC partition selection screen."""
        # Switch context to partition selection
        self.config = self._load_config("hmc_partition_selection")
        self.verify()
        # Logic to find and select partition...
        # For simplicity, let's assume we can type the partition name if there's a filter or selection field
        self.fill_field("selection", partition_name)
        self.driver.send_keys("Enter")

    def _load_config(self, screen_key):
        import yaml
        with open(self.config_path, 'r') as f:
            full_config = yaml.safe_load(f)
        return full_config.get(screen_key)
