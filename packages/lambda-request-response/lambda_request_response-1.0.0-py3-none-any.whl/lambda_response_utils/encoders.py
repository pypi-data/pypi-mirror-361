import json
import logging
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from .exceptions import SerializationError

logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    """Enhanced JSON encoder that handles common Python types safely."""
    
    def default(self, obj: Any) -> Any:
        """Convert non-serializable objects to serializable format."""
        try:
            # Handle numeric types
            if isinstance(obj, Decimal):
                return float(obj)
            
            # Handle date/time types
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, date):
                return obj.isoformat()
            elif isinstance(obj, time):
                return obj.isoformat()
            
            # Handle UUID
            elif isinstance(obj, UUID):
                return str(obj)
            
            # Handle Enums
            elif isinstance(obj, Enum):
                return obj.value
            
            # Handle bytes
            elif isinstance(obj, bytes):
                try:
                    return obj.decode('utf-8')
                except UnicodeDecodeError:
                    return obj.hex()
            
            # Handle sets, frozensets, tuples
            elif isinstance(obj, (set, frozenset, tuple)):
                return list(obj)
            
            # Handle custom objects with __dict__
            elif hasattr(obj, '__dict__'):
                return {k: v for k, v in obj.__dict__.items() 
                       if not k.startswith('_')}
            
            # Handle objects with __slots__
            elif hasattr(obj, '__slots__'):
                return {slot: getattr(obj, slot, None) 
                       for slot in obj.__slots__}
            
            # Handle iterables (but not strings/bytes)
            elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
                return list(obj)
            
            # Last resort: convert to string
            else:
                return str(obj)
                
        except Exception as e:
            logger.warning(f"Failed to encode {type(obj).__name__}: {e}")
            return f"<Unserializable: {type(obj).__name__}>"

def safe_json_encode(content: Any, ensure_ascii: bool = False) -> str:
    """
    Safely encode content to JSON with comprehensive error handling.
    
    Args:
        content: Content to encode
        ensure_ascii: Whether to escape non-ASCII characters
        
    Returns:
        JSON string
        
    Raises:
        SerializationError: If encoding fails completely
    """
    if content is None:
        return json.dumps(None)
    
    try:
        return json.dumps(
            content, 
            cls=CustomJSONEncoder, 
            ensure_ascii=ensure_ascii,
            separators=(',', ':') 
        )
    except (TypeError, ValueError, RecursionError) as e:
        logger.error(f"Primary serialization failed: {e}")
        
        # Create error response
        try:
            error_content = {
                'error': 'serialization_failed',
                'message': str(e),
                'content_type': type(content).__name__,
                'content_repr': repr(content)[:200] 
            }
            return json.dumps(error_content, ensure_ascii=ensure_ascii)
        except Exception as fallback_error:
            raise SerializationError(content, e) from fallback_error
