# SECOND-KNOWLEDGE-BRAIN - VTuber Lore & Dialogue Builder (Idea 221)

This document is the living knowledge base for the `vtuber-lore-dialogue-builder` skill.
It codifies persona design, world-building, parasocial engagement, and platform
policy so the harness and its sub-skills can reason against a shared, citable
foundation. The self-update protocol (`tools/knowledge_updater.py`) appends dated,
deduplicated entries to the "Knowledge Update Log" at the bottom.

---

## 1. Character Archetype Library

Archetypes are the load-bearing core of a virtual character. Pick one primary
archetype and at most one secondary archetype (the "gap-moe" pair). Every canon
rule, voice choice, and trend decision must trace back to the chosen archetype(s).

| Archetype | Core drive | Voice signature | Engagement lever | Example VTuber flavor |
|-----------|-------------|-----------------|------------------|------------------------|
| The Innocent | Belonging / safety | Bright, earnest, naive | Protective warmth | "first-time streamer" idol |
| The Trickster | Freedom / disruption | Teasing, ironic, quick | Playful chaos | gremlin / prankster |
| The Mentor | Mastery / giving | Calm, instructive, warm | Guidance & trust | "big sister" lore keeper |
| The Rebel | Liberation | Blunt, defiant, witty | Anti-authority bond | punk / anti-corp rogue |
| The Caregiver | Service / love | Soft, reassuring | Comfort & rituals | comfort-streamer, ASMR-adjacent |
| The Explorer | Discovery | Curious, excitable | Shared discovery | traveler / researcher |
| The Ruler | Control / order | Formal, measured | Loyalty & hierarchy | royal / CEO persona |
| The Creator | Self-expression | Passionate, rambling | Co-creation | artist / composer |
| The Magician | Transformation | Mystical, cryptic | Wonder & ritual | witch / oracle |
| The Hero | Proving worth | Determined, direct | Shared challenge | idol-in-training |
| The Jester | Joy / truth | Goofy, punny | Pure entertainment | comedian / gamer |
| The Lover | Connection | Flirty, devoted | Parasocial intimacy | gachikoi-adjacent |
| Gap-moe (modifier) | Contrast surprise | Switch register | Subverts expectation | tough-but-shy, cool-but-clumsy |

Selection rules:
- Primary archetype must fit the stated audience age rating and platform tone.
- Secondary archetype must create productive tension, not contradiction
  (e.g. Trickster + Caregiver = teasing-but-protective; Innocent + Rebel breaks).
- If the concept conflicts with all archetypes, flag for requirements re-intake.

### Big Five flavoring
Use Big Five traits as a consistency fingerprint, not a label. Map archetype to a
trait profile and keep every line within +/- one band of the profile.
- Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism (OCEAN).
- Each trait scored Low / Mid / High; the profile is the "voice fingerprint" the
  scoring-engine matches generated lines against.

---

## 2. World-Building / Lore Bible Practice

A lore bible is the single source of truth. Borrowed from TV/game writers' rooms,
it has six mandatory sections:

1. **Setting & world rules** - what is possible/impossible in this universe
   (magic system, tech level, physics, geography). Hard rules, not vibes.
2. **Backstory** - origin, inciting events, timeline (ordered, dated).
3. **Relationships** - allies, rivals, family, fans/lore-community, with one-line
   dynamics. Each relationship has a status that can change across arcs.
4. **Voice guide** - speech patterns, vocabulary level, verbal tics, catchphrases,
  emotional range, forbidden words/topics, sentence-length tendency.
5. **Canon rules** - numbered, atomic, testable statements. Each rule is either
   HARD (never break) or SOFT (breakable only with explicit arc justification).
6. **Continuity hooks** - open threads, foreshadowing, planned arcs, callbacks
   registry (the list of inside jokes the audience "owns").

Canon rule format (atomic + testable):
```
CR-001 [HARD] {subject} cannot {action} because {world-rule reason}.
Source: {backstory beat | world rule | relationship}.
```

