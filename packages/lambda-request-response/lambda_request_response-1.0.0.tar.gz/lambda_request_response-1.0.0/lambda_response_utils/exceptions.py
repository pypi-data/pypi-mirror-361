class JSONResponseError(Exception):
    """Base exception for package."""
    pass


class SerializationError(JSONResponseError):
    """Raised when content cannot be serialized to JSON."""
    
    def __init__(self, content, original_error):
        self.content = content
        self.original_error = original_error
        super().__init__(f"Failed to serialize {type(content).__name__}: {original_error}")


class InvalidStatusCodeError(JSONResponseError):
    """Raised when an invalid HTTP status code is provided."""
    
    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"Invalid HTTP status code: {status_code}. Must be between 100-599.")


class InvalidHeaderError(JSONResponseError):
    """Raised when invalid headers are provided."""
    
    def __init__(self, header_key, header_value):
        self.header_key = header_key
        self.header_value = header_value
        super().__init__(f"Invalid header '{header_key}': {header_value}")
