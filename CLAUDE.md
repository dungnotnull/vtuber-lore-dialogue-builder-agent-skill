# CLAUDE.md - VTuber Lore & Interactive Dialogue Builder (Idea 221)

**Skill name:** `vtuber-lore-dialogue-builder`
**Tagline:** Builds consistent VTuber/virtual-character lore bibles and trend-aware interactive dialogue that stays in-persona and on-brand.
**Cluster:** `design-creative-media` (shared with ideas 152, 224, 184)
**Source idea:** 221
**Current phase:** Production-ready deliverable set (Phases 0-5 complete)

## Problem This Skill Solves
VTubers and virtual characters need a coherent backstory (lore) and the ability to
generate fresh, in-character, trend-aware dialogue for streams and content - without
contradicting canon or breaking persona. This skill architects a lore bible with
explicit canon rules, generates interactive dialogue grounded in the established
personality, integrates current internet trends safely, and scores persona
consistency, engagement potential, and content safety.

## Harness Flow Summary
1. **Intake** -> `sub-requirements-gatherer` - character concept, personality, constraints, platform.
2. **Framework selection** -> `sub-evaluation-framework-selector` - archetype + Big Five + engagement model.
3. **Lore architecture** -> `sub-lore-architect` - consistent lore bible + canon rules + voice guide.
4. **Dialogue generation** -> `sub-dialogue-engine` - interactive, in-persona, trend-aware lines.
5. **Scoring** -> `sub-scoring-engine` - persona consistency + engagement + safety.
6. **Roadmap** - content/lore expansion suggestions with continuity hooks.

## Sub-skills
- `sub-requirements-gatherer.md`
- `sub-evaluation-framework-selector.md`
- `sub-lore-architect.md`
- `sub-dialogue-engine.md`
- `sub-scoring-engine.md`

`sub-evaluation-framework-selector` and `sub-scoring-engine` are **shared** across
the `design-creative-media` cluster (ideas 152, 224, 184). See
`INTEGRATION.md` for cross-cluster wiring.

## Tools Required
WebSearch, WebFetch, Read, Write, Bash.

## Knowledge Sources
`SECOND-KNOWLEDGE-BRAIN.md` (archetype library, world-building, parasocial
engagement, platform policy, trend rules, canon-consistency framework).

## Supporting Tools
- `tools/knowledge_updater.py` - crawls character-design + trend + platform-policy
  sources; dedup by URL hash; writes `tools/trend_cache.json` for offline fallback.
- `tests/run_tests.py` - validates skill-file structure, runs knowledge_updater
  unit tests with fixtures, and validates scenario coverage.

## Active Development Tasks
- [x] Scaffold deliverables
- [x] Add archetype library (SECOND-KNOWLEDGE-BRAIN.md section 1)
- [x] Track platform policy + trend updates (sections 5-6, knowledge_updater.py)
- [x] Canon consistency + retcon framework (section 3)
- [x] Test runner + scenarios (tests/)
- [x] Cross-cluster integration (INTEGRATION.md)

## Reference Docs
`PROJECT-detail.md`, `PROJECT-DEVELOPMENT-PHASE-TRACKING.md`, `SECOND-KNOWLEDGE-BRAIN.md`, `INTEGRATION.md`.
