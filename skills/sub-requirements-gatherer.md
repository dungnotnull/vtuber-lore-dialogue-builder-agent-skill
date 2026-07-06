---
name: sub-requirements-gatherer
description: Captures character concept, personality, platform, audience, and existing canon for a virtual character, producing a structured profile that downstream stages can validate against.
---

## Purpose
Define the character and all constraints before any lore or dialogue is written.
A weak intake produces a weak bible; this sub-skill makes intake complete and
machine-checkable so downstream stages never have to guess.

## Inputs
Free-form user brief. May be a sentence, a paragraph, or an existing design doc.

## Procedure

### Step 1 - Capture the concept
- **name** (and any aliases / "lore name" vs "streamer name" split).
- **design** (visual: model style, colors, accessories, distinguishing marks).
- **theme** (one-line high-concept, e.g. "clumsy space-witch").
- **archetype hints** (any archetype the user already has in mind; if none, leave blank for the framework-selector).

### Step 2 - Capture the personality
- **traits** (3-7 adjectives, ordered by prominence).
- **quirks** (verbal tics, physical tics, habits).
- **speech patterns** (vocabulary level, sentence-length tendency, register).
- **values** (what the character cares about / would never compromise).
- **boundaries** (topics to avoid: explicit list, not vague "be careful").

### Step 3 - Capture platform & audience
- **platform** (Twitch / YouTube / app / other) - drives which policy gate applies.
- **age rating** (general / teen / mature) - drives safety strictness.
- **region** (for policy variants, e.g. EU DSA, JP guidelines).
- **audience** (size tier, primary demographic if known).

### Step 4 - Capture existing canon (if any)
- List any prior backstory, relationships, or rules already established.
- Mark each item `HARD` (audience knows it, cannot retcon) or `SOFT` (flexible).
- If none, output `canon: none`.

### Step 5 - Capture the goal
- One of: `full-lore` (bible from scratch), `dialogue-set` (lines for an existing
  character), `ongoing-companion` (long-session continuity plan), `audit` (check
  existing content for consistency/safety).

### Step 6 - Validate completeness
Run the intake against the Quality Gate checklist below. If any mandatory field
is missing, ask a targeted follow-up (one question per missing field) before
producing the output. Do not proceed with guesses on mandatory fields.

## Output Schema
```yaml
name: <string>
concept:
  design: <string>
  theme: <string>
  archetype_hints: [<string> | none]
personality:
  traits: [<string>, ...]            # 3-7, ordered
  quirks: [<string>, ...]
  speech:
    vocabulary_level: low | mid | high
    sentence_length: short | mixed | long
    register: casual | formal | code-switched | ...
  values: [<string>, ...]
  boundaries: [<string>, ...]         # explicit forbidden topics
platform:
  name: twitch | youtube | app | other
  age_rating: general | teen | mature
  region: <string>
  audience: <string>
canon:                                # prior established facts
  - fact: <string>
    hardness: hard | soft
  # or: none
goal: full-lore | dialogue-set | ongoing-companion | audit
```

## Question Bank (use only for missing mandatory fields)
- Design: "What does the model look like - style, colors, signature accessory?"
- Traits: "Three to seven adjectives that describe them, most prominent first?"
- Speech: "Do they speak casual, formal, or switch? Short sentences or rambling?"
- Boundaries: "Any topics this character would never touch?"
- Platform/age: "Which platform, and is the audience general, teen, or mature?"
- Goal: "Do you want a full lore bible, just dialogue lines, an ongoing companion
  plan, or an audit of existing content?"

## Edge Cases
- **Vague brief ("make a cute VTuber")** - ask the 6 question-bank prompts in order.
- **Contradictory traits** ("shy but loud party host") - keep as gap-moe but flag for
  the framework-selector to resolve into a coherent primary + secondary archetype.
- **No platform stated** - default to `youtube`, age `teen`, ask to confirm.
- **Existing canon conflicts with the new brief** - mark conflict, do NOT silently
  retcon; route to the lore-architect's retcon-control step.
- **Mature-rated concept with minor-adjacent themes** - hard-stop; refuse and explain
  the policy conflict. This is non-overridable.

## Quality Gate
- [ ] Personality: traits + speech + values + boundaries all present.
- [ ] Platform: name + age_rating + region present.
- [ ] Audience captured (at least size tier).
- [ ] Existing canon captured or explicitly `none`.
- [ ] Goal set to one of the four valid values.
- [ ] No mandatory field filled by guessing (follow-up asked instead).

## Example (abbreviated)
Input: "A clumsy space-witch VTuber for YouTube, teen audience."
Output:
```yaml
name: Nova
concept:
  design: starry-purple robes, oversized pointed hat, floating spellbook
  theme: clumsy space-witch
  archetype_hints: [magician, gap-moe]
personality:
  traits: [curious, clumsy, earnest, easily-flustered]
  quirks: ["mispronounces spell names", "hat slides over eyes"]
  speech:
    vocabulary_level: mid
    sentence_length: mixed
    register: casual-with-mystic-flavor
  values: [helpfulness, wonder]
  boundaries: [no real-world religion mockery, no self-harm jokes]
platform:
  name: youtube
  age_rating: teen
  region: global
  audience: teen, idol-curious
canon: none
goal: full-lore
```
