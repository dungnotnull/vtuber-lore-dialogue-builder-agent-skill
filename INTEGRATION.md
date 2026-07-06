# INTEGRATION.md - design-creative-media Cluster Cross-Links (Idea 221)

This document defines how `vtuber-lore-dialogue-builder` (221) shares sub-skills
with its sibling skills in the `design-creative-media` cluster:
- **Idea 152** - brand/mascot voice & visual identity builder
- **Idea 224** - creative-content campaign planner
- **Idea 184** - social-media copy & caption generator

Sharing two sub-skills keeps scoring and archetype selection comparable across
the cluster and avoids duplicate maintenance. The shared sub-skills are designed
to accept a generic "profile" input, so a sibling skill can call them without
adopting the VTuber-specific lore bible.

## Shared sub-skills

### `sub-evaluation-framework-selector`
- **VTuber use (221):** selects character archetype + Big Five (OCEAN) profile + engagement approach.
- **Brand/mascot (152):** selects brand-archetype (same library) + brand-voice OCEAN profile + audience-engagement approach. Input = brand-voice profile instead of character profile.
- **Campaign planner (224):** selects campaign archetype (hero/rebel/etc.) + tone OCEAN + engagement approach. Input = campaign brief.
- **Social copy (184):** selects voice archetype for caption tone + OCEAN + engagement hooks. Input = channel persona brief.

Invocation contract: pass a structured profile containing at least
`theme, traits, platform, age_rating, audience`; read back
`primary_archetype, secondary_archetype, trait_profile (OCEAN), engagement_approach, justification`.

### `sub-scoring-engine`
- Same three dimensions (consistency, engagement, safety), same rubric thresholds
  (`consistency_pass=70`, `engagement_pass=60`, `safety_block=any hard SAFETY-*`).
- The "voice fingerprint" is whichever guide the calling skill established:
  - 221 -> lore-bible voice guide + canon rules.
  - 152 -> brand voice guide + brand do/don'ts.
  - 224 -> campaign tone guide + brand-safety rules.
  - 184 -> channel persona guide + platform-policy rules.
- The `tools/canon_check.py` deterministic backend (rule parsing, contradiction
  scan, OCEAN band match, consistency scoring) is reusable verbatim: a sibling
  skill's rules just need to follow the `CR-xxx [HARD|SOFT] {subject} cannot
  {action} because {reason}.` format (for brand: `BR-xxx`; for campaign:
  `CMP-xxx`). `parse_rules` accepts any `XX-###` prefix matching `CR-`? No - it is
  hard-coded to `CR-`. Sibling skills that want the backend should alias their rule
  ids to the `CR-` form for the checker, or use the public functions
  (`_content_tokens`, `scan_contradictions`, `score_consistency`,
  `voice_band_match`) directly with their own rule list constructed via
  `CanonRule(...)`.
- Safety rubric (SAFETY-* taxonomy + Twitch/YouTube policy summaries in
  SECOND-KNOWLEDGE-BRAIN section 6) is shared unchanged across the cluster.

## Cross-link registry

| From | To | Shared artifact | How to invoke |
|------|----|-----------------|---------------|
| 221 | 152 | sub-evaluation-framework-selector | pass brand-voice profile as the intake profile |
| 221 | 224 | sub-evaluation-framework-selector, sub-scoring-engine | pass campaign brief as profile; score campaign copy with shared rubric |
| 221 | 184 | sub-scoring-engine | score social captions against channel persona guide + platform policy |
| 152 | 221 | sub-scoring-engine | brand mascot dialogue scored with shared consistency/engagement/safety rubric |
| 184 | 221 | sub-evaluation-framework-selector | caption tone archetype selection reuses the archetype library |

## Deterministic backend reuse (cross-cluster)
`tools/canon_check.py` exposes:
- `parse_rules(text)` - parse `CR-### [HARD|SOFT] ... cannot ... because ...` rules.
- `CanonRule(...)` - construct rules directly (for sibling skills using `BR-`/`CMP-` ids).
- `scan_contradictions(lines, rules)` - per-line HARD-rule contradiction scan.
- `voice_band_match(line_profile, guide)` - OCEAN band drift detection.
- `score_consistency(lines, rules, guide)` - 0-100 consistency score.
- `internal_contradiction_scan(rules)` - HARD-vs-HARD conflict detection.

Sibling skills import these (the file is dependency-free stdlib) for reproducible,
auditable consistency scoring, then layer their skill-specific engagement and
safety judgment on top.

## Governance
- Changes to a shared sub-skill MUST be validated by `tests/run_tests.py` in this
  repo AND by the sibling skill's own test suite before merge.
- The archetype library (SECOND-KNOWLEDGE-BRAIN section 1) and the SAFETY-*
  taxonomy (section 6) are cluster-canonical; edits require a dated entry in the
  Knowledge Update Log and sign-off across affected skills.
- `tools/knowledge_updater.py` refreshes the trend cache used by all cluster
  skills that integrate trends; sibling skills may point their dialogue/copy
  engines at the same `tools/trend_cache.json` for offline fallback.
