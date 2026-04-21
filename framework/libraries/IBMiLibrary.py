# framework/libraries/IBMiLibrary.py

import os
from typing import Optional, Dict, Any
from robot.api import logger
from ..core.p5250_client import P5250Client
from ..core.base_screen import BaseScreen

class IBMiLibrary:
    """
    Robot Framework Library for IBM i (TN5250) automation using P5250Client.
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.client: Optional[P5250Client] = None
        self.current_screen: Optional[BaseScreen] = None

    def initialize_connection(self, host: Optional[str] = None, 
                              port: Optional[int] = None, 
                              ssl: Optional[bool] = None, 
                              model: Optional[str] = None, 
                              lu_name: Optional[str] = None, 
                              code_page: Optional[str] = None):
        """
        Initialises the P5250Client and establishes a connection.
        If parameters are not provided, it falls back to environment variables or defaults.
        """
        # Resolve SSL first as it affects port default
        if ssl is None:
            env_ssl = os.getenv("IBMI_SSL", "True")
            ssl = env_ssl.lower() in ("true", "1", "yes")

        # Resolve other parameters from environment or defaults
        host = host or os.getenv("IBMI_HOST", "localhost")
        
        if port is None:
            env_port = os.getenv("IBMI_PORT")
            if env_port:
                port = int(env_port)
            else:
                port = 992 if ssl else 23
        
        model = model or os.getenv("IBMI_MODEL", "3477-FC")
        lu_name = lu_name or os.getenv("IBMI_LU_NAME", "")
        code_page = code_page or os.getenv("IBMI_MAP", "285")

        self.client = P5250Client(
            host_name=host, 
            host_port=port, 
            enable_tls=ssl, 
            model_name=model, 
            lu_name=lu_name, 
            code_page=code_page
        )
        self.client.connect()
        logger.info(f"Initialised P5250Client connection to {host}:{port} (SSL={ssl})")

    def verify_screen(self, config_path: str, screen_key: str):
        """Verifies the current screen against its YAML definition."""
        if not self.client:
            raise RuntimeError("Client not initialised.")
        
        # BaseScreen needs the driver (TmuxDriver) which is internal to P5250Client
        screen = BaseScreen(self.client._driver, config_path, screen_key)
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
        if not self.client:
            raise RuntimeError("Client not initialised.")
        
        self.client._driver.send_keys(key_name, enter=True)
        logger.info(f"Pressed control key: {key_name}")

    def bypass_optional_screen(self, config_path: str, screen_key: str, control_key: str = "Enter"):
        """
        Checks if an optional screen is present; if so, sends the control key to bypass it.
        """
        if not self.client:
            raise RuntimeError("Client not initialised.")
        
        screen = BaseScreen(self.client._driver, config_path, screen_key)
        if screen.matches():
            logger.info(f"Optional screen '{screen_key}' detected. Bypassing with '{control_key}'...")
            self.client._driver.send_keys(control_key, enter=True)
        else:
            logger.info(f"Optional screen '{screen_key}' not detected. Continuing...")

    def handle_optional_signon_info(self):
        """Specific keyword to handle the IBM i Sign-on Information screen."""
        config = "framework/config/signon_info_screen.yaml"
        self.bypass_optional_screen(config, "signon_info", "Enter")

    def get_handler_result(self, handler_name: str) -> Dict:
        """Retrieves result from last executed screen handler."""
        if not self.current_screen:
            raise RuntimeError("No screen context.")
        
        result = self.current_screen.get_handler_result(handler_name)
        if result is None:
            raise KeyError(f"Handler result '{handler_name}' not found")
        
        return result

    def close_connection(self):
        """Terminates the P5250Client session."""
        if self.client:
            self.client.disconnect()
            self.client = None
            logger.info("Connection closed.")

    # --- P5250Client Wrapper Keywords ---

    def send_enter(self):
        """Sends the Enter key to the host."""
        self.client.send_enter()

    def send_back_tab(self):
        """Sends Shift+Tab to navigate to the previous field."""
        self.client.send_back_tab()

    def send_tab(self):
        """Sends Tab key to navigate to the next field."""
        self.client.send_tab()

    def send_backspace(self):
        """Sends backspace or moves cursor left."""
        self.client.send_back_space()

    def del_char(self):
        """Deletes the character under the cursor."""
        self.client.del_char()

    def del_field(self):
        """Deletes the entire current field."""
        self.client.del_field()

    def erase_char(self):
        """Erases the previous character or sends ASCII backspace."""
        self.client.erase_char()

    def move_cursor_down(self):
        """Moves cursor down one row."""
        self.client.move_cursor_down()

    def move_cursor_up(self):
        """Moves cursor up one row."""
        self.client.move_cursor_up()

    def move_cursor_left(self):
        """Moves cursor left one column."""
        self.client.move_cursor_left()

    def move_cursor_right(self):
        """Moves cursor right one column."""
        self.client.move_cursor_right()

    def move_to(self, row: int, col: int):
        """Moves cursor to specified row and column position."""
        self.client.move_to(row, col)

    def move_to_first_input_field(self):
        """Moves cursor to the first input field on screen."""
        self.client.move_to_first_input_field()

    def send_text(self, text: str):
        """Sends text string to the host."""
        self.client.send_text(text)

    def save_screen(self, file_name: str, data_type: str = "html"):
        """Saves current screen content to a file."""
        self.client.save_screen(file_name, data_type)

    def get_screen(self) -> str:
        """Retrieves current screen content as a string."""
        return self.client.get_screen()

    def print_screen(self):
        """Prints current screen content to stdout."""
        self.client.print_screen()

    def is_connected(self) -> bool:
        """Returns connection status (True/False)."""
        return self.client.is_connected()

    def read_text_at_position(self, row: int, col: int, length: int) -> str:
        """Reads and returns text at specified position and length."""
        return self.client.read_text_at_position(row, col, length)

    def read_text_area(self, row: int, col: int, rows: int, cols: int) -> str:
        """Reads and returns a rectangular area of text."""
        return self.client.read_text_area(row, col, rows, cols)

    def found_text_at_position(self, row: int, col: int, sent_text: str) -> bool:
        """Checks if specific text is found at given position."""
        return self.client.found_text_at_position(row, col, sent_text)

    def try_send_text_to_field(self, text: str, row: int, col: int) -> bool:
        """Attempts to send text to a field at specified coordinates."""
        return self.client.try_send_text_to_field(text, row, col)

    def wait_for_field(self):
        """Waits for an input field to become available."""
        self.client.wait_for_field()

    def roll_up(self):
        """Sends PF8 (Page Up/Roll Up)."""
        self.client.roll_up()

    def roll_down(self):
        """Sends PF7 (Page Down/Roll Down)."""
        self.client.roll_down()

    def error_reset(self):
        """Sends PF10 (Error/Reset)."""
        self.client.error_reset()

    def send_f(self, n: int):
        """Sends function key F1-F24."""
        self.client.send_f(int(n))
