"""Custom exception hierarchy for dgraphrag MVP."""

class dgraphragError(Exception):
    """Base exception for all dgraphrag errors."""


class IngestionError(dgraphragError):
    """Raised when ingestion fails."""


class GraphAdapterError(dgraphragError):
    """Raised for graph adapter related errors."""


class RetrievalError(dgraphragError):
    """Raised during retrieval phase errors."""
