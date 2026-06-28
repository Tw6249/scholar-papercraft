#!/usr/bin/env python3
"""Language-density metrics shared by Scholar Papercraft scripts."""

from __future__ import annotations

import re
import statistics
from collections import Counter
from dataclasses import dataclass

from paper_state_common import count_words, split_sentences


FILLER_PHRASES = (
    "it is important to note that",
    "it is worth noting that",
    "in order to",
    "it should be noted that",
    "as previously mentioned",
    "in this paper, we",
    "this paper presents",
    "the rest of this paper",
)
TRANSITIONS = (
    "moreover",
    "furthermore",
    "additionally",
    "in addition",
    "overall",
    "therefore",
    "thus",
    "however",
)
VAGUE_EVALUATORS = (
    "important",
    "effective",
    "powerful",
    "comprehensive",
    "promising",
    "superior",
    "substantial",
    "crucial",
    "pivotal",
    "transformative",
    "groundbreaking",
    "significant",
)
WEAK_VERBS = (
    "highlight",
    "highlights",
    "highlighted",
    "underscore",
    "underscores",
    "underscored",
    "showcase",
    "showcases",
    "showcased",
    "leverage",
    "leverages",
    "leveraged",
    "utilize",
    "utilizes",
    "utilized",
    "facilitate",
    "facilitates",
    "facilitated",
)
ACTION_VERBS = (
    "prove",
    "proves",
    "bound",
    "bounds",
    "reduce",
    "reduces",
    "separate",
    "separates",
    "estimate",
    "estimates",
    "enforce",
    "enforces",
    "derive",
    "derives",
    "establish",
    "establishes",
    "measure",
    "measures",
    "compare",
    "compares",
    "ablate",
    "ablates",
)
CLAIM_STRENGTH_TERMS = (
    "guarantee",
    "guarantees",
    "ensure",
    "ensures",
    "prove",
    "proves",
    "optimal",
    "globally optimal",
    "stable",
    "safe",
    "robust",
    "state-of-the-art",
    "significant",
    "first",
    "novel",
)
TECHNICAL_TERMS = (
    "theorem",
    "lemma",
    "proof",
    "assumption",
    "constraint",
    "objective",
    "baseline",
    "ablation",
    "metric",
    "dataset",
    "controller",
    "policy",
    "optimization",
    "feasibility",
    "stability",
    "safety",
    "invariance",
    "latency",
    "seed",
    "trial",
    "simulation",
    "hardware",
)

EMPTY_CONCLUSION_RE = re.compile(
    r"\b(?:these|the)\s+results\s+(?:demonstrate|show|highlight|underscore)\s+"
    r"(?:the\s+)?(?:effectiveness|superiority|benefits?|advantages?)\b",
    re.IGNORECASE,
)
NOMINALIZATION_RE = re.compile(
    r"\b(realization|utilization|implementation|improvement|optimization|enhancement|"
    r"demonstration|evaluation|investigation|consideration)\s+of\s+(?:the\s+)?\w+",
    re.IGNORECASE,
)
CITE_RE = re.compile(r"\\cite\w*\s*(?:\[[^\]]*\]){0,2}\s*\{([^}]*)\}")
REF_RE = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref)\s*\{([^}]*)\}")
LABEL_RE = re.compile(r"\\label\s*\{([^}]*)\}")
NUMBER_RE = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?\s*(?:%|pp|Hz|ms|s|m|cm|mm|rad|N|Nm|kg|W)?", re.IGNORECASE)


@dataclass(frozen=True)
class LanguageMetrics:
    word_count: int
    sentence_count: int
    sentence_mean: float
    sentence_stdev: float
    filler_count: int
    transition_count: int
    vague_evaluator_count: int
    weak_verb_count: int
    action_verb_count: int
    nominalization_count: int
    empty_conclusion_count: int
    repeated_opening_count: int
    claim_bearing_sentence_count: int
    technical_term_count: int
    claim_strength_term_count: int

    @property
    def filler_per_1000(self) -> float:
        return self.filler_count / max(self.word_count, 1) * 1000

    @property
    def transition_per_1000(self) -> float:
        return self.transition_count / max(self.word_count, 1) * 1000

    @property
    def vague_evaluator_per_1000(self) -> float:
        return self.vague_evaluator_count / max(self.word_count, 1) * 1000

    @property
    def weak_verb_per_1000(self) -> float:
        return self.weak_verb_count / max(self.word_count, 1) * 1000

    @property
    def nominalization_per_1000(self) -> float:
        return self.nominalization_count / max(self.word_count, 1) * 1000

    @property
    def claim_bearing_ratio(self) -> float:
        return self.claim_bearing_sentence_count / max(self.sentence_count, 1)

    @property
    def technical_action_balance(self) -> float:
        return (self.technical_term_count + self.action_verb_count) / max(self.word_count, 1) * 1000


