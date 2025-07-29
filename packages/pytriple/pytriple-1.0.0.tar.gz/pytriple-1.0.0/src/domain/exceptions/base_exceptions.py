"""
Base exceptions for the multiline string indentation fixer domain.
"""

class MultilineStringFixerException(Exception):
    """Base exception for all multiline string fixer errors."""
    
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message

class DomainException(MultilineStringFixerException):
    """Base exception for domain-related errors."""
    pass

class ValidationException(DomainException):
    """Exception raised when domain validation fails."""
    pass

class BusinessRuleException(DomainException):
    """Exception raised when business rules are violated."""
    pass