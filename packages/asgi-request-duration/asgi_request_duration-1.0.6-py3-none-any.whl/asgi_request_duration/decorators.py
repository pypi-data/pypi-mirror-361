from collections.abc import Callable
from .constants import (
    _DEFAULT_HEADER_NAME,
    _DEFAULT_PRECISION,
    _DEFAULT_SKIP_VALIDATE_HEADER_NAME,
    _DEFAULT_SKIP_VALIDATE_PRECISION,
    _HEADER_NAME_PATTERN,
    _PRECISION_MAX,
    _PRECISION_MIN,
)
from .exceptions import (
    InvalidHeaderNameException, 
    PrecisionValueOutOfRangeException,
)

def validate_header_name(skip: bool =_DEFAULT_SKIP_VALIDATE_HEADER_NAME) -> Callable:
    """
    Decorator to validate the header name against a pattern.
    
    Args:
        func (function): The function to be decorated.
        skip (bool): Flag to skip the validation.
    
    Returns:
        function: The wrapped function with header name validation.
    
    Raises:
        InvalidHeaderNameException: If the header name is invalid.
    """
    def decorator(func: Callable)-> Callable:
        def wrapper(self, *args, **kwargs) -> Callable:
            if not skip:
                header_name = getattr(self, 'header_name', _DEFAULT_HEADER_NAME)
                if not _HEADER_NAME_PATTERN.match(header_name):
                    raise InvalidHeaderNameException(header_name)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def validate_precision(skip: bool =_DEFAULT_SKIP_VALIDATE_PRECISION)-> Callable:
    """
    Decorator to validate the precision value.
    
    Args:
        func (function): The function to be decorated.
        skip (bool): Flag to skip the validation.
    
    Returns:
        function: The wrapped function with precision validation.
    
    Raises:
        TypeError: If the precision value is not an integer.
        PrecisionValueOutOfRangeException: If the precision value is out of range.
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(self, *args, **kwargs) -> Callable:
            if not skip:
                precision = getattr(self, 'precision', _DEFAULT_PRECISION)
                if not isinstance(precision, int):
                    raise TypeError(f"Precision value must be an integer, not {type(precision).__name__}")
                if not (_PRECISION_MIN <= precision <= _PRECISION_MAX):
                    raise PrecisionValueOutOfRangeException(precision, _PRECISION_MIN, _PRECISION_MAX)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator