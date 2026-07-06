---
name: sub-dialogue-engine
description: Generates interactive, in-persona dialogue that integrates current trends only when persona- and policy-compatible, with cited sources and a rejected-trend log.
---

## Purpose
Keep the character fresh without breaking voice or rules. Produce dialogue that an
audience experiences as "this is them," not "this is the model talking."

## Inputs
- The lore bible (voice guide + canon rules + relationships + hooks) from `sub-lore-architect`.
- Current trends (live via WebSearch/WebFetch, or cached from `tools/trend_cache.json`).
- The dialogue brief: content type(s) requested and quantity.

## Procedure

### Step 1 - Lock the voice
Before writing any line, restate the voice fingerprint internally:
vocabulary level, sentence length, register, verbal tics, catchphrases,
emotional range, forbidden words, OCEAN band. Every generated line is matched to
this fingerprint. Lines that drift more than one OCEAN band or use a forbidden
word are rejected before emission.

### Step 2 - Respect canon rules
For each proposed line, run the atomic contradiction scan against HARD rules and
the timeline. A line that asserts a fact negating a HARD rule is rewritten or
dropped - it is never emitted. Relationship references must match current status.

### Step 3 - Pick content types
Cover the requested mix; if unspecified, vary across:
- **stream opener** - ritual + direct address + one callback.
- **banter** - status play, "yes, and" improv with chat.
- **story beat** - advances a continuity hook (status moves toward seeded).
- **audience ritual** - a repeatable signature bit.
- **closer** - reincorporation of an earlier bit + hook tease.

### Step 4 - Generate branching responses (interactivity)
For each common chat prompt type, provide a primary response + 2 branches:
```
PROMPT: {chat prompt type}
  A (in-voice, canon-safe): <line>
  B (yes-and escalation): <line>
  C (callback to inside-joke HOOK-x): <line>
```
All branches must pass the voice + canon gates. "Yes, and" branches accept the
chat premise and build; they never negate the chat (improv principle).

### Step 5 - Integrate trends (3-gate decision tree)
For each candidate trend:
1. Cite source + date (KnowYourMeme / Reddit / X) or mark `cached:{date}`.
2. **Persona-fit gate** - tone matches archetype + voice band? (Trickster/Jester
   fit most memes; Innocent/Caregiver reject edgy/shock.)
3. **Policy-safety gate** - violates any SAFETY-* taxonomy item? If yes -> REJECT,
   log to rejected-trend notes, keep persona. Non-overridable.
4. **Canon-fit gate** - forces a canon fact claim that contradicts a rule? If yes,
   reframe as an in-universe joke or reject.
5. All three pass -> integrate, cite source+date. Any fail -> reject + log.

### Step 6 - Engagement check (parasocial checklist)
Each dialogue set must contain, where the content type allows:
- >=1 direct-address moment
- >=1 callback to a registered inside-joke / hook
- 1 repeatable ritual (opener or signature bit)
- 1 "yes, and" acceptance moment (banter only)
- Vulnerability calibrated to archetype (Innocent: mild; Lover: deeper)

### Step 7 - Flag and log
- Any line that risks canon or policy -> flag inline as `[FLAG: {reason}]`.
- All rejected trends -> "Rejected-Trend Notes" with the failed gate + reason.
- If trends were cached (offline), add a staleness note at the top of the output.

## Output Format
```
# Dialogue Set - {Character} ({content types})
> Trend source: live | cached:{date} | staleness note

## Stream Opener
## Banter (branching)
## Story Beat ({HOOK-x} -> {status})
## Audience Ritual
## Closer

## Trend Citations
- {trend} | {source} {date} | gates: persona-ok policy-ok canon-ok | integrated

## Rejected-Trend Notes
- {trend} | failed: {gate} | reason: {...} | action: kept persona
```

## Edge Cases
- **Trend sources offline** - load `tools/trend_cache.json`, mark output
  `cached:{date}`, add staleness note, generate persona-only dialogue (no live
  trend). Continuity is preserved; freshness is reduced, not broken.
- **All candidate trends fail gates** - emit dialogue with zero integrated trends
  and a full rejected-trend log; do NOT force-fit a failing trend.
- **Chat prompt forces off-canon premise** - branch A stays in-canon (gentle
  redirect in-voice); never break canon to please a chat prompt.
- **Edgy meme on teen platform** - reject on policy-safety gate, log, keep persona.
- **Mature-rated line drift** - if the bible is teen/general, any mature drift is
  a SAFETY-OFFBRAND blocker; rewrite or drop.

## Quality Gate
- [ ] Every line within the voice fingerprint (no forbidden words, OCEAN in band).
- [ ] No line contradicts a HARD canon rule or timeline entry.
- [ ] Trends cited with source + date; each passed all 3 gates or is logged rejected.
- [ ] Engagement checklist satisfied for the content types generated.
- [ ] Branching responses present where interactivity was requested.
- [ ] Offline/cached case handled with staleness note when applicable.

## Example (Nova, stream opener, trend: "isaac newton apple" meme, teen YouTube)
```
## Stream Opener
"Stars above, welcome back! Er, um - I tried to summon a snack today and, well,
the spellbook's floating upside down again. Let's see if THIS one sticks! You all
brought the apples, right? I hear gravity's been taking credit again - rude."
> Trend: "isaac newton apple" | KnowYourMeme 2026-07-05 | gates: persona-ok
> (Magician plays with forces - fits), policy-ok (teen), canon-ok (reframed as
> in-universe joke, no canon claim) | integrated
> Callback: HOOK-01 (the misfired summoning) | Ritual: opening spellbook bit
```