def term_count(text: str, terms: tuple[str, ...]) -> int:
    total = 0
    for term in terms:
        total += len(re.findall(rf"\b{re.escape(term)}\b", text, re.IGNORECASE))
    return total


def sentence_opening_repetitions(sentences: list[str]) -> int:
    starts: Counter[str] = Counter()
    for sent in sentences:
        words = re.findall(r"[A-Za-z]+", sent.lower())[:3]
        if len(words) == 3:
            starts[" ".join(words)] += 1
    return sum(count - 1 for count in starts.values() if count >= 3)


def claim_bearing_sentences(sentences: list[str]) -> int:
    claim_re = re.compile(
        r"\b(we|our|this|these|result|results|method|approach|controller|policy|"
        r"theorem|lemma|experiment|ablation|figure|table)\b",
        re.IGNORECASE,
    )
    evidence_re = re.compile(r"\b(show|shows|prove|proves|establish|establishes|reduce|reduces|improve|improves|support|supports|indicate|indicates|suggest|suggests|demonstrate|demonstrates)\b", re.IGNORECASE)
    return sum(1 for sent in sentences if claim_re.search(sent) and evidence_re.search(sent))


def language_metrics(text: str) -> LanguageMetrics:
    sentences = split_sentences(text)
    lengths = [count_words(sent) for sent in sentences if count_words(sent)]
    sentence_mean = statistics.mean(lengths) if lengths else 0.0
    sentence_stdev = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0
    return LanguageMetrics(
        word_count=count_words(text),
        sentence_count=len(sentences),
        sentence_mean=sentence_mean,
        sentence_stdev=sentence_stdev,
        filler_count=term_count(text, FILLER_PHRASES),
        transition_count=term_count(text, TRANSITIONS),
        vague_evaluator_count=term_count(text, VAGUE_EVALUATORS),
        weak_verb_count=term_count(text, WEAK_VERBS),
        action_verb_count=term_count(text, ACTION_VERBS),
        nominalization_count=len(NOMINALIZATION_RE.findall(text)),
        empty_conclusion_count=len(EMPTY_CONCLUSION_RE.findall(text)),
        repeated_opening_count=sentence_opening_repetitions(sentences),
        claim_bearing_sentence_count=claim_bearing_sentences(sentences),
        technical_term_count=term_count(text, TECHNICAL_TERMS),
        claim_strength_term_count=term_count(text, CLAIM_STRENGTH_TERMS),
    )


def extract_citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for match in CITE_RE.finditer(text):
        keys.update(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def extract_ref_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for regex in (REF_RE, LABEL_RE):
        for match in regex.finditer(text):
            keys.add(match.group(1).strip())
    return keys


def extract_numbers(text: str) -> list[str]:
    return [re.sub(r"\s+", "", match.group(0)) for match in NUMBER_RE.finditer(text)]


def metric_table(metrics: LanguageMetrics) -> list[tuple[str, str]]:
    return [
        ("words", str(metrics.word_count)),
        ("sentences", str(metrics.sentence_count)),
        ("sentence_mean", f"{metrics.sentence_mean:.1f}"),
        ("sentence_stdev", f"{metrics.sentence_stdev:.1f}"),
        ("filler_per_1000", f"{metrics.filler_per_1000:.1f}"),
        ("transition_per_1000", f"{metrics.transition_per_1000:.1f}"),
        ("vague_evaluator_per_1000", f"{metrics.vague_evaluator_per_1000:.1f}"),
        ("weak_verb_per_1000", f"{metrics.weak_verb_per_1000:.1f}"),
        ("nominalization_per_1000", f"{metrics.nominalization_per_1000:.1f}"),
        ("empty_conclusions", str(metrics.empty_conclusion_count)),
        ("repeated_openings", str(metrics.repeated_opening_count)),
        ("claim_bearing_ratio", f"{metrics.claim_bearing_ratio:.2f}"),
        ("technical_action_balance", f"{metrics.technical_action_balance:.1f}"),
        ("claim_strength_terms", str(metrics.claim_strength_term_count)),
    ]
