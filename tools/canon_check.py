#!/usr/bin/env python3
"""canon_check.py - VTuber Lore & Dialogue Builder (idea 221).

Deterministic canon-consistency and voice-fingerprint backend used by the
sub-scoring-engine. Implements the canon-consistency check described in
SECOND-KNOWLEDGE-BRAIN.md section 3 and the voice-fingerprint band match
used by the scoring rubric. Pure stdlib, dependency-free, unit-testable.

The agent (sub-scoring-engine) calls these helpers via Bash to get objective
consistency/voice signals; it then applies the engagement and safety rubrics
(which require judgment) on top. Keeping the objective parts in code makes the
consistency dimension reproducible and auditable.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

# OCEAN ordered bands for distance comparison.
_BANDS = {"Low": 0, "Mid": 1, "High": 2, None: 1}
OCEAN_DIMS = ("O", "C", "E", "A", "N")


@dataclass
class CanonRule:
    id: str
    hardness: str  # HARD | SOFT
    subject: str
    action: str
    reason: str
    source: str
    raw: str

    @property
    def is_hard(self) -> bool:
        return self.hardness.upper() == "HARD"


@dataclass
class VoiceFingerprint:
    O: str | None = None
    C: str | None = None
    E: str | None = None
    A: str | None = None
    N: str | None = None
    forbidden_words: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, str | None]:
        return {d: getattr(self, d) for d in OCEAN_DIMS}


@dataclass
class Contradiction:
    line: str
    rule_id: str
    fix: str


@dataclass
class VoiceDrift:
    line: str
    dimension: str
    expected: str
    actual: str


_CR_RE = re.compile(
    r"""^CR-\(?(\d+)\)?\s*        # CR-001
    \[(HARD|SOFT)\]\s*              # hardness
    (.+?)\s+cannot\s+(.+?)          # subject cannot action
    \s+because\s+(.+?)              # reason
    (?:\.\s*Source:\s*(.+?))?       # optional source
    \.?\s*$""",
    re.IGNORECASE | re.VERBOSE,
)


def parse_rules(text: str) -> list[CanonRule]:
    """Parse 'CR-xxx [HARD] ...' canon rules from lore-bible markdown."""
    rules: list[CanonRule] = []
    for line in text.splitlines():
        m = _CR_RE.match(line.strip())
        if not m:
            continue
        num, hardness, subject, action, reason, source = m.groups()
        rules.append(
            CanonRule(
                id=f"CR-{num}",
                hardness=hardness.upper(),
                subject=subject.strip(),
                action=action.strip(),
                reason=reason.strip(),
                source=(source or "").strip(),
                raw=line.strip(),
            )
        )
    return rules


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()


STOPWORDS = {
    "a", "an", "the", "on", "in", "of", "to", "and", "or", "for", "with", "at",
    "by", "from", "her", "his", "their", "its", "is", "was", "be", "do", "as",
    "that", "this", "these", "those", "it", "she", "he", "they", "we", "you",
}


def _content_tokens(text: str, min_len: int = 3) -> list[str]:
    """Tokenize but drop stopwords so a contradiction is triggered by meaningful
    content overlap (e.g. 'spell') rather than glue words like 'the'."""
    return [t for t in _normalize(text).split() if len(t) >= min_len and t not in STOPWORDS]


def _token_in_words(token: str, words: set) -> bool:
    """Whole-word match with light inflection (s/es/ed/ing) so 'land' matches
    'lands' but 'spell' does NOT match 'spellbook'."""
    if not token:
        return False
    if token in words:
        return True
    for suffix in ("s", "es", "ed", "ing"):
        if token + suffix in words:
            return True
    return False


def check_contradiction(line: str, rule: CanonRule) -> Contradiction | None:
    """Heuristic contradiction scan: the rule says the subject cannot do an action;
    a line that positively asserts the subject performing that action contradicts
    a HARD rule. Negated or failure-framed lines do not contradict. Uses whole-word
    matching to avoid false positives on compound words like 'spell' vs 'spellbook'."""
    if not rule.is_hard:
        return None
    line_words = set(_normalize(line).split())
    subj_tokens = _content_tokens(rule.subject, min_len=2)
    act_tokens = _content_tokens(rule.action, min_len=3)
    mentions_subject = any(_token_in_words(t, line_words) for t in subj_tokens) if subj_tokens else False
    action_present = any(_token_in_words(t, line_words) for t in act_tokens) if act_tokens else False
    if mentions_subject and action_present:
        negators = ("cannot", "cant", "wont", "never", "fails", "misses", "unable")
        if any(n in line_words for n in negators):
            return None
        return Contradiction(
            line=line,
            rule_id=rule.id,
            fix=f"Rephrase so {rule.subject} does not {rule.action}; the rule says they cannot ({rule.reason}).",
        )
    return None


def scan_contradictions(lines: Iterable[str], rules: list[CanonRule]) -> list[Contradiction]:
    out: list[Contradiction] = []
    for line in lines:
        for rule in rules:
            c = check_contradiction(line, rule)
            if c is not None:
                out.append(c)
    return out


def band_distance(a: str | None, b: str | None) -> int:
    return abs(_BANDS.get(a, 1) - _BANDS.get(b, 1))


def voice_band_match(line_profile: dict[str, str | None], guide: VoiceFingerprint) -> list[VoiceDrift]:
    """Return drifts where a line OCEAN band is more than 1 band off the guide."""
    drifts: list[VoiceDrift] = []
    guide_d = guide.as_dict()
    for dim in OCEAN_DIMS:
        expected = guide_d.get(dim)
        actual = line_profile.get(dim)
        if expected is None or actual is None:
            continue
        if band_distance(expected, actual) > 1:
            drifts.append(VoiceDrift(line="", dimension=dim, expected=expected, actual=actual))
    return drifts


def forbidden_word_hits(line: str, forbidden: Iterable[str]) -> list[str]:
    norm_line = _normalize(line)
    return [w for w in forbidden if _normalize(w) and _normalize(w) in norm_line]


def score_consistency(
    lines: list[str],
    rules: list[CanonRule],
    guide: VoiceFingerprint,
    line_profiles: list[dict[str, str | None]] | None = None,
) -> dict:
    """Implement the consistency dimension of sub-scoring-engine (0-100)."""
    contradictions = scan_contradictions(lines, rules)
    drifts: list[VoiceDrift] = []
    if line_profiles:
        for line, prof in zip(lines, line_profiles):
            for d in voice_band_match(prof, guide):
                d.line = line
                drifts.append(d)
    forbidden_hits: list[str] = []
    for line in lines:
        forbidden_hits.extend(forbidden_word_hits(line, guide.forbidden_words))

    score = 50  # base: zero contradictions
    score -= 25 * len(contradictions)
    if score < 0:
        score = 0
    if not drifts:
        score += 30
    else:
        score += max(0, 30 - 10 * len(drifts))
    if not contradictions:
        score += 10
    else:
        score -= 10 * len(contradictions)
    score -= 10 * len(forbidden_hits)
    score = max(0, min(100, score))
    return {
        "score": score,
        "contradictions": [vars(c) for c in contradictions],
        "voice_drift": [vars(d) for d in drifts],
        "forbidden_hits": forbidden_hits,
    }


def internal_contradiction_scan(rules: list[CanonRule]) -> list[tuple[str, str, str]]:
    """Detect HARD-vs-HARD rule pairs that bind the same subject+action."""
    conflicts: list[tuple[str, str, str]] = []
    hard = [r for r in rules if r.is_hard]
    for i, a in enumerate(hard):
        for b in hard[i + 1:]:
            if _normalize(a.subject) == _normalize(b.subject) and _normalize(a.action) == _normalize(b.action):
                conflicts.append((a.id, b.id, f"Both {a.id} and {b.id} bind '{a.subject}' to '{a.action}'."))
    return conflicts


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser(description="Canon-consistency check for idea 221.")
    ap.add_argument("bible", help="path to a lore bible markdown file containing CR- rules")
    ap.add_argument("--lines", help="path to a newline-separated dialogue file to scan", default=None)
    args = ap.parse_args()
    text = open(args.bible, encoding="utf-8").read()
    rules = parse_rules(text)
    print(f"parsed {len(rules)} canon rules")
    if args.lines:
        lines = [l for l in open(args.lines, encoding="utf-8").read().splitlines() if l.strip()]
        result = score_consistency(lines, rules, VoiceFingerprint())
        print(json.dumps(result, indent=2))
