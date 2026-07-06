# PROJECT-detail.md - VTuber Lore & Interactive Dialogue Builder

## Executive Summary
A harness that gives virtual characters a coherent identity and a renewable voice.
It builds a lore bible with explicit canon rules, generates interactive, in-persona
dialogue that integrates current trends without breaking character, and scores
persona consistency, engagement potential, and content safety. Designed for
VTubers, AI companions, and brand mascots.

## Problem Statement
Inconsistent lore and out-of-character responses break the parasocial bond
audiences form with virtual characters. Manually keeping a character fresh,
trend-relevant, AND consistent is hard, and trend integration risks policy
violations or off-brand content.

## Target Users & Use Cases
- **VTuber** - "Build my character's backstory and a stream-opening monologue." -> lore bible + dialogue.
- **AI companion dev** - "Keep responses in-persona over long sessions." -> canon rules + voice guide.
- **Brand** - "Create a mascot persona and FAQ replies." -> on-brand dialogue.
- **Writer** - "Generate banter referencing today's trends, in character." -> trend-aware lines.
- **Mod team** - "Check this script stays on-brand and policy-safe." -> consistency + safety score.

## Harness Architecture
```
/vtuber-lore-dialogue-builder
  Stage 1 Intake     -> sub-requirements-gatherer         -> character profile
  Stage 2 Framework  -> sub-evaluation-framework-selector -> archetype + engagement model
  Stage 3 Lore       -> sub-lore-architect                -> lore bible + canon rules
  Stage 4 Dialogue   -> sub-dialogue-engine               -> interactive in-persona lines
  Stage 5 Scoring    -> sub-scoring-engine                -> consistency/engagement/safety
  Stage 6 Roadmap    -> content/lore expansion plan with continuity hooks
```

## Full Sub-Skill Catalog
| Sub-skill | Purpose | Inputs | Outputs | Tools | Quality gate |
|-----------|---------|--------|---------|-------|--------------|
| requirements-gatherer | Concept | user | character profile | Read | Personality + platform + audience + boundaries captured |
| framework-selector | Archetype | profile | archetype + trait + engagement | WebSearch | Archetype + trait profile defined |
| lore-architect | Lore bible | concept + archetype | bible + canon rules + voice guide | - | Canon rules + no contradictions |
| dialogue-engine | Dialogue | bible + trends | in-persona lines + citations | WebSearch | In-voice + trend cited + policy-checked |
| scoring-engine | Score | dialogue + bible | scorecard + blockers | - | Consistency + safety scored; blockers enforced |

## Skill File Format Specification
Standard Claude skill format (YAML frontmatter `name` + `description`, then
markdown body with Purpose / Procedure / Outputs / Quality Gate / Examples).

## E2E Execution Flow
Intake -> framework -> lore -> dialogue -> score -> roadmap. Each stage has a
gate; failure routes to repair, not silent pass-through.

Fallback behavior:
- Live trends unreachable -> use cached `tools/trend_cache.json`, note staleness.
- Trend conflicts with persona or policy -> reject trend, keep persona, log reason.
- Canon contradiction detected at scoring -> block, suggest fix, re-run dialogue.
- Safety blocker detected -> content not emitted, rewritten or dropped.

## SECOND-KNOWLEDGE-BRAIN Integration
`knowledge_updater.py` crawls character-design + trend + policy sources, scores
and deduplicates by URL hash, appends dated entries to the brain, and refreshes
the local trend cache for offline fallback.

## Quality Gates
- Lore bible has explicit canon rules; no internal contradictions.
- Dialogue stays in established voice/personality (voice-fingerprint band).
- Trend integration checked against persona AND platform policy (3-gate).
- Safety check for harmful/off-brand content (SAFETY-* blocker taxonomy).
- Engagement techniques grounded in parasocial/improv principles (checklist).

## Test Scenarios
See `tests/test-scenarios.md` (6 scenarios incl. trend conflict, canon
contradiction, safety blocker, offline trends). Run `python tests/run_tests.py`.

## Key Design Decisions
1. Canon rules are the source of truth; dialogue must respect them.
2. Persona consistency outranks trend-chasing.
3. Platform policy + safety are hard gates (non-overridable).
4. Trends integrated only when persona- AND policy-compatible.
5. Lore is extensible (continuity hooks for future arcs).
6. Shared sub-skills (framework-selector, scoring-engine) are cluster-level.

## Cluster Integration
This skill shares `sub-evaluation-framework-selector` and `sub-scoring-engine`
with design-creative-media cluster ideas 152, 224, 184. See `INTEGRATION.md`.
