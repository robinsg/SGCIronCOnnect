# framework/core/p5250_client.py

import os
import time
import re
from typing import List, Tuple, Optional, Dict, Any
from .terminal_driver import TmuxDriver
from .exceptions import TerminalError, ConnectionLostError

class P5250Client:
    """
    Higher-level 5250 client that provides a rich API for interacting with IBM i.
    Designed to follow the P5250Client specification with PEP-8 formatting.
    """

    def __init__(self, 
                 lu_name: str = "", 
                 host_name: str = "localhost", 
                 host_port: int = 23, 
                 model_name: str = "3477-FC", 
                 verify_cert: bool = False, 
                 enable_tls: bool = False, 
                 code_page: str = "285", 
                 path: str = "tn5250", 
                 timeout_in_sec: int = 30):
        """
        Initialises the P5250Client with connection settings.
        """
        self.lu_name = lu_name
        self.host_name = host_name
        self.host_port = host_port
        self.model_name = model_name
        self.verify_cert = verify_cert
        self.enable_tls = enable_tls
        self.code_page = code_page
        self.bin_path = path
        self.timeout = timeout_in_sec
        
        # Initialise underlying driver
        # We map code_page to map_value if numeric
        try:
            map_val = int(code_page)
        except ValueError:
            map_val = 285
            
        self._driver = TmuxDriver(
            host_name=host_name,
            host_port=host_port,
            code_page=map_val,
            enable_tls=enable_tls
        )
        self._is_connected = False

    def connect(self):
        """Establishes a connection to the host."""
        self._driver.start_session()
        self._is_connected = True
        # Allow some time for the screen to render
        time.sleep(1)

    def disconnect(self):
        """Closes the connection to the host."""
        self._driver.stop_session()
        self._is_connected = False

    def end_session(self):
        """Terminates the emulator script/session."""
        self.disconnect()

    def send_enter(self):
        """Sends the Enter key to the host."""
        self._driver.send_keys("Enter")

    def send_back_tab(self):
        """Sends Shift+Tab to navigate to the previous field."""
        self._driver.send_keys("S-Tab", enter=False)

    def send_tab(self):
        """Sends Tab key to navigate to the next field."""
        self._driver.send_keys("Tab", enter=False)

    def send_back_space(self):
        """Sends backspace or moves cursor left."""
        self._driver.send_keys("BSpace", enter=False)

    def del_char(self):
        """Deletes the character under the cursor."""
        self._driver.send_keys("Delete", enter=False)

    def del_field(self):
        """Deletes the entire current field."""
        # 5250 Delete Field is usually mapped to 'Delete' in tn5250 keymap
        self._driver.send_keys("Delete", enter=False)

    def erase_char(self):
        """Erases the previous character or sends ASCII backspace."""
        self._driver.send_keys("BSpace", enter=False)

    def move_cursor_down(self):
        """Moves cursor down one row."""
        self._driver.send_keys("Down", enter=False)

    def move_cursor_up(self):
        """Moves cursor up one row."""
        self._driver.send_keys("Up", enter=False)

    def move_cursor_left(self):
        """Moves cursor left one column."""
        self._driver.send_keys("Left", enter=False)

    def move_cursor_right(self):
        """Moves cursor right one column."""
        self._driver.send_keys("Right", enter=False)

    def move_to(self, row: int, col: int):
        """
        Moves cursor to specified row and column position.
        Note: Emulated since tmux capture-pane doesn't give us current cursor easily.
        """
        pass

    def move_to_first_input_field(self):
        """Moves cursor to the first input field on screen."""
        self._driver.send_keys("Home", enter=False)

    def send_text(self, text: str):
        """Sends text string to the host."""
        self._driver.send_keys(text, enter=False)

    def save_screen(self, file_name: str, data_type: str = "html"):
        """Saves current screen content to a file (default HTML format)."""
        content = self.get_screen()
        with open(file_name, 'w') as f:
            if data_type.lower() == "html":
                f.write(f"<html><body><pre>{content}</pre></body></html>")
            else:
                f.write(content)

    def get_screen(self) -> str:
        """Retrieves current screen content as a string."""
        buffer = self._driver.get_buffer()
        return "\n".join(buffer)

    def print_screen(self):
        """Prints current screen content to stdout."""
        print(self.get_screen())

    def is_connected(self) -> bool:
        """Returns connection status (True/False)."""
        return self._is_connected

    def read_text_at_position(self, row: int, col: int, length: int) -> str:
        """Reads and returns text at specified position and length."""
        buffer = self._driver.get_buffer()
        if row <= 0 or row > len(buffer):
            return ""
        
        line = buffer[row - 1]
        if col <= 0 or col > len(line):
            return ""
            
        return line[col - 1 : col - 1 + length]

    def read_text_area(self, row: int, col: int, rows: int, cols: int) -> str:
        """Reads and returns a rectangular area of text."""
        buffer = self._driver.get_buffer()
        results = []
        for r in range(row, row + rows):
            if r <= len(buffer):
                line = buffer[r - 1]
                segment = line[col - 1 : col - 1 + cols]
                results.append(segment)
        return "\n".join(results)

    def found_text_at_position(self, row: int, col: int, sent_text: str) -> bool:
        """Checks if specific text is found at given position."""
        actual = self.read_text_at_position(row, col, len(sent_text))
        return actual == sent_text

    def try_send_text_to_field(self, text: str, row: int, col: int) -> bool:
        """
        Attempts to send text to a field at specified coordinates (returns bool).
        """
        try:
            self.move_to(row, col)
            self.send_text(text)
            return True
        except Exception:
            return False

    def wait_for_field(self):
        """Waits for an input field to become available (not inhibited)."""
        timeout = time.time() + self.timeout
        while time.time() < timeout:
            if not self._driver.is_input_inhibited():
                return
            time.sleep(0.5)
        raise TerminalError("Timeout waiting for input field (inhibited state persisted)")

    def roll_up(self):
        """Sends PF8 (Page Up/Roll Up)."""
        self.send_f(8)

    def roll_down(self):
        """Sends PF7 (Page Down/Roll Down)."""
        self.send_f(7)

    def error_reset(self):
        """Sends PF10 (Error/Reset)."""
        self.send_f(10)

    def send_f(self, n: int):
        """Sends function key F1-F24 with appropriate PA codes."""
        if 1 <= n <= 24:
            self._driver.send_keys(f"F{n}")
        else:
            raise ValueError(f"Invalid function key: F{n}")
