# framework/core/terminal_driver.py

import os
import time
from typing import List, Tuple, Optional
import libtmux
from .exceptions import TerminalTimeoutError, ConnectionLostError

class TmuxDriver:
    """
    Driver for managing a tn5250 session within a tmux session using libtmux.
    """

    def __init__(self, 
                 session_name: str = "tn5250_session", 
                 host_name: str = "localhost", 
                 host_port: int = 23, 
                 code_page: int = 285,
                 enable_tls: bool = False,
                 lu_name: str = ""):
        self.session_name = session_name
        self.host_name = host_name
        self.host_port = host_port
        self.code_page = code_page
        self.enable_tls = enable_tls
        self.lu_name = lu_name
        self.server = libtmux.Server()
        self.session: Optional[libtmux.Session] = None
        self.pane: Optional[libtmux.Pane] = None

    def start_session(self):
        """
        Launches the tn5250 session inside a tmux session.
        """
        if self.server.has_session(self.session_name):
            self.server.kill_session(self.session_name)

        # Build tn5250 command
        ssl_prefix = "ssl:" if self.enable_tls else ""
        lu_arg = f"luname={self.lu_name} " if self.lu_name else ""
        tn_cmd = f"tn5250 {lu_arg}{ssl_prefix}{self.host_name}:{self.host_port} map={self.code_page}"
        
        self.session = self.server.new_session(
            session_name=self.session_name,
            window_command=tn_cmd
        )
        self.pane = self.session.active_window.active_pane
        time.sleep(2)  # Wait for initial connect

    def send_keys(self, keys: str, enter: bool = True):
        """
        Sends raw keys or control keys to the tmux pane.
        """
        if not self.pane:
            raise ConnectionLostError("No active tmux pane found.")
        
        if enter:
            self.pane.send_keys(keys, enter=True)
        else:
            self.pane.send_keys(keys, enter=False)

    def get_buffer(self) -> List[str]:
        """
        Captures the current visual buffer of the tmux pane.
        """
        if not self.pane:
            raise ConnectionLostError("No active tmux pane found.")
        return self.pane.cmd('capture-pane', '-p').stdout

    def get_dimensions(self) -> Tuple[int, int]:
        """
        Returns the (width, height) of the terminal pane.
        Default 5250 is usually 80x24.
        """
        if not self.pane:
            return 80, 24
        return int(self.pane.display_message("#{pane_width}")[0]), \
               int(self.pane.display_message("#{pane_height}")[0])

    def is_input_inhibited(self) -> bool:
        """
        Heuristic to detect 'Input Inhibited' state.
        On many 5250 screens, this is indicated in the status line (bottom).
        """
        buffer = self.get_buffer()
        if not buffer:
            return False
        # Common pattern: "X" or "II" in the status line area
        bottom_line = buffer[-1]
        return " X " in bottom_line or " II " in bottom_line

    def stop_session(self):
        """
        Terminates the tmux session.
        """
        if self.server.has_session(self.session_name):
            self.server.kill_session(self.session_name)
