#!/usr/bin/env python3
"""run_tests.py - VTuber Lore & Dialogue Builder (idea 221) test runner.

Validates:
  1. Skill-file structure: every sub-skill + main.md has YAML frontmatter and the
     required sections (Purpose, Procedure, Outputs, Quality Gate).
  2. SECOND-KNOWLEDGE-BRAIN required sections present.
  3. Scenario coverage: tests/test-scenarios.md declares >= 5 scenarios incl.
     trend conflict, canon contradiction, safety blocker, offline trends, each
     with Input/Expected/Pass blocks.
  4. knowledge_updater.py: dedup, scoring, cache, HTML parse on synthetic fixtures.
  5. canon_check.py: rule parsing, contradiction scan, voice-band match, internal
     contradiction scan, consistency scoring on synthetic fixtures.

No network access required. Run:
    python tests/run_tests.py
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.knowledge_updater as ku  # noqa: E402
import tools.canon_check as cc  # noqa: E402

SKILLS = ROOT / "skills"
REQUIRED_SKILL_FILES = [
    "main.md",
    "sub-requirements-gatherer.md",
    "sub-evaluation-framework-selector.md",
    "sub-lore-architect.md",
    "sub-dialogue-engine.md",
    "sub-scoring-engine.md",
]
REQUIRED_SECTIONS = ["Purpose", "Procedure", "Output", "Quality Gate"]
BRAIN = ROOT / "SECOND-KNOWLEDGE-BRAIN.md"
BRAIN_SECTIONS = [
    "Character Archetype Library",
    "World-Building",
    "Narrative Consistency",
    "Parasocial Engagement",
    "Trend Integration Rules",
    "Platform Policy",
    "Self-Update Protocol",
    "Knowledge Update Log",
]


class Results:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.messages: list[str] = []

    def ok(self, name: str) -> None:
        self.passed += 1
        self.messages.append(f"PASS  {name}")

    def fail(self, name: str, detail: str) -> None:
        self.failed += 1
        self.messages.append(f"FAIL  {name} - {detail}")

    def check(self, name: str, cond: bool, detail: str = "") -> None:
        if cond:
            self.ok(name)
        else:
            self.fail(name, detail)


def test_skill_structure(r: Results) -> None:
    for fname in REQUIRED_SKILL_FILES:
        p = SKILLS / fname
        r.check(f"exists:{fname}", p.exists(), "file missing")
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        has_fm = text.startswith("---") and text.count("---") >= 2
        r.check(f"frontmatter:{fname}", has_fm, "missing YAML frontmatter")
        # main.md (harness) requires Role/Workflow/Quality Gate; sub-skills require Purpose/Procedure/Output/Quality Gate.
        if fname == "main.md":
            secs = ["Role", "Workflow", "Quality Gate"]
        else:
            secs = REQUIRED_SECTIONS
        for sec in secs:
            r.check(f"section:{fname}:{sec}", sec.lower() in text.lower(),
                    f"missing section {sec}")


def test_brain_sections(r: Results) -> None:
    text = BRAIN.read_text(encoding="utf-8")
    for sec in BRAIN_SECTIONS:
        r.check(f"brain:{sec}", sec.lower() in text.lower(), f"missing {sec}")


def test_scenario_coverage(r: Results) -> None:
    p = ROOT / "tests" / "test-scenarios.md"
    text = p.read_text(encoding="utf-8")
    scenarios = re.findall(r"^## Scenario \d+", text, flags=re.MULTILINE)
    r.check("scenarios>=5", len(scenarios) >= 5, f"found {len(scenarios)}")
    required_tags = {
        "trend conflict": "trend conflict",
        "canon contradiction": "canon contradiction",
        "safety blocker": "safety blocker",
        "trends unavailable": "trends unavailable",
    }
    lower = text.lower()
    for label, needle in required_tags.items():
        r.check(f"scenario:{label}", needle in lower, f"missing {label} scenario")
    # Each scenario has Input, Expected, Pass.
    blocks = re.split(r"^## Scenario \d+", text, flags=re.MULTILINE)
    for i, b in enumerate(blocks[1:], start=1):
        r.check(f"scenario{i}:input", "**input:**" in b.lower(), "no input block")
        r.check(f"scenario{i}:expected", "**expected:**" in b.lower(), "no expected block")
        r.check(f"scenario{i}:pass", "**pass:**" in b.lower(), "no pass block")


def test_knowledge_updater(r: Results) -> None:
    # url_hash determinism
    r.check("ku:url_hash stable", ku.url_hash("https://x.com") == ku.url_hash("https://x.com"),
            "non-deterministic hash")
    # parse_entries on synthetic html
    html = (
        "<html><head><title>KYM VTuber 2026</title></head><body>"
        "<p>Best vtuber memes of 2026 for character design.</p>"
        '<a href="/memes/foo">Foo Meme 2026</a>'
        '<a href="https://example.com/bar">Bar Trend</a>'
        '<a href="/login">login</a>'
        "</body></html>"
    )
    entries = ku.parse_entries("knowyourmeme", "https://knowyourmeme.com/", html)
    r.check("ku:parse>=2", len(entries) >= 2, f"got {len(entries)}")
    r.check("ku:page_entry_title", "KYM" in entries[0].title, f"title={entries[0].title}")
    # score_entry monotonic on keywords
    e_relevant = ku.Entry("vtuber meme trend", "character design archetype", "https://a.com", "k", 2026)
    e_stale = ku.Entry("weather report", "rainy day forecast", "https://b.com", "k", 2010)
    r.check("ku:score relevance", ku.score_entry(e_relevant) > ku.score_entry(e_stale),
            "scoring not relevance-weighted")
    # dedup + append on temp brain
    tmpdir = Path(tempfile.mkdtemp())
    brain = tmpdir / "brain.md"
    seed_url = "https://seed.com/"
    brain.write_text(
        f"# Brain\n\n## Knowledge Update Log\n- 2026-01-01 - seed (s, 2026) {seed_url} <!--h:{ku.url_hash(seed_url)}-->\n",
        encoding="utf-8",
    )
    orig_brain = ku.BRAIN
    ku.BRAIN = brain
    try:
        dup = ku.Entry("seed", "", seed_url, "s", 2026)
        new = ku.Entry("New vtuber trend", "meme", "https://new.com/t", "k", 2026)
        added = ku.append_entries([dup, new], dry_run=False)
        r.check("ku:dedup_append=1", added == 1, f"added={added}")
        text = brain.read_text(encoding="utf-8")
        r.check("ku:no_dup_seed", text.count(seed_url) == 1, "seed duplicated")
        r.check("ku:new_appended", "https://new.com/t" in text, "new entry not appended")
        # idempotent re-run
        added2 = ku.append_entries([new], dry_run=False)
        r.check("ku:idempotent", added2 == 0, f"re-added {added2}")
    finally:
        ku.BRAIN = orig_brain
    # trend cache dry-run
    cnt = ku.update_trend_cache([e_relevant, e_stale], dry_run=True)
    r.check("ku:cache_dryrun=2", cnt == 2, f"cache={cnt}")
    # trend cache real write + load
    orig_cache = ku.TREND_CACHE
    cache_path = tmpdir / "trend_cache.json"
    ku.TREND_CACHE = cache_path
    try:
        ku.update_trend_cache([e_relevant], dry_run=False)
        loaded = ku.load_trend_cache()
        r.check("ku:cache_load_items", len(loaded.get("items", [])) == 1, "cache load mismatch")
        r.check("ku:cache_has_updated", bool(loaded.get("updated")), "no updated timestamp")
    finally:
        ku.TREND_CACHE = orig_cache


def test_canon_check(r: Results) -> None:
    bible = (
        "# Lore Bible\n"
        "## Canon Rules\n"
        "CR-001 [HARD] Nova cannot land a spell on the first try because her magic "
        "is powerful but unstable. Source: the misfired summoning.\n"
        "CR-002 [HARD] Nova cannot mention real-world deities because she lives in "
        "a fantasy pantheon. Source: world rule WR-03.\n"
        "CR-003 [SOFT] Nova cannot skip her opening ritual because fans expect it. Source: voice guide.\n"
    )
    rules = cc.parse_rules(bible)
    r.check("cc:parse=3", len(rules) == 3, f"got {len(rules)}")
    r.check("cc:hard_count=2", sum(1 for x in rules if x.is_hard) == 2, "hard count wrong")
    # contradiction: line asserts Nova lands a spell on first try
    cons = cc.scan_contradictions(["Nova lands a spell on the very first try today!"], rules)
    r.check("cc:contradiction=1", len(cons) == 1, f"got {len(cons)}")
    r.check("cc:contradiction_rule", cons[0].rule_id == "CR-001", "wrong rule")
    # non-contradiction: failure-framed line
    cons2 = cc.scan_contradictions(["Nova fails to land a spell on the first try again."], rules)
    r.check("cc:failure_not_contradiction", len(cons2) == 0, "false positive on failure line")
    # internal contradiction scan: two HARD rules binding same subject+action
    conflict_bible = (
        "CR-010 [HARD] Nova cannot enter the Forbidden Grove because it is sealed.\n"
        "CR-011 [HARD] Nova cannot enter the Forbidden Grove because it is warded.\n"
    )
    conflicts = cc.internal_contradiction_scan(cc.parse_rules(conflict_bible))
    r.check("cc:internal_conflict=1", len(conflicts) == 1, f"got {len(conflicts)}")
    # voice band match
    guide = cc.VoiceFingerprint(O="High", C="Low", E="Mid", A="High", N="High",
                                forbidden_words=("slur", "deity"))
    drift = cc.voice_band_match({"O": "Low", "C": "Low", "E": "Mid", "A": "High", "N": "Mid"}, guide)
    r.check("cc:drift_O", any(d.dimension == "O" for d in drift), "missed O drift >1 band")
    # score_consistency: clean lines -> high, contradicting line -> low
    clean = cc.score_consistency(
        ["Nova carefully studies her spellbook before the stream."], rules, guide
    )
    r.check("cc:clean_score>=70", clean["score"] >= 70, f"score={clean['score']}")
    bad = cc.score_consistency(
        ["Nova lands a spell on the first try, then says a deity name."], rules, guide
    )
    r.check("cc:bad_has_contradiction", len(bad["contradictions"]) >= 1, "no contradiction")
    r.check("cc:bad_has_forbidden", len(bad["forbidden_hits"]) >= 1, "no forbidden hit")
    r.check("cc:bad_score<clean", bad["score"] < clean["score"], "scoring not monotonic")
    # forbidden word detection
    hits = cc.forbidden_word_hits("she invokes a deity here", guide.forbidden_words)
    r.check("cc:forbidden_deity", "deity" in hits, "missed forbidden word")


def main() -> int:
    r = Results()
    test_skill_structure(r)
    test_brain_sections(r)
    test_scenario_coverage(r)
    test_knowledge_updater(r)
    test_canon_check(r)
    for m in r.messages:
        print(m)
    print(f"\n--- {r.passed} passed, {r.failed} failed ---")
    return 1 if r.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
