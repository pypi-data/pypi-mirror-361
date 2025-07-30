"""Document loaders for dgraphrag MVP."""

from __future__ import annotations

from pathlib import Path

from ..core.base import BaseLoader
from ..core.exceptions import IngestionError


class LocalTextLoader(BaseLoader):
    """Load plain text, markdown, or HTML files from local disk."""

    SUPPORTED_SUFFIXES = {".txt", ".md", ".html", ".htm"}

    def load(self, path: str | Path) -> str:  # noqa: D401
        file_path = Path(path)
        if not file_path.exists():
            raise IngestionError(f"File not found: {file_path}")

        if file_path.suffix.lower() not in self.SUPPORTED_SUFFIXES:
            raise IngestionError(
                f"Unsupported file type: {file_path.suffix}. "
                f"Supported: {', '.join(self.SUPPORTED_SUFFIXES)}"
            )

        text = file_path.read_text(encoding="utf-8", errors="ignore")

        # crude HTML tag stripping if needed
        if file_path.suffix.lower() in {".html", ".htm"}:
            import re

            text = re.sub(r"<[^>]+>", " ", text)
        return text
