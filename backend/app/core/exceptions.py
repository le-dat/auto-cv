"""Custom exceptions for CV Optimizer."""


class CVOptimizerError(Exception):
    """Base exception for all CV Optimizer errors."""

    pass


class ParseError(CVOptimizerError):
    """Raised when CV or JD parsing fails."""

    pass


class ValidationError(CVOptimizerError):
    """Raised when extracted data fails Pydantic validation."""

    pass


class ContextError(CVOptimizerError):
    """Raised when context gathering fails."""

    pass


class MatchError(CVOptimizerError):
    """Raised when skill matching fails."""

    pass


class RewriteError(CVOptimizerError):
    """Raised when CV rewriting fails."""

    pass


class JobNotFoundError(CVOptimizerError):
    """Raised when a job record is not found."""

    pass


class RateLimitError(CVOptimizerError):
    """Raised when rate limit is exceeded."""

    pass
