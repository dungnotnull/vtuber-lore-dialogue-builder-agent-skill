# VTuber Lore & Interactive Dialogue Builder

Builds consistent VTuber / virtual-character **lore bibles** and generates
**trend-aware interactive dialogue** that stays in-persona, on-brand, and
policy-safe. Part of the `design-creative-media` skill cluster.

## Why
Inconsistent lore and out-of-character responses break the parasocial bond
audiences form with virtual characters. This skill architects a lore bible with
explicit canon rules, writes dialogue grounded in the established voice,
integrates current trends only when they fit the persona and platform policy,
and scores persona consistency, engagement, and safety.

## What's inside
```
skills/
  main.md                          # harness orchestrator + gates
  sub-requirements-gatherer.md     # intake -> character profile
  sub-evaluation-framework-selector.md  # archetype + OCEAN + engagement (shared)
  sub-lore-architect.md            # lore bible + canon rules + voice guide
  sub-dialogue-engine.md           # in-persona dialogue + trend 3-gate
  sub-scoring-engine.md            # consistency/engagement/safety (shared)
tools/
  knowledge_updater.py             # crawl + dedup + cache trends (stdlib)
  canon_check.py                   # deterministic canon-consistency backend
tests/
  test-scenarios.md                # 6 scenarios incl. trend conflict, canon contradiction
  run_tests.py                     # structure + unit + coverage runner (offline)
SECOND-KNOWLEDGE-BRAIN.md          # archetype library, frameworks, policy, trend rules
INTEGRATION.md                      # cross-cluster sharing (ideas 152, 224, 184)
```

## Harness flow
```
Intake -> Framework -> Lore -> Dialogue -> Scoring -> Roadmap
```
Each stage has a gate; failure routes to repair, not silent pass-through.

## Quickstart (agent)
Open `skills/main.md` in your Claude agent and provide a character brief. The
harness runs the six stages and emits a full Lore & Dialogue Package.

## Tools
```bash
# Refresh the knowledge brain + trend cache (weekly or on demand)
python tools/knowledge_updater.py                 # live crawl + append + cache
python tools/knowledge_updater.py --dry-run       # preview, write nothing
python tools/knowledge_updater.py --source knowyourmeme

# Deterministic canon-consistency check on a lore bible
python tools/canon_check.py path/to/bible.md --lines path/to/dialogue.txt
```

## Tests (offline, no network, no models)
```bash
python tests/run_tests.py        # 89 checks: structure, brain, scenarios, updater, canon
```

## Design decisions
1. Canon rules are the single source of truth; dialogue must respect them.
2. Persona consistency outranks trend-chasing.
3. Platform policy + safety are hard, non-overridable gates.
4. Trends integrate only when persona- AND policy-compatible (3-gate).
5. Lore is extensible via continuity hooks.
6. `sub-evaluation-framework-selector` and `sub-scoring-engine` are cluster-shared.

## License
Open source. See repository license.
