"""Custom exception hierarchy for dgraphrag MVP."""

class DGraphRAGError(Exception):
    """Base exception for all dgraphrag errors."""


class IngestionError(DGraphRAGError):
    """Raised when ingestion fails."""


class GraphAdapterError(DGraphRAGError):
    """Raised for graph adapter related errors."""


class RetrievalError(DGraphRAGError):
    """Raised during retrieval phase errors."""
