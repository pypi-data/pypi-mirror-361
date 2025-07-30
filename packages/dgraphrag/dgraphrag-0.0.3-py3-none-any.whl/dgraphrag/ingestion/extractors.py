"""Simple extractor for MVP using regex pattern 'X is Y'."""

from __future__ import annotations

import re
from typing import List

from ..core.base import BaseExtractor, Triple


class RegexExtractor(BaseExtractor):
    """Extract triples using a naive 'X is Y' pattern inside text chunks."""

    PATTERN = re.compile(r"(?P<subject>[A-Z][\w]*)\s+is\s+(?P<object>[A-Z][\w]*)\.")

    def extract(self, chunks: List[str]) -> List[Triple]:  # noqa: D401
        triples: List[Triple] = []
        for chunk in chunks:
            for match in self.PATTERN.finditer(chunk):
                subject = match.group("subject").strip()
                obj = match.group("object").strip()
                predicate = "is"
                triples.append(Triple(subject, predicate, obj))
        return triples
