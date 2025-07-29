import json
import logging
from typing import Any, Dict, Optional

from .encoders import safe_json_encode
from .exceptions import (InvalidHeaderError, InvalidStatusCodeError,
                         SerializationError)

logger = logging.getLogger(__name__)


class JSONResponse:
    """
    A robust JSON response class for serverless functions with comprehensive
    exception handling and API Gateway compatibility.
    """
    
    # Valid HTTP status code ranges
    MIN_STATUS_CODE = 100
    MAX_STATUS_CODE = 599
    
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        ensure_ascii: bool = False
    ):
        """
        Initialize a JSON response with validation.
        
        Args:
            content: The data to be JSON-encoded
            status_code: HTTP status code (100-599)
            headers: Optional HTTP headers dictionary
            ensure_ascii: Whether to escape non-ASCII characters
            
        Raises:
            InvalidStatusCodeError: If status code is invalid
            InvalidHeaderError: If headers are invalid
        """
        self._validate_status_code(status_code)
        self._validate_headers(headers)
        
        self.content = content
        self.status_code = status_code
        self.headers = self._normalize_headers(headers or {})
        self.ensure_ascii = ensure_ascii
        
        # Set default content type
        if 'content-type' not in self.headers:
            self.headers['content-type'] = 'application/json'
    
    def _validate_status_code(self, status_code: int) -> None:
        """Validate HTTP status code."""
        if not isinstance(status_code, int):
            raise InvalidStatusCodeError(f"Status code must be integer, got {type(status_code)}")
        
        if not (self.MIN_STATUS_CODE <= status_code <= self.MAX_STATUS_CODE):
            raise InvalidStatusCodeError(status_code)
    
    def _validate_headers(self, headers: Optional[Dict[str, str]]) -> None:
        """Validate headers dictionary."""
        if headers is None:
            return
        
        if not isinstance(headers, dict):
            raise InvalidHeaderError("headers", "Headers must be a dictionary")
        
        for key, value in headers.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise InvalidHeaderError(key, f"Header key and value must be strings, got {type(key)} and {type(value)}")
    
    def _normalize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Normalize header keys to lowercase for consistency."""
        return {key.lower(): value for key, value in headers.items()}
    
    def __call__(self) -> Dict[str, Any]:
        """Make the response callable to return API Gateway response dict."""
        return self.to_dict()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to API Gateway-compatible dictionary.
        
        Returns:
            Dictionary with statusCode, headers, and body
            
        Raises:
            SerializationError: If content cannot be serialized
        """
        try:
            body = safe_json_encode(self.content, self.ensure_ascii)
            
            return {
                'statusCode': self.status_code,
                'headers': self.headers,
                'body': body,
                'isBase64Encoded': False
            }
        except SerializationError as e:
            logger.error(f"Response serialization failed: {e}")
            # Return error response instead of raising
            return {
                'statusCode': 500,
                'headers': {'content-type': 'application/json'},
                'body': json.dumps({
                    'error': 'internal_server_error',
                    'message': 'Response serialization failed'
                }),
                'isBase64Encoded': False
            }
    
    def add_header(self, key: str, value: str) -> 'JSONResponse':
        """
        Add a header (chainable).
        
        Args:
            key: Header name
            value: Header value
            
        Returns:
            Self for method chaining
            
        Raises:
            InvalidHeaderError: If header is invalid
        """
        if not isinstance(key, str) or not isinstance(value, str):
            raise InvalidHeaderError(key, f"Header must be strings, got {type(key)} and {type(value)}")
        
        self.headers[key.lower()] = value
        return self
    
    def set_cors(
        self, 
        origin: str = "*", 
        methods: Optional[str] = None,
        headers: Optional[str] = None
    ) -> 'JSONResponse':
        """
        Add CORS headers (chainable).
        
        Args:
            origin: Allowed origin
            methods: Allowed methods
            headers: Allowed headers
            
        Returns:
            Self for method chaining
        """
        cors_headers = {
            'access-control-allow-origin': origin,
            'access-control-allow-methods': methods or 'GET, POST, PUT, DELETE, OPTIONS',
            'access-control-allow-headers': headers or 'Content-Type, Authorization, X-Requested-With'
        }
        
        self.headers.update(cors_headers)
        return self
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"JSONResponse(status={self.status_code}, headers={len(self.headers)})"
