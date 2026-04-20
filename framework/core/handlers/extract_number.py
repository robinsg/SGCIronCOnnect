# framework/core/handlers/extract_number.py

import re
from typing import Dict, List, Any, Optional
from ..screen_handlers import ScreenHandler
from ..exceptions import HandlerConfigMissingError, HandlerValidationError

class ExtractNumberHandler(ScreenHandler):
    """
    Extract and parse numeric values from a specific row/column position.
    """
    
    HANDLER_TYPE = "extract_number"
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        required_fields = ['row', 'col', 'length']
        for field in required_fields:
            if field not in config:
                raise HandlerConfigMissingError(
                    f"Missing required field for extract_number: {field}"
                )
        
        try:
            int(config['row'])
            int(config['col'])
            int(config['length'])
        except (ValueError, TypeError):
            raise HandlerValidationError("row, col, and length must be integers")
        return True
    
    def execute(self, buffer: List[str], config: Dict[str, Any], 
                dimensions: tuple[int, int]) -> Dict[str, Any]:
        row = int(config['row']) - 1
        col = int(config['col']) - 1
        length = int(config['length'])
        decimal_places = int(config.get('decimal_places', 2))
        trim_spaces = config.get('trim_spaces', True)
        sign_position = config.get('sign_position', 'prefix')
        thousands_separator = config.get('thousands_separator', '')
        
        try:
            if row >= len(buffer):
                return {'success': False, 'error': "Row out of bounds"}
            
            row_content = buffer[row]
            raw_text = row_content[col:col + length]
            
            if trim_spaces:
                raw_text = raw_text.strip()
            
            parsed_value, is_negative, parse_error = self._parse_number(
                raw_text, decimal_places, sign_position, thousands_separator
            )
            
            if parse_error:
                return {'success': False, 'raw_text': raw_text, 'error': parse_error}
            
            return {
                'success': True,
                'value': parsed_value,
                'raw_text': raw_text,
                'formatted': f"{parsed_value:.{decimal_places}f}",
                'is_negative': is_negative
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _parse_number(self, text: str, decimal_places: int, 
                     sign_position: str, thousands_sep: str) -> tuple[float, bool, Optional[str]]:
        if not text:
            return 0.0, False, "Empty text"
        
        is_negative = False
        working_text = text
        
        if sign_position == 'prefix':
            if working_text.startswith('-'):
                is_negative = True
                working_text = working_text[1:].strip()
        elif sign_position == 'suffix':
            if working_text.endswith('-'):
                is_negative = True
                working_text = working_text[:-1].strip()
        
        if thousands_sep:
            working_text = working_text.replace(thousands_sep, '')
        
        working_text = working_text.strip()
        
        try:
            value = float(working_text)
            if is_negative:
                value = -value
            return value, is_negative, None
        except ValueError:
            return 0.0, False, f"Unable to parse '{text}' as number"
