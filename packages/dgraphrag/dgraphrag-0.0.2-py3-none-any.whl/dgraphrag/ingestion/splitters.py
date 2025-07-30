"""Text splitters for dgraphrag MVP."""

from __future__ import annotations

import re
from typing import List

from ..core.base import BaseSplitter


class SimpleParagraphSplitter(BaseSplitter):
    """Split text by blank lines into paragraphs."""

    def __init__(self, min_len: int = 20) -> None:
        self.min_len = min_len

    def split(self, text: str) -> List[str]:  # noqa: D401
        # Normalize line endings
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        paragraphs = re.split(r"\n\s*\n", normalized)
        return [p.strip() for p in paragraphs if len(p.strip()) >= self.min_len]
