# framework/core/handlers/text_block_search.py

from typing import Dict, List, Any
from ..screen_handlers import ScreenHandler
from ..exceptions import HandlerConfigMissingError, HandlerValidationError

class TextBlockSearchHandler(ScreenHandler):
    """
    Search for text within a bounded rectangular region on the 5250 screen.
    """
    
    HANDLER_TYPE = "text_block_search"
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate handler configuration."""
        required_fields = ['search_term', 'start_row', 'end_row']
        for field in required_fields:
            if field not in config:
                raise HandlerConfigMissingError(
                    f"Missing required field for text_block_search: {field}"
                )
        
        if not isinstance(config['search_term'], str) or not config['search_term']:
            raise HandlerValidationError("search_term must be non-empty string")
        
        try:
            start_row = int(config['start_row'])
            end_row = int(config['end_row'])
        except (ValueError, TypeError):
            raise HandlerValidationError("start_row and end_row must be integers")
        
        if start_row < 1:
            raise HandlerValidationError("start_row must be >= 1")
        
        if end_row < start_row:
            raise HandlerValidationError("end_row must be >= start_row")
        
        return True
    
    def execute(self, buffer: List[str], config: Dict[str, Any], 
                dimensions: tuple[int, int]) -> Dict[str, Any]:
        """Execute text search within defined block."""
        search_term = config['search_term']
        start_row = int(config['start_row']) - 1
        end_row = int(config['end_row'])
        start_col = int(config.get('start_col', 1)) - 1
        end_col = int(config.get('end_col', 80))
        case_sensitive = config.get('case_sensitive', False)
        
        try:
            for row_idx in range(start_row, min(end_row, len(buffer))):
                row_content = buffer[row_idx]
                section = row_content[start_col:end_col]
                
                if not case_sensitive:
                    search_lower = search_term.lower()
                    col_offset = section.lower().find(search_lower)
                else:
                    col_offset = section.find(search_term)
                
                if col_offset >= 0:
                    return {
                        'success': True,
                        'found': True,
                        'row': row_idx + 1,
                        'col': start_col + col_offset + 1,
                        'matched_text': search_term,
                        'context': row_content.rstrip(),
                        'context_row': row_content
                    }
            
            return {
                'success': True,
                'found': False,
                'search_term': search_term
            }
        except Exception as e:
            return {'success': False, 'found': False, 'error': str(e)}
