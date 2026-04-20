# framework/core/handler_registry.py

from typing import Dict, List, Any, Optional
from .screen_handlers import ScreenHandler

class HandlerRegistry:
    """
    Central registry for all screen handlers.
    """
    
    _handlers: Dict[str, type] = {}
    _initialized: bool = False
    
    @classmethod
    def initialize(cls):
        """Register all built-in handlers."""
        if cls._initialized:
            return
        
        from .handlers.text_block_search import TextBlockSearchHandler
        from .handlers.extract_number import ExtractNumberHandler
        
        cls.register("text_block_search", TextBlockSearchHandler)
        cls.register("extract_number", ExtractNumberHandler)
        cls._initialized = True
    
    @classmethod
    def register(cls, handler_type: str, handler_class: type):
        """Register a new handler."""
        cls._handlers[handler_type] = handler_class
    
    @classmethod
    def get(cls, handler_type: str) -> type:
        """Retrieve handler class by type."""
        cls.initialize()
        return cls._handlers.get(handler_type)
    
    @classmethod
    def execute_handler(cls, 
                       handler_type: str, 
                       buffer: List[str], 
                       config: Dict[str, Any], 
                       dimensions: tuple[int, int]) -> Dict[str, Any]:
        """Execute handler and return result."""
        handler_class = cls.get(handler_type)
        if not handler_class:
            raise ValueError(f"Unknown handler type: {handler_type}")
        
        handler = handler_class()
        handler.validate_config(config)
        return handler.execute(buffer, config, dimensions)
