# framework/core/screen_handlers.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class ScreenHandler(ABC):
    """
    Base class for all 5250 screen handling operations.
    """
    
    HANDLER_TYPE: str = "base"
    
    @abstractmethod
    def execute(self, 
                buffer: List[str], 
                config: Dict[str, Any], 
                dimensions: tuple[int, int]) -> Dict[str, Any]:
        """
        Execute the handler operation.
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate handler configuration before execution.
        """
        pass
