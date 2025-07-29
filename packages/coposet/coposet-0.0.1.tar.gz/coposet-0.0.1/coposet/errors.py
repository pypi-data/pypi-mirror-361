"""
Custom error types for coposet operations.
"""


class CoposetError(Exception):
    """Base exception for all coposet errors."""

    pass


class ValidationError(CoposetError):
    """Raised when data validation fails."""

    pass


class NotFoundError(CoposetError):
    """Raised when a requested entity is not found."""

    pass


class RelationError(CoposetError):
    """Raised when poset relation operations fail."""

    pass


class ConsensusError(CoposetError):
    """Raised when consensus operations fail."""

    pass


class ExportError(CoposetError):
    """Raised when export operations fail."""

    pass


class VotingError(CoposetError):
    """Raised when voting operations fail."""

    pass


class EnrichmentError(CoposetError):
    """Raised when enrichment operations fail."""

    pass
