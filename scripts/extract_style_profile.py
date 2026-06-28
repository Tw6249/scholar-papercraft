#!/usr/bin/env python3
"""Extract a lightweight style profile from exemplar drafts or papers.

The profile captures style statistics and transferable rhetorical moves. It
must not be treated as factual evidence for a target paper.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

from paper_state_common import count_words, iter_text_files, read_text, split_sentences, write_json


TRANSITIONS = ("moreover", "furthermore", "additionally", "in addition", "however", "therefore")

MOVE_PATTERNS = {
    "gap_sentence_patterns": (
        r"\b(?:however|yet|nevertheless|despite this|although)\b[^.?!]{20,180}",
        r"\b(?:remain|remains|lack|lacks|do not|does not|cannot|fails to)\b[^.?!]{20,180}",
    ),
    "claim_qualification_patterns": (
        r"\b(?:under|given|assuming|provided that|within|for)\b[^.?!]{10,160}",
        r"\b(?:suggests|indicates|is consistent with|we hypothesize)\b[^.?!]{10,160}",
    ),
    "theorem_interpretation_patterns": (
        r"\b(?:Theorem|Lemma|Proposition|Corollary)\s+\w+[^.?!]{10,180}",
        r"\b(?:implies|establishes|guarantees|ensures)\b[^.?!]{10,180}",
    ),
    "figure_interpretation_patterns": (
        r"\b(?:Figure|Fig\.|Table)\s+\w+[^.?!]{10,180}",
        r"\b(?:shows|reports|compares|summarizes)\b[^.?!]{10,180}",
    ),
    "experiment_takeaway_patterns": (
        r"\b(?:results|experiments|ablation|evaluation)\b[^.?!]{10,180}",
        r"\b(?:reduces|improves|outperforms|matches|degrades)\b[^.?!]{10,180}",
    ),
    "limitation_phrasing_patterns": (
        r"\b(?:limited to|does not|we leave|future work|limitation|assumes|requires)\b[^.?!]{10,180}",
    ),
    "related_work_contrast_patterns": (
        r"\b(?:in contrast|unlike|whereas|while prior|existing methods)\b[^.?!]{10,180}",
        r"\b(?:differs from|complements|extends|relaxes|specializes)\b[^.?!]{10,180}",
    ),
    "abstract_ending_patterns": (
        r"\b(?:overall|together|these results|our results|the results)\b[^.?!]{10,180}",
    ),
}

PREFERRED_VERBS = (
    "establish",
    "derive",
    "bound",
    "enforce",
    "estimate",
    "separate",
    "reduce",
    "compare",
    "ablate",
    "verify",
    "certify",
)

AVOID_PHRASES = (
    "it is important to note that",
    "it is worth noting that",
    "opens new avenues",
    "paves the way",
    "robust framework",
    "highly effective",
    "significantly improves",
)


def sample_patterns(text: str, patterns: tuple[str, ...], limit: int = 8) -> list[str]:
    samples: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            snippet = " ".join(match.group(0).split())
            if 8 <= len(snippet.split()) <= 40 and snippet not in samples:
                samples.append(snippet)
            if len(samples) >= limit:
                return samples
    return samples


def rhetorical_moves(text: str) -> dict[str, list[str]]:
    return {name: sample_patterns(text, patterns) for name, patterns in MOVE_PATTERNS.items()}


def section_patterns(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = "global"
    buckets: dict[str, list[str]] = {current: []}
    for line in text.splitlines():
        heading = re.match(r"^\s*(?:#+|\\section\*?\{|\\subsection\*?\{)\s*([^}\n]+)", line)
        if heading:
            current = re.sub(r"[^A-Za-z0-9_-]+", "_", heading.group(1).strip().lower()).strip("_") or "section"
            buckets.setdefault(current, [])
        elif line.strip():
            buckets.setdefault(current, []).append(line.strip())
    for name, lines in buckets.items():
        joined = " ".join(lines)
        moves = []
        for move, samples in rhetorical_moves(joined).items():
            if samples:
                moves.append(move)
        if moves:
            sections[name] = moves
    return sections


def profile(files: list[Path], venue: str, domain: str) -> dict[str, object]:
    all_sentences = []
    all_text = []
    citation_count = 0
    transition_count = 0
    paragraph_count = 0
    starts: dict[str, int] = {}
    full_text_parts: list[str] = []
    for file in files:
        text = read_text(file)
        full_text_parts.append(text)
        all_text.append(text)
        sentences = split_sentences(text)
        all_sentences.extend(sentences)
        citation_count += len(re.findall(r"\\cite\w*\s*(?:\[[^\]]*\]){0,2}\s*\{", text))
        transition_count += sum(len(re.findall(rf"\b{re.escape(t)}\b", text, re.IGNORECASE)) for t in TRANSITIONS)
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        paragraph_count += len(paragraphs)
        for para in paragraphs:
            start = " ".join(re.findall(r"[A-Za-z]+", para.lower())[:3])
            if start:
                starts[start] = starts.get(start, 0) + 1

    full_text = "\n".join(full_text_parts)
    words = count_words("\n".join(all_text))
    sent_lengths = [count_words(s) for s in all_sentences if count_words(s)]
    median_sentence_words = statistics.median(sent_lengths) if sent_lengths else 0
    mean_sentence_words = statistics.mean(sent_lengths) if sent_lengths else 0
    stdev_sentence_words = statistics.pstdev(sent_lengths) if len(sent_lengths) > 1 else 0

    common_starts = sorted(starts.items(), key=lambda item: (-item[1], item[0]))[:12]
    move_samples = rhetorical_moves(full_text)
    return {
        "corpus": {
            "venue": venue,
            "domain": domain,
            "num_files": len(files),
            "sections_analyzed": [],
        },
        "sections": {
            "global": {
                "median_sentence_words": median_sentence_words,
                "mean_sentence_words": round(mean_sentence_words, 2),
                "stdev_sentence_words": round(stdev_sentence_words, 2),
                "citation_density_per_1000_words": round(citation_count / max(words, 1) * 1000, 2),
                "transition_density_per_1000_words": round(transition_count / max(words, 1) * 1000, 2),
                "paragraph_count": paragraph_count,
                "common_sentence_or_paragraph_starts": [start for start, _ in common_starts],
                "avoid": [],
            }
        },
        "language_modes": {
            "cold-dense": {
                "goal": "short, precise, evidence-forward, low adjective and transition load",
                "best_for": ["control", "robotics", "Automatica", "T-RO", "RA-L", "ICRA/IROS"],
            },
            "narrative-persuasive": {
                "goal": "strong reader path and paragraph momentum without marketing language",
                "best_for": ["Science Robotics", "Nature-family venues", "NeurIPS/ICLR introductions"],
            },
        },
        "rhetorical_moves": move_samples,
        "section_patterns": section_patterns(full_text),
        "preferred_verbs": [verb for verb in PREFERRED_VERBS if re.search(rf"\b{re.escape(verb)}\w*\b", full_text, re.IGNORECASE)],
        "avoid_phrases": [phrase for phrase in AVOID_PHRASES if re.search(rf"\b{re.escape(phrase)}\b", full_text, re.IGNORECASE)],
        "phrase_copying_risk_notes": [
            "Use these snippets only to infer move types and syntax constraints.",
            "Do not copy exemplar facts, citations, assumptions, limitations, or consecutive distinctive phrasing.",
        ],
        "global_avoid": ["copying consecutive exemplar phrases", "importing exemplar facts"],
        "fact_isolation_notes": ["This profile contains style statistics only; it is not factual evidence for the target paper."],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Exemplar text files or folders")
    parser.add_argument("--venue", default="", help="Venue label")
    parser.add_argument("--domain", default="", help="Domain label")
    parser.add_argument("--out", help="Write JSON profile to this path")
    args = parser.parse_args()

    files = iter_text_files([Path(p) for p in args.paths])
    data = profile(files, args.venue, args.domain)
    if args.out:
        write_json(Path(args.out).expanduser().resolve(), data)
        print(f"Wrote {Path(args.out).expanduser().resolve()}")
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
