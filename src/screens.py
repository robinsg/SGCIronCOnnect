import yaml
import time
import logging
from pathlib import Path
from src.driver import TmuxDriver, ScreenMismatchError, TerminalTimeoutError

class BaseScreen:
    """
    Represents a single screen in the TN5250 terminal.
    """
    def __init__(self, driver: TmuxDriver):
        self.driver = driver
        self.screen_name: str = ""
        self.identifiers: list[str] = []
        self.fields: dict = {}
        self.wait_conditions: dict = {}

    def load_screen_definition(self, screen_name: str) -> None:
        """Loads screen definition from a YAML file."""
        config_path = Path(__file__).parent.parent / "config" / "screens" / f"{screen_name.lower()}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Screen definition not found: {config_path}")

        with open(config_path, 'r', encoding="utf-8") as f:
            data = yaml.safe_load(f)
            self.screen_name = data.get("screen_name", "")
            self.identifiers = data.get("identifiers", [])
            self.fields = data.get("fields", {})
            self.wait_conditions = data.get("wait_conditions", {})

    def wait_for_screen(self, timeout: int = 15) -> bool:
        """
        Waits for the screen to appear and be ready for input.
        """
        logging.info(f"Waiting for screen: '{self.screen_name}'")
        start_time = time.time()
        while time.time() - start_time < timeout:
            screen_text = self.driver.capture_screen()

            if "Input Inhibited" in screen_text:
                time.sleep(0.5)
                continue

            if all(identifier in screen_text for identifier in self.identifiers):
                logging.info(f"Successfully identified screen: '{self.screen_name}'")
                return True

            time.sleep(0.5)

        debug_filepath = f"error_{self.screen_name}_{int(time.time())}.txt"
        self.driver.save_screen_capture(debug_filepath)
        raise TerminalTimeoutError(
            f"Timeout waiting for screen '{self.screen_name}'. "
            f"Debug capture saved to {debug_filepath}"
        )

    def is_on_screen(self) -> bool:
        """Checks if the current screen matches the definition without waiting."""
        screen_text = self.driver.capture_screen()
        return all(identifier in screen_text for identifier in self.identifiers)


class LoginScreen(BaseScreen):
    """
    Represents the IBM i Sign-On screen.
    """
    def __init__(self, driver: TmuxDriver):
        super().__init__(driver)
        self.load_screen_definition("login")

    def login(self, user: str, password: str) -> None:
        """Performs the login action."""
        if not self.is_on_screen():
            raise ScreenMismatchError(f"Cannot perform login. Not on the '{self.screen_name}' screen.")

        self.wait_for_screen()
        
        logging.info(f"Entering username: {user}")
        self.driver.send_keys(user)
        self.driver.send_keys("[tab]")
        
        logging.info("Entering password.")
        self.driver.send_keys(password, enter=True, suppress_log=True)
