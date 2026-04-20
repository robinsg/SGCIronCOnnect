# framework/core/base_screen.py

from typing import Dict, Any, List, Optional
import yaml
from .terminal_driver import TmuxDriver
from .exceptions import ScreenMismatchError, InputInhibitedError
from .handler_registry import HandlerRegistry

class BaseScreen:
    """
    Base class for all screen objects. Implements the Screen State Machine.
    """
    
    def __init__(self, driver: TmuxDriver, config_path: str, 
                 screen_key: Optional[str] = None):
        self.driver = driver
        with open(config_path, 'r') as f:
            full_config = yaml.safe_load(f)
        
        if screen_key:
            self.config = full_config.get(screen_key)
            if not self.config:
                raise KeyError(f"Screen key '{screen_key}' not found in {config_path}")
        else:
            self.config = full_config
        
        self.screen_name = self.config.get('screen_name', screen_key or "Unnamed Screen")
        self.indicators = self.config.get('indicators', [])
        self.fields = self.config.get('fields', {})
        self.handlers_config = self.config.get('handlers', [])
        self.handler_results: Dict[str, Any] = {}

    def verify(self):
        """
        Mandatory check with handler support.
        """
        if not self.matches():
            # For backward compatibility and strict enforcement in verify()
            # We re-run logic or just raise a generic error if matches() logic is moved
            # Let's keep the logic here for simplicity but allow a non-throwing version
            self._do_verify(raise_error=True)
        else:
            self._do_verify(raise_error=False)

    def matches(self) -> bool:
        """
        Returns True if the current terminal buffer matches the screen indicators.
        """
        try:
            self._do_verify(raise_error=True)
            return True
        except ScreenMismatchError:
            return False

    def _do_verify(self, raise_error: bool = True):
        buffer = self.driver.get_buffer()
        buffer_text = "\n".join(buffer)
        
        # 1. Indicator verification
        for indicator in self.indicators:
            if isinstance(indicator, str):
                if indicator not in buffer_text:
                    if raise_error:
                        raise ScreenMismatchError(
                            f"Expected global indicator '{indicator}' not found for screen '{self.screen_name}'"
                        )
                    return False
            elif isinstance(indicator, dict):
                text = indicator.get('text', '')
                try:
                    row = int(indicator.get('row', 0))
                    col = int(indicator.get('col', 0))
                except (ValueError, TypeError):
                    continue

                if not text or row <= 0 or col <= 0:
                    continue 

                target_row = row - 1
                target_col = col - 1

                if target_row >= len(buffer):
                    if raise_error:
                        raise ScreenMismatchError(f"Row {row} is out of bounds.")
                    return False

                width, _ = self.driver.get_dimensions()
                row_content = buffer[target_row].ljust(width) 
                actual_text = row_content[target_col:target_col + len(text)]

                if actual_text != text:
                    if raise_error:
                        raise ScreenMismatchError(
                            f"Positional mismatch at R{row}C{col}: Expected '{text}', found '{actual_text}'"
                        )
                    return False
        
        # 2. Input inhibited check
        if self.driver.is_input_inhibited():
            if raise_error:
                raise InputInhibitedError(f"Terminal is inhibited on screen '{self.screen_name}'")
            return False
        
        # 3. Execute handlers
        dimensions = self.driver.get_dimensions()
        results = {}
        
        for handler_config in self.handlers_config:
            handler_type = handler_config.get('type')
            handler_name = handler_config.get('name', handler_type)
            required = handler_config.get('required', False)
            
            try:
                result = HandlerRegistry.execute_handler(
                    handler_type, buffer, handler_config, dimensions
                )
                results[handler_name] = result
                
                if required and not result.get('success', False):
                    if raise_error:
                        raise ScreenMismatchError(
                            f"Required handler '{handler_name}' failed: {result.get('error', 'Unknown error')}"
                        )
                    return False
            except Exception as e:
                if required:
                    if raise_error:
                        raise ScreenMismatchError(f"Handler '{handler_name}' error: {str(e)}")
                    return False
                else:
                    results[handler_name] = {'success': False, 'error': str(e)}
        
        # Only store results if we verified successfully
        self.handler_results = results
        return True

    def fill_field(self, field_name: str, value: str, tabs_override: Optional[int] = None):
        """Fills a field based on its YAML definition."""
        if field_name not in self.fields:
            raise KeyError(f"Field '{field_name}' not defined in {self.screen_name}")
        
        field_cfg = self.fields[field_name]
        tabs = tabs_override if tabs_override is not None else field_cfg.get('tabs_to_reach', 0)
        for _ in range(tabs):
            self.driver.send_keys("Tab", enter=False)
            
        self.driver.send_keys(value, enter=False)

    def press_key(self, key: str):
        self.driver.send_keys(key)

    def get_handler_result(self, handler_name: str) -> Optional[Dict[str, Any]]:
        return self.handler_results.get(handler_name)

    def get_all_handler_results(self) -> Dict[str, Any]:
        return self.handler_results.copy()
