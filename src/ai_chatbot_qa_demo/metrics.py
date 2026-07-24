from __future__ import annotations

from collections import Counter
import re

TOKEN_RE = re.compile(r"[a-z0-9']+")

# Tiny synonym map for teaching METEOR/BERTScore ideas without heavy packages.
SYNONYM_CANONICAL = {
    "advil": "ibuprofen",
    "ibuprofen": "ibuprofen",
    "pharmacist": "pharmacist",
    "pharmacy": "pharmacist",
    "clinician": "pharmacist",
    "doctor": "clinician",
    "provider": "clinician",
    "prescriber": "clinician",
    "ask": "contact",
    "contact": "contact",
    "using": "take",
    "taking": "take",
    "use": "take",
    "warfarin": "warfarin",
}

MEANING_GROUPS = {
    "consult_professional": {"ask", "contact", "pharmacist", "pharmacy", "clinician", "doctor", "provider", "prescriber"},
    "medication_pair": {"ibuprofen", "advil", "warfarin"},
    "take_or_use": {"take", "taking", "using", "use"},
}


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def _overlap_count(candidate_tokens: list[str], reference_tokens: list[str]) -> int:
    candidate_counts = Counter(candidate_tokens)
    reference_counts = Counter(reference_tokens)
    return sum((candidate_counts & reference_counts).values())


def bleu_unigram_precision(candidate: str, reference: str) -> float:
    """Teaching BLEU-like score: exact token precision.

    Memory cheat: BLEU ≈ precision. "Of what the chatbot said, how much matches the reference?"
    """

    candidate_tokens = tokenize(candidate)
    if not candidate_tokens:
        return 0.0
    return _overlap_count(candidate_tokens, tokenize(reference)) / len(candidate_tokens)


def rouge_unigram_recall(candidate: str, reference: str) -> float:
    """Teaching ROUGE-like score: exact token recall.

    Memory cheat: ROUGE ≈ recall. "Of what the reference expected, how much did the chatbot cover?"
    """

    reference_tokens = tokenize(reference)
    if not reference_tokens:
        return 0.0
    return _overlap_count(tokenize(candidate), reference_tokens) / len(reference_tokens)


def _canonicalize_for_synonyms(text: str) -> list[str]:
    return [SYNONYM_CANONICAL.get(token, token) for token in tokenize(text)]


def meteor_synonym_overlap(candidate: str, reference: str) -> float:
    """Teaching METEOR-like score: token overlap with synonym credit.

    Memory cheat: METEOR gives more credit for synonyms/stems than plain BLEU/ROUGE.
    """

    candidate_tokens = _canonicalize_for_synonyms(candidate)
    reference_tokens = _canonicalize_for_synonyms(reference)
    if not candidate_tokens or not reference_tokens:
        return 0.0
    overlap = _overlap_count(candidate_tokens, reference_tokens)
    precision = overlap / len(candidate_tokens)
    recall = overlap / len(reference_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _meaning_concepts(text: str) -> set[str]:
    tokens = set(tokenize(text))
    concepts = set()
    for concept, words in MEANING_GROUPS.items():
        if tokens & words:
            concepts.add(concept)
    return concepts


def bertscore_meaning_overlap(candidate: str, reference: str) -> float:
    """Tiny BERTScore-style meaning overlap.

    Official BERTScore uses contextual embeddings. This toy version only checks broad
    meaning groups so the project remains small and runnable for beginners.

    Memory cheat: BERTScore ≈ meaning similarity.
    """

    candidate_concepts = _meaning_concepts(candidate)
    reference_concepts = _meaning_concepts(reference)
    if not candidate_concepts or not reference_concepts:
        return 0.0
    overlap = len(candidate_concepts & reference_concepts)
    precision = overlap / len(candidate_concepts)
    recall = overlap / len(reference_concepts)
    if precision + recall == 0:
        return 0.0
    semantic_f1 = 2 * precision * recall / (precision + recall)
    return max(semantic_f1, meteor_synonym_overlap(candidate, reference))


def choose_metric_for_chatbot() -> str:
    return (
        "For chatbots, use intent + business outcome + guardrail checks as the primary pass/fail gate. "
        "Use BERTScore or human/domain review as a secondary meaning-similarity signal; BLEU/ROUGE are weaker "
        "because safe chatbot wording can vary a lot."
    )
