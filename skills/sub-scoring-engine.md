---
name: sub-scoring-engine
description: Scores virtual-character output on persona consistency, engagement potential, and content safety. Shared across the design-creative-media cluster (ideas 152, 224, 184).
---

## Purpose
Quantify whether the output stays true to the character and is safe to emit. This
sub-skill is **shared**: sibling skills (152, 224, 184) reuse the same rubric so
scores are comparable across the cluster. Safety is a hard gate - any blocker
blocks emission regardless of how well the other dimensions score.

## Inputs
- The dialogue set (and/or proposed lore addition) to evaluate.
- The lore bible (voice guide with OCEAN fingerprint, canon rules, relationships,
  timeline, continuity hooks).
- The platform + age rating (selects the active policy gate).

## Procedure

### Step 1 - Consistency dimension (0-100)
Run the canon-consistency check (SECOND-KNOWLEDGE-BRAIN section 3) per line, then
aggregate:
1. **Atomic contradiction scan** - each line vs HARD rules + timeline.
   - 0 contradictions -> +50; each contradiction -> -25 (min 0).
2. **Voice-fingerprint match** - each line's OCEAN band vs the voice guide.
   - All within band -> +30; each line > 1 band off -> -10.
3. **Relationship status check** - each line vs current relationship statuses.
   - 0 status conflicts -> +10; each conflict -> -10 (min 0).
4. **Forbidden-word check** - any forbidden word used -> -10 each, and flags a
   consistency blocker (not safety; still must fix).
5. **Retcon check** - any unlogged HARD/timeline change -> -20 + blocker.
Aggregate to 0-100. Below the consistency threshold (default 70) is a repair signal,
not an emission blocker (unless paired with a safety blocker).

### Step 2 - Engagement dimension (0-100)
Score against the parasocial engagement checklist (SECOND-KNOWLEDGE-BRAIN section 4):
- Direct address present -> +20
- >=1 callback to a registered hook/inside-joke -> +20
- Repeatable ritual present -> +20
- "Yes, and" acceptance moment (banter content) -> +20
- Vulnerability calibrated to archetype -> +20
Subtract 10 per technique that is present but mis-calibrated (e.g. vulnerability
too deep for an Innocent on a teen platform). Below the engagement threshold
(default 60) is a soft flag, not a blocker.

### Step 3 - Safety dimension (0-100) + blockers
Apply the platform policy gate (Twitch or YouTube summary, SECOND-KNOWLEDGE-BRAIN
section 6) and the safety blocker taxonomy. Start at 100.
- For each SAFETY-* blocker detected, subtract 40 AND emit the blocker record.
  Any SAFETY-* blocker present -> safety is below threshold and emission is
  blocked (non-overridable).
- SAFETY-OFFBRAND (materially off-brand) is a soft blocker: subtract 20 and flag,
  but does not auto-block unless paired with a hard SAFETY-* blocker.
- 0 hard blockers -> safety passes; score reflects minor deductions only.

### Step 4 - Aggregate scorecard
Produce a scorecard with per-dimension score + rationale + blockers list. Decide:
- **PASS** - zero hard blockers AND consistency >= threshold AND engagement >= threshold.
- **REPAIR** - consistency or engagement below threshold, zero hard blockers ->
  return suggested fixes and route back to the dialogue stage.
- **BLOCK** - any hard SAFETY-* blocker -> do not emit; rewrite/drop the offending
  lines, re-run dialogue, re-score.

## Outputs
```yaml
scorecard:
  consistency:
    score: <0-100>
    rationale: <string>
    contradictions: [{line, rule, fix}]
    voice_drift: [{line, dimension, expected, actual}]
  engagement:
    score: <0-100>
    rationale: <string>
    techniques_present: [...]
    mis_calibrated: [...]
  safety:
    score: <0-100>
    rationale: <string>
    blockers: [{type: SAFETY-*, line, reason}]
  verdict: PASS | REPAIR | BLOCK
  thresholds:
    consistency: 70
    engagement: 60
    safety_block_on: any hard SAFETY-* blocker
```

## Thresholds (configurable per deployment)
- consistency_pass: 70
- engagement_pass: 60
- safety_block: any hard SAFETY-* blocker (non-overridable)

## Edge Cases
- **Trend cited but failed a gate** - if a trend slipped into the dialogue without
  passing the 3-gate, flag SAFETY-OFFBRAND or the appropriate SAFETY-* and BLOCK.
- **Cached-trend staleness** - staleness does not lower safety; it lowers freshness
  (not a scored dimension here) but is noted in the rationale.
- **Sibling-skill invocation (brand mascot)** - substitute the brand voice guide as
  the fingerprint and brand do/don'ts as the canon rules; safety rubric is unchanged.
- **Ambiguous blocker** - if a line is borderline between off-brand and a hard
  SAFETY-* category, treat as the harder category (conservative).

## Quality Gate
- [ ] Consistency scored with contradiction + drift breakdown.
- [ ] Engagement scored with technique checklist.
- [ ] Safety scored with blocker taxonomy; any hard blocker -> BLOCK verdict.
- [ ] Verdict is PASS / REPAIR / BLOCK and matches the threshold logic exactly.
- [ ] Suggested fixes provided for any non-PASS verdict.

## Example (Nova, edgy meme line on teen YouTube)
```yaml
scorecard:
  consistency:
    score: 85
    rationale: No canon contradictions; one line drifts N one band high (fluster
      overshoots to anger) - within tolerance.
  engagement:
    score: 75
    rationale: Ritual + callback + direct address present; vulnerability mild and
      on-archetype.
  safety:
    score: 20
    rationale: One line references a self-harm-adjacent meme; SAFETY-HARM triggered.
    blockers:
      - type: SAFETY-HARM
        line: "{the offending line}"
        reason: self-harm-adjacent meme violates teen YouTube policy
  verdict: BLOCK
  thresholds:
    consistency: 70
    engagement: 60
    safety_block_on: any hard SAFETY-* blocker
```
Action: drop the offending line, re-run Stage 4, re-score.
