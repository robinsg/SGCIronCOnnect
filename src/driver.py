import libtmux
import time
import logging
from typing import List, Tuple

# --- Custom Exceptions ---
class TerminalError(Exception):
    """Base exception for terminal interactions."""
    pass

class ScreenMismatchError(TerminalError):
    """Raised when the screen does not match expectations."""
    pass

class TerminalTimeoutError(TerminalError):
    """Raised on timeouts."""
    pass

class ConnectionLostError(TerminalError):
    """Raised when the connection is lost."""
    pass


class TmuxDriver:
    """
    Manages the tn5250 terminal session within a tmux pane.
    """
    def __init__(self, session_name: str, host: str, ssl: bool = False, tn5250_map: str = "285"):
        self.server = libtmux.Server()
        self.session_name = session_name
        self.host = host
        self.ssl = ssl
        self.tn5250_map = tn5250_map
        self.session: libtmux.Session
        self.pane: libtmux.Pane

        session = self.server.find_where({"session_name": self.session_name})
        if session:
            self.session = session
            self.pane = self.session.attached_pane
            logging.info(f"Attached to existing tmux session: {self.session_name}")
        else:
            self.session = self.server.new_session(session_name=self.session_name, attach=False)
            self.pane = self.session.attached_pane
            logging.info(f"Created new tmux session: {self.session_name}")
            self._start_tn5250()

    def _start_tn5250(self) -> None:
        """Constructs and sends the tn5250 connection command."""
        ssl_option = "-ssl" if self.ssl else ""
        command = f"tn5250 {self.host} {ssl_option} map={self.tn5250_map}"
        logging.info(f"Starting tn5250 with command: {command}")
        self.pane.send_keys(command, enter=True)
        time.sleep(2)

    def send_keys(self, keys: str, enter: bool = False, suppress_log: bool = False) -> None:
        """Sends keystrokes to the pane."""
        if not suppress_log:
            logging.info(f"Sending keys: '{keys}' (Enter: {enter})")
        self.pane.send_keys(keys, enter=enter)

    def capture_screen(self) -> str:
        """Captures and returns the visible screen content as a single string."""
        return "\n".join(self.pane.capture_pane())

    def save_screen_capture(self, filepath: str) -> None:
        """Saves the current screen buffer to a file."""
        screen_content = self.capture_screen()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(screen_content)
        logging.info(f"Screen capture saved to {filepath}")

    def close(self) -> None:
        """Kills the tmux session and cleans up."""
        if self.session:
            logging.info(f"Killing tmux session: {self.session_name}")
            self.session.kill_session()
