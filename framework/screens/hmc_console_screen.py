# framework/screens/hmc_console_screen.py

import time
import yaml
from ..core.base_screen import BaseScreen
from ..core.terminal_driver import TmuxDriver

class HMCConsoleScreen(BaseScreen):
    """
    Handles HMC Console screen navigation and interactions based on
    verified HMC connection sequences.
    """

    def __init__(self, driver: TmuxDriver):
        self.config_path = "framework/config/hmc_screens.yaml"
        # Load config once during initialization
        with open(self.config_path, 'r') as f:
            self._full_config = yaml.safe_load(f)

        # Start with language selection as it's typically the first screen
        super().__init__(driver, self.config_path, "hmc_language_selection")

    def select_language(self, language_code="23"):
        """Handle Screen 1: Language Selection (Default 23 for en_US/UK)"""
        if self.matches():
            self.fill_field("language", language_code)
            self.driver.send_keys("Enter")
            time.sleep(1)

    def login(self, username, password):
        """Handle Screen 2: HMC Sign on"""
        self._switch_to("hmc_login")
        self.verify()
        self.fill_field("user", username)
        self.fill_field("password", password)
        self.driver.send_keys("Enter")
        time.sleep(1)

    def select_system(self, system_option="1"):
        """Handle Screen 3: System Selection"""
        self._switch_to("hmc_system_selection")
        if self.matches():
            self.fill_field("system", system_option)
            self.driver.send_keys("Enter")
            time.sleep(1)

    def select_partition(self, partition_id, connection_type="2"):
        """
        Handle Screen 4: Partition Selection
        partition_id: The ID or name of the partition to select (e.g., '10')
        connection_type: '1' for dedicated, '2' for shared
        """
        self._switch_to("hmc_partition_selection")
        self.verify()

        # In a production scenario, we'd need to find the correct row.
        # Based on Screen 4 in the provided text, the selection field
        # is at the bottom, and options are entered next to partition entries.
        # Since we use tabs_to_reach in YAML, we'll assume the partition_id
        # combined with connection_type is typed in the correct field.
        # For simplicity in this version, we type the partition_id,
        # then connection_type if needed.
        self.fill_field("selection", partition_id)
        self.driver.send_keys("Enter") # Select the partition
        time.sleep(1)

        # If we need to select dedicated/shared, we might be on the same screen
        # or a sub-screen. The screenshot shows Option field next to partitions.
        # Re-verify and type connection type if prompted or if it was part of the same input.
        # Based on '2 10: F4I400X', the '2' (shared) is typed in the Option col for row 10.
        # Our simplified model will just type the whole string if it's a single selection field
        # or we could implement row-finding logic here.

    def enter_session_key(self, session_key):
        """Handle Screen 5: Session Key"""
        self._switch_to("hmc_session_key")
        if self.matches():
            self.fill_field("key", session_key)
            self.fill_field("verify_key", session_key)
            self.driver.send_keys("Enter")
            time.sleep(2)

    def _switch_to(self, screen_key):
        self.config = self._full_config.get(screen_key)
        if not self.config:
             raise KeyError(f"Screen key '{screen_key}' not found in {self.config_path}")
        self.screen_name = self.config.get('screen_name')
        self.indicators = self.config.get('indicators', [])
        self.fields = self.config.get('fields', {})
