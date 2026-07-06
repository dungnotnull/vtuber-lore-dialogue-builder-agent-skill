---
name: sub-lore-architect
description: Produces a consistent lore bible with backstory, world rules, relationships, voice patterns, and explicit canon rules for a virtual character.
---

## Purpose
Create the single source of truth the character must obey. Every later stage
(dialogue, scoring, roadmap) reads from this bible and cannot override its HARD
rules. A bible without explicit, atomic canon rules is not a bible.

## Inputs
The character profile from `sub-requirements-gatherer` and the archetype + Big
Five trait profile from `sub-evaluation-framework-selector`.

## Procedure

### Step 1 - Setting & world rules
Write what is possible and impossible in the character's universe.
- Magic/tech level, physics, geography, factions.
- Each world rule is a numbered, atomic statement: `WR-{n}: {statement}`.
- Hard world rules constrain every canon rule and dialogue line.

### Step 2 - Backstory & timeline
- Origin, inciting events, key beats.
- Timeline is an ordered, dated list. Each entry: `{date | era} - {event}`.
- Every later contradiction against a timeline entry is a blocker.

### Step 3 - Relationships
- Allies, rivals, family, fans/lore-community.
- Each entry: `{name} - {role} - {one-line dynamic} - status: {state}`.
- Status can change across arcs but must be tracked (no silent rewrites).

### Step 4 - Voice guide (the voice fingerprint)
This is what the scoring-engine matches dialogue against. Be concrete.
- **vocabulary_level**: low | mid | high
- **sentence_length**: short | mixed | long
- **register**: casual | formal | code-switched | ...
- **verbal_tics**: [<string>, ...] (e.g. "nya~", "er, um")
- **catchphrases**: [<string>, ...]
- **emotional_range**: which emotions the archetype expresses freely vs suppresses
- **forbidden_words**: [<string>, ...]
- **OCEAN_profile**: O/C/E/A/N each Low|Mid|High - the consistency fingerprint

### Step 5 - Canon rules
- Numbered, atomic, testable. Format:
  ```
  CR-{n} [HARD|SOFT] {subject} cannot {action} because {world-rule reason}.
  Source: {backstory beat | world rule | relationship}.
  ```
- HARD rules never break. SOFT rules break only with a logged retcon.
- Aim for 5-15 rules; more rules = more consistency but less creative room.

### Step 6 - Continuity hooks
- Open threads + planned arcs. Format:
  ```
  HOOK-{n}: {open thread} -> planned payoff: {arc} -> status: open | seeded | paid-off
  ```
- Each hook must not contradict a HARD rule or a dated timeline entry.

### Step 7 - Internal contradiction scan
Before emitting the bible, run the canon-consistency check (SECOND-KNOWLEDGE-BRAIN
section 3) on the bible itself:
1. No HARD rule negates another HARD rule or a world rule.
2. No timeline entry contradicts a HARD rule.
3. No relationship status contradicts a backstory beat.
4. No voice-guide trait sits outside the archetype's expected band (flag, do not
   block - voice can refine the archetype).
If any contradiction found -> fix in place, do not emit a contradictory bible.

### Step 8 - Retcon control (only when intake included existing canon)
If the new bible must change a prior HARD fact from intake, log a retcon:
```
RETCON-{n} {date}: changed {CR-xxx | timeline entry} from {old} to {new}.
Reason: {arc justification}. Approved: yes | no.
```
Unapproved/unlogged retcons are blockers. If intake marked a fact HARD, prefer
restructuring the new bible around it over retconning.

## Output Format
```
# Lore Bible - {Character}
## Setting & World Rules
## Backstory & Timeline
## Relationships
## Voice Guide
## Canon Rules
## Continuity Hooks
## Internal Consistency Check Result
## Retcon Ledger (if any)
```

## Edge Cases
- **No existing canon** - skip the retcon ledger; all rules are new.
- **Conflicting intake facts** - flag and ask the requirements-gatherer to resolve
  before building; do not silently pick one.
- **Archetype + theme clash** (e.g. Innocent + dark-gore theme) - flag, suggest a
  compatible secondary archetype or route back to requirements.
- **Mature theme on minor-adjacent platform** - hard-stop per policy gate.
- **Too many HARD rules (>15)** - warn that creative room is shrinking; suggest
  converting some HARD to SOFT.

## Quality Gate
- [ ] All six mandatory bible sections present (setting, backstory, relationships,
      voice, canon rules, continuity hooks).
- [ ] Canon rules are numbered, atomic, and each is HARD or SOFT with a source.
- [ ] Voice guide includes OCEAN_profile (the fingerprint) + forbidden words.
- [ ] At least one continuity hook for an extensible arc.
- [ ] Internal contradiction scan passed (zero HARD-vs-HARD / timeline conflicts).
- [ ] Retcon ledger present if and only if existing canon was changed.

## Example (Voice Guide excerpt - Nova the space-witch)
```yaml
vocabulary_level: mid
sentence_length: mixed
register: casual-with-mystic-flavor
verbal_tics: ["er, um", "stars above"]
catchphrases: ["Let's see if THIS one sticks!"]
emotional_range:
  expresses: [wonder, fluster, pride, sympathy]
  suppresses: [cruelty, cynicism]
forbidden_words: [slurs, real-religion-mockery]
OCEAN_profile:
  O: High
  C: Low
  E: Mid
  A: High
  N: High
```
Canon rule example:
```
CR-001 [HARD] Nova cannot land a spell on the first try because her magic is
powerful but unstable (world rule WR-02).
Source: backstory beat "the misfired summoning".
```
