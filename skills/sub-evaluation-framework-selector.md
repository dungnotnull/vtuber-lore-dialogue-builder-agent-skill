---
name: sub-evaluation-framework-selector
description: Selects character archetype, Big Five trait profile, and engagement approach for a virtual character. Shared across the design-creative-media cluster (ideas 152, 224, 184).
---

## Purpose
Ground the character in proven design models so consistency and engagement are
deterministic, not improvised. This sub-skill is **shared**: sibling skills in the
design-creative-media cluster (152, 224, 184) reuse it by passing their own
"character"/"brand voice" profile as input and reading the archetype + trait
profile + engagement approach as output.

## Inputs
The character profile from `sub-requirements-gatherer` (or, for sibling skills,
the equivalent structured profile). Must include at least: theme, traits,
platform, age_rating, audience.

## Procedure

### Step 1 - Choose the primary archetype
Map the concept to one archetype from the library in SECOND-KNOWLEDGE-BRAIN
section 1. Selection rules:
- Primary archetype must fit the stated audience age rating and platform tone.
- If the concept's dominant trait cluster maps unambiguously, choose it.
- If ambiguous, pick the archetype whose voice signature best matches the
  intake's speech patterns and values.

### Step 2 - Choose the optional secondary archetype (gap-moe)
- At most one secondary archetype, creating productive tension, not contradiction.
- Validate compatibility:
  - Compatible: Trickster + Caregiver, Innocent + Magician, Cool + Clumsy.
  - Incompatible: Innocent + Rebel (tone break), Caregiver + Jester-cruel.
- If no productive tension exists, output `secondary: none` (single archetype is fine).

### Step 3 - Map personality to Big Five / OCEAN
Produce a trait profile by scoring each OCEAN dimension Low/Mid/High from the
intake traits. This profile is the **voice fingerprint** the lore-architect
writes to and the scoring-engine matches dialogue against.
- O (Openness): curious/creative traits -> High; routine-bound -> Low.
- C (Conscientiousness): organized/diligent -> High; chaotic/clumsy -> Low.
- E (Extraversion): outgoing/energetic -> High; withdrawn -> Low.
- A (Agreeableness): warm/cooperative -> High; blunt/defiant -> Low.
- N (Neuroticism): easily flustered/anxious -> High; steady -> Low.

### Step 4 - Select the engagement approach
From the parasocial engagement framework (SECOND-KNOWLEDGE-BRAIN section 4),
choose 2-3 primary techniques that fit the archetype:
- Innocent/Caregiver -> direct address + rituals + mild vulnerability.
- Trickster/Jester -> status play + callbacks + reincorporation.
- Magician/Mentor -> rituals + callbacks + co-creation (with guardrails).
- Rebel -> callbacks + anti-authority bond + vulnerability.
- Lover -> direct address + deeper vulnerability + rituals.

### Step 5 - Justify against audience & platform
One paragraph: why this archetype + trait profile + engagement approach fits the
audience age rating and platform policy. Flag any technique that would breach
policy at this age rating (e.g. deeper vulnerability on a general-audience
platform -> tone down).

## Outputs
```yaml
primary_archetype: <name>
secondary_archetype: <name | none>
trait_profile:            # OCEAN, the voice fingerprint
  O: Low | Mid | High
  C: Low | Mid | High
  E: Low | Mid | High
  A: Low | Mid | High
  N: Low | Mid | High
engagement_approach:
  primary_techniques: [<technique>, ...]
  rationale: <string>
justification: <paragraph>
```

## Edge Cases
- **Ambiguous archetype** - present the top 2 candidates with their trade-offs and
  choose the one matching the intake speech patterns; record the runner-up.
- **Conflicting secondary** - drop the secondary rather than create a tone break.
- **Sibling-skill invocation (brand mascot)** - map brand-voice adjectives to
  OCEAN the same way; choose an archetype matching brand personality, not the
  product category.
- **Policy-limiting engagement** - if the chosen engagement technique would breach
  the platform/age policy, substitute a safer technique and note the substitution.

## Quality Gate
- [ ] Primary archetype chosen and library-compatible.
- [ ] Secondary archetype (if any) is compatibility-validated, not contradictory.
- [ ] OCEAN trait profile complete (all five dimensions scored).
- [ ] 2-3 engagement techniques chosen, archetype-appropriate.
- [ ] Justification paragraph addresses audience age + platform policy.

## Example
Input profile: theme "clumsy space-witch", traits [curious, clumsy, earnest,
flustered], YouTube teen.
Output:
```yaml
primary_archetype: Magician
secondary_archetype: Innocent      # gap-moe: powerful-but-clumsy-and-earnest
trait_profile:
  O: High
  C: Low
  E: Mid
  A: High
  N: High
engagement_approach:
  primary_techniques: [rituals, callbacks, mild-vulnerability]
  rationale: Magician roots the wonder/mystic tone; Innocent softens it for a teen
    audience and licenses the clumsy gap-moe. Rituals (opening spellbook bit) and
    callbacks (the misfired summoning) build parasocial consistency; mild
    vulnerability fits teen YouTube policy.
justification: The Magician+Innocent pair fits teen YouTube: wonder-driven, not
  edgy; rituals and callbacks are policy-safe; vulnerability stays mild per
  teen-rated guidelines.
```
