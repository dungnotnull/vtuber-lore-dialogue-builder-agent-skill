# Test Scenarios - VTuber Lore & Dialogue (Idea 221)

These six scenarios validate the full harness end-to-end. Each scenario lists the
input, expected behavior, and a pass criterion the scoring-engine or gate must
satisfy. The runnable harness tests/run_tests.py validates skill-file structure,
exercises knowledge_updater.py against synthetic fixtures, and asserts every
scenario below is declared and has a non-empty expected/pass block (coverage gate).

## Scenario 1 - Full lore bible
**Input:** Concept: a clumsy space-witch VTuber for YouTube, teen audience. Goal: full-lore.
**Stages exercised:** Intake -> Framework -> Lore.
**Expected:** Lore bible with all six sections (setting & world rules, backstory &
timeline, relationships, voice guide incl. OCEAN fingerprint, canon rules, continuity
hooks); archetype identified (Magician + Innocent gap-moe); 5-15 atomic canon rules.
**Pass:** Canon rules present + atomic + sourced; voice guide has OCEAN profile;
internal contradiction scan returns zero HARD-vs-HARD / timeline conflicts.

## Scenario 2 - In-persona dialogue
**Input:** From the bible above, request a stream-opening monologue.
**Stages exercised:** Dialogue -> Scoring.
**Expected:** Dialogue matching the voice guide (vocabulary, register, tics,
catchphrases), with at least one callback to a registered continuity hook and a
repeatable ritual.
**Pass:** Voice-fingerprint match within +/- one OCEAN band; engagement checklist
satisfied (direct address + callback + ritual); no forbidden words; consistency >= 70.

## Scenario 3 - Trend conflict
**Input:** A current edgy meme (e.g. self-harm-adjacent shock humor) offered as a
trend on a teen YouTube character.
**Stages exercised:** Dialogue (trend 3-gate) -> Scoring.
**Expected:** Trend rejected on the policy-safety gate with a logged reason; persona
preserved; the rejected-trend notes section records the failed gate.
**Pass:** Trend present in rejected-trend notes, failed gate = policy-safety;
no SAFETY-* blocker emitted in the final dialogue; safety verdict PASS (post-reject).

## Scenario 4 - Canon contradiction caught
**Input:** A proposed line asserts Nova lands a spell on the first try, contradicting
canon rule CR-001 [HARD].
**Stages exercised:** Dialogue -> Scoring -> repair.
**Expected:** Scoring flags a consistency contradiction (CR-001), suggests a fix, and
the dialogue stage is re-run with the corrected line.
**Pass:** Contradiction detected in scorecard.contradictions with the offending line
+ rule + fix; verdict REPAIR; consistency < 70 on the offending pass, >= 70 after fix.

## Scenario 5 - Safety blocker
**Input:** Dialogue drifts toward hateful/harassing content (SAFETY-HATE) on a teen
platform.
**Stages exercised:** Scoring (safety gate).
**Expected:** Safety score drops, a SAFETY-HATE blocker is recorded, verdict = BLOCK,
and the offending line is not emitted; content is rewritten or dropped then re-scored.
**Pass:** Blocker type SAFETY-HATE present; verdict BLOCK on first pass; final emitted
output has zero hard blockers and safety verdict PASS.

## Scenario 6 - Trends unavailable
**Input:** Live trend sources offline.
**Stages exercised:** Dialogue (fallback).
**Expected:** Loads tools/trend_cache.json, marks output cached:{date}, adds a
staleness note, and generates persona-only dialogue (zero live trends integrated).
**Pass:** Output header carries cached + staleness note; trend citations list is empty
or marked cached; persona consistency preserved (consistency >= 70); no crash.

## Coverage gate (enforced by tests/run_tests.py)
- Each scenario has a non-empty Input, Expected, and Pass block.
- >= 1 trend-conflict scenario (3) and >= 1 canon-contradiction scenario (4) present.
- >= 1 safety-blocker scenario (5) and >= 1 offline-trend scenario (6) present.
- Total scenarios >= 5 (this file has 6).