Continuity hook format:
```
HOOK-{n}: {open thread} -> planned payoff: {arc} -> status: open | seeded | paid-off
```

---

## 3. Narrative Consistency & Canon Enforcement

Consistency outranks trend-chasing. The canon-consistency check is a four-step gate
applied to every proposed line, lore addition, or trend integration:

1. **Atomic contradiction scan** - does the line assert a fact that negates a HARD
   canon rule or a dated timeline entry? If yes -> blocker, suggest fix.
2. **Voice-fingerprint match** - does the line's trait profile (OCEAN) and register
   stay within +/- one band of the voice guide? If drift > one band -> flag.
3. **Relationship status check** - does the line imply a relationship state that
   contradicts the current status field? If yes -> flag for arc approval.
4. **Retcon control** - any change to a HARD rule or dated fact requires a logged
   retcon entry (date, reason, affected rules). Unlogged retcons are blockers.

Retcon ledger entry format:
```
RETCON-{n} {date}: changed {CR-xxx | timeline entry} from {old} to {new}. Reason: {arc justification}. Approved: yes/no.
```

---

## 4. Parasocial Engagement Framework

Audience bonding is built through repeated, consistent, low-stakes intimacy.
Grounded in Horton & Wohl (1956) parasocial interaction theory and Johnstone (1979)
improv principles. Engagement techniques are scored by the scoring-engine.

| Technique | Mechanism | How to deploy | Risk if overused |
|-----------|-----------|---------------|------------------|
| Direct address | Uses viewer name / "you all" | 1-2x per segment | Feels forced |
| Callbacks | References a canon inside-joke | After it's audience-owned | Stale if repeated |
| Vulnerability | Small in-persona confession | Sparingly, arc-aligned | Breaks archetype |
| Rituals | Repeated opener/closer/signature bit | Every stream | Comfort anchor |
| "Yes, and" | Accept chat prompt, build on it | Live improv only | Off-canon drift |
| Reincorporation | Bring back earlier bit | End of session | None if timed |
| Status play | Shift high/low status vs chat | Banter segments | Tone mismatch |
| Audience co-creation | Let chat name/decide minor canon | With HARD-rule guardrails | Canon bloat |

Parasocial engagement checklist (each item scores the engagement dimension):
- [ ] At least one direct-address moment.
- [ ] At least one callback to a registered inside-joke.
- [ ] A repeatable ritual present (opener/closer/signature bit).
- [ ] One improv acceptance ("yes, and") moment.
- [ ] Vulnerability calibrated to archetype (Innocent: mild; Lover: deeper).

---

## 5. Trend Integration Rules

Trends keep a character fresh but are the #1 risk to consistency and safety.
Trends are integrated ONLY when they pass all three gates below.

Trend-fit decision tree:
1. Fetch trend (cite source: KnowYourMeme / Reddit / X). If unavailable -> use
   cached trends from `tools/trend_cache.json` and note staleness.
2. **Persona-fit gate**: does the trend's tone match the archetype + voice band?
   Trickster/Jester -> most memes fit; Innocent/Caregiver -> reject edgy/shock.
3. **Policy-safety gate**: does the trend violate platform community guidelines
   (hateful, sexual, self-harm, illegal, doxxing, harassment)? If yes -> reject,
   log reason, keep persona. This is a HARD blocker, non-overridable.
4. **Canon-fit gate**: can the trend be referenced without asserting a canon
   fact that contradicts a rule? If it forces a canon claim -> reframe as
   in-universe joke or reject.
5. If all three pass -> integrate, cite source + date. If any fail -> reject,
   record in "rejected-trend notes" with the failed gate and reason.

Currency vs. cringe principle: a trend past its peak + 2 weeks reads as cringe
unless reframed through the character's voice; prefer reframing over raw reuse.

---

## 6. Platform Policy & Safety (hard gates)

Policy is a non-negotiable HARD gate. Summaries below are decision aids, not legal
text; always defer to the live platform guidelines when in doubt.

