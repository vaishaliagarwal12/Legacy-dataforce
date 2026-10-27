class ServiceError(Exception):
    """Base exception for all service layer operations."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(ServiceError):
    """Raised when request payload or parameters fail domain validation rules."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class NotFoundError(ServiceError):
    """Raised when a requested resource does not exist in the database."""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ConflictError(ServiceError):
    """Raised when an operation violates unique constraints or business rules."""
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class ProtectedDeleteError(ConflictError):
    """Raised when a deletion is blocked to preserve critical history (e.g. placements, internships)."""
    def __init__(self, message: str):
        super().__init__(message)
