import logging
import traceback
from typing import Any, Dict, Optional

from .exceptions import InvalidHeaderError, InvalidStatusCodeError
from .response import JSONResponse

logger = logging.getLogger(__name__)


def json_response(
    content: Any = None,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    function for quick JSON responses.
    
    Args:
        content: Response content
        status_code: HTTP status code
        headers: Optional headers
        **kwargs: Additional JSONResponse arguments
        
    Returns:
        API Gateway-compatible response dictionary
    """
    try:
        return JSONResponse(content, status_code, headers, **kwargs).to_dict()
    except (InvalidStatusCodeError, InvalidHeaderError) as e:
        logger.error(f"Invalid response parameters: {e}")
        return error_response(f"Invalid response: {e}", 500)


def success_response(
    data: Any = None, 
    message: str = "Success",
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create standardized success response."""
    content = {
        'success': True,
        'message': message
    }
    
    if data is not None:
        content['data'] = data
    
    return json_response(content, status_code, headers)


def error_response(
    message: str = "Fail",
    status_code: int = 400,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create standardized error response."""
    content = {
        'success': False,
        'error': {
            'message': message,
            'status_code': status_code
        }
    }
    
    if error_code:
        content['error']['code'] = error_code
    
    if details:
        content['error']['details'] = details
    
    return json_response(content, status_code, headers)


def exception_response(
    exception: Exception,
    status_code: int = 500,
    include_traceback: bool = False
) -> Dict[str, Any]:
    """
    Create error response from exception.
    
    Args:
        exception: The exception that occurred
        status_code: HTTP status code
        include_traceback: Whether to include full traceback (dev only)
        
    Returns:
        API Gateway-compatible error response
    """
    error_details = {
        'type': type(exception).__name__,
        'message': str(exception)
    }
    
    if include_traceback:
        error_details['traceback'] = traceback.format_exc()
    
    logger.exception("Exception in response handler", exc_info=exception)
    
    return error_response(
        message="An internal error occurred",
        status_code=status_code,
        error_code="INTERNAL_ERROR",
        details=error_details
    )