### Twitch Community Guidelines (summary)
- No hateful conduct / harassment (targeted on protected traits).
- No sexual content / nudity; no sexually explicit language targeting minors.
- No threats, violence incitement, self-harm encouragement.
- No illegal goods/services; no gambling promotion to minors.
- Respect DMCA; no unauthorized copyrighted content.
- Age-appropriate: 13+ default; mature-label only where allowed.

### YouTube Community Guidelines (summary)
- No hate speech, harassment, cyberbullying.
- No harmful/dangerous acts, no self-harm content.
- No sexual content / nudity (esp. involving minors -> zero tolerance).
- No spam, deceptive practices, scam content.
- No regulated goods (firearms, drugs) promotion outside policy.
- Child safety: made-for-kids content has stricter limits.

### Safety blocker taxonomy (used by scoring-engine)
- `SAFETY-HATE` hateful/harassing content
- `SAFETY-SEX` sexual content, esp. minor-adjacent
- `SAFETY-HARM` self-harm / violence incitement
- `SAFETY-ILLEGAL` illegal goods/services
- `SAFETY-DOXX` personal/private info exposure
- `SAFETY-COPYRIGHT` unauthorized copyrighted content
- `SAFETY-OFFBRAND` materially off-brand for the archetype (soft blocker)

Any SAFETY-* blocker blocks emission; the line is rewritten or dropped.

---

## 7. Key Reference Frameworks (citable)

| Framework | Source | Use |
|-----------|--------|-----|
| Jungian archetypes | Jung; Campbell, *The Hero with a Thousand Faces* | Character core |
| Big Five / OCEAN | Personality psychology | Trait consistency fingerprint |
| Lore bible practice | TV/game writers' rooms | Canon management |
| Parasocial interaction | Horton & Wohl, 1956 | Audience bonding |
| Improv ("yes, and", status) | Johnstone, *Impro* (1979) | Interactive dialogue |
| Platform community guidelines | Twitch / YouTube | Safety gate |

## 8. Key Research / References

| Title | Source | Year | Link | Relevance |
|-------|--------|------|------|-----------|
| Parasocial Interaction | Horton & Wohl | 1956 | - | Audience bonding |
| Impro | Keith Johnstone | 1979 | book | Interactive dialogue |
| The Hero with a Thousand Faces | Joseph Campbell | 1949 | book | Archetype core |
| Twitch Community Guidelines | Twitch Safety | live | https://safety.twitch.tv/s/article/Community-Guidelines | Safety gate |
| YouTube Community Guidelines | YouTube | live | https://www.youtube.com/howyoutubeworks/policies/community-guidelines/ | Safety gate |
| KnowYourMeme | KYM | live | https://knowyourmeme.com/ | Trend source |
| r/VirtualYoutubers | Reddit | live | https://www.reddit.com/r/VirtualYoutubers/ | Community/trend |

## 9. State-of-the-Art Methods & Tools
LLM persona prompting + persistent memory; character cards (V2/W++ variants);
continuity trackers; trend feeds (X, Reddit, KnowYourMeme); moderation
classifiers; voice-fingerprint similarity scoring.

## 10. Analytical Frameworks
- Canon-consistency check (4-step gate, section 3).
- Voice-fingerprint match (OCEAN band comparison).
- Parasocial engagement checklist (section 4).
- Trend-fit + policy-safety gate (section 5, 6).

## 11. Self-Update Protocol
`tools/knowledge_updater.py` runs weekly (or on demand via CLI): crawls
character-design + trend + policy sources, scores and deduplicates by URL hash,
and appends dated entries to the "Knowledge Update Log" below. A local trend
cache (`tools/trend_cache.json`) is written each run so the dialogue-engine can
fall back when live sources are unreachable.

---

## Knowledge Update Log
- 2026-06-18 - Seed: archetypes, lore-bible practice, parasocial engagement, policy captured.
- 2026-07-06 - Expansion: full archetype library, Big Five flavoring, 4-step canon check, trend-fit decision tree, platform policy summaries, safety blocker taxonomy, retcon ledger, continuity hook format.
