"""Advanced triple extractors for dgraphrag.

This sub-module provides several extraction strategies:
1. `AdvancedRegexExtractor` – more flexible pattern rules.
2. `SpacyDependencyExtractor` – dependency-based using spaCy.
3. `StanfordCoreNLPExtractor` – via stanza (lightweight Stanford CoreNLP).
4. `LLMExtractor` – generic LLM prompt (works with OpenAI).

All extractors implement the same `BaseExtractor` interface and can be
hot-swapped in the pipeline.
"""

from __future__ import annotations

import re
from typing import List

from ..core.base import BaseExtractor, Triple

# ---------------------------------------------------------------------------
# 1. Advanced regex extractor
# ---------------------------------------------------------------------------


class AdvancedRegexExtractor(BaseExtractor):
    """Extract triples with richer copular/verbal patterns."""

    # Matches e.g. "X is/are/was/were Y", "X becomes Y", "X remains Y"
    _PATTERN = re.compile(
        r"(?P<subject>[A-Z][\w\s]{0,40}?)\s+"
        r"(?P<predicate>is|are|was|were|becomes|remains)\s+"
        r"(?P<object>[A-Z][\w\s]{0,40}?)\.",
        flags=re.IGNORECASE,
    )

    def extract(self, chunks: List[str]) -> List[Triple]:  # noqa: D401
        triples: List[Triple] = []
        for text in chunks:
            for m in self._PATTERN.finditer(text):
                triples.append(
                    Triple(
                        m.group("subject").strip(),
                        m.group("predicate").lower(),
                        m.group("object").strip(),
                    )
                )
        return triples


# ---------------------------------------------------------------------------
# 2. spaCy extractor (dependency parsing)
# ---------------------------------------------------------------------------

try:
    import spacy  # type: ignore
except ImportError:  # pragma: no cover
    spacy = None  # type: ignore


class SpacyDependencyExtractor(BaseExtractor):
    """Use spaCy dependency parse to extract (subject, copula, attr) triples."""

    def __init__(self, model: str = "en_core_web_sm") -> None:  # noqa: D401
        if spacy is None:
            raise ImportError("spaCy is not installed. Run `pip install spacy` and download a model.")
        self.nlp = spacy.load(model)

    def extract(self, chunks: List[str]) -> List[Triple]:  # noqa: D401
        triples: List[Triple] = []
        for text in chunks:
            doc = self.nlp(text)
            for token in doc:
                # Find copular constructions: nsubj –(cop)–> ROOT(be) –(attr)–>
                if token.dep_ == "cop" and token.head.lemma_ == "be":
                    subject = None
                    obj = None
                    for child in token.head.children:
                        if child.dep_ == "nsubj":
                            subject = child.text
                        elif child.dep_ in {"attr", "acomp"}:
                            obj = child.text
                    if subject and obj:
                        triples.append(Triple(subject, "is", obj))
        return triples


# ---------------------------------------------------------------------------
# 3. Stanford CoreNLP / stanza extractor
# ---------------------------------------------------------------------------

try:
    import stanza  # type: ignore
except ImportError:  # pragma: no cover
    stanza = None  # type: ignore


class StanfordCoreNLPExtractor(BaseExtractor):
    """Extractor using stanza's dependency parse (lightweight Stanford CoreNLP)."""

    def __init__(self) -> None:  # noqa: D401
        if stanza is None:
            raise ImportError("stanza is not installed. Run `pip install stanza` and download English model.")
        stanza.download("en", processors="tokenize,pos,lemma,depparse", verbose=False)
        self.nlp = stanza.Pipeline(lang="en", processors="tokenize,pos,lemma,depparse", verbose=False)

    def extract(self, chunks: List[str]) -> List[Triple]:  # noqa: D401
        triples: List[Triple] = []
        for text in chunks:
            doc = self.nlp(text)
            for sentence in doc.sentences:
                for word in sentence.words:
                    if word.deprel == "cop" and word.text.lower() in {"is", "are", "was", "were"}:
                        head = sentence.words[word.head - 1]
                        subj = next((w.text for w in sentence.words if w.head == head.id and w.deprel == "nsubj"), None)
                        obj = next((w.text for w in sentence.words if w.head == head.id and w.deprel in {"attr", "acomp"}), None)
                        if subj and obj:
                            triples.append(Triple(subj, "is", obj))
        return triples


# ---------------------------------------------------------------------------
# 4. LLM-based extractor
# ---------------------------------------------------------------------------

try:
    import openai  # type: ignore
    from openai import OpenAI  # type: ignore
except ImportError:  # pragma: no cover
    openai = None  # type: ignore


class LLMExtractor(BaseExtractor):
    """Generic extractor that asks an LLM to output triples in pipe-delimited format.

    Example returned lines:
        Foo | is | Bar
        Alice | works_for | AcmeCorp
    """

    def __init__(self, model: str = "gpt-3.5-turbo", client: OpenAI | None = None) -> None:  # noqa: D401
        if openai is None:
            raise ImportError("openai package not installed. Run `pip install openai`.")
        self.client = client or OpenAI()
        self.model = model

    def extract(self, chunks: List[str]) -> List[Triple]:  # noqa: D401
        prompt = (
            "Extract semantic triples from the following text chunks. "
            "Return one triple per line in the format: subject | predicate | object\n\n" +
            "\n\n".join(chunks)
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = response.choices[0].message.content if response.choices else ""
        triples: List[Triple] = []
        for line in content.splitlines():
            if "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 3:
                    triples.append(Triple(parts[0], parts[1], parts[2]))
        return triples
