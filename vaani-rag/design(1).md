# VaaniRAG — Visual Design System

## 1. Design Direction

VaaniRAG should feel like a modern AI research/product interface rather than a generic chatbot.

The visual language should communicate:

- Indian multilingual identity;
- voice-first interaction;
- trustworthy retrieval;
- technical credibility;
- speed and clarity.

Avoid a cluttered "AI dashboard" aesthetic.

## 2. Theme

### Primary theme

Dark-first interface.

Recommended visual direction:

- deep charcoal/navy background;
- warm saffron/orange accent;
- clean white/near-white text;
- muted slate secondary text;
- subtle borders;
- restrained gradients.

The colors are a design direction, not a requirement to hard-code every component to exact hex values.

## 3. Suggested Palette

```text
Background        #0B1020
Surface           #111827
Elevated surface  #172033
Primary accent    #FF8A3D
Secondary accent  #F4C95D
Text              #F8FAFC
Muted text        #94A3B8
Success           #22C55E
Error             #EF4444
Border            #263247
```

Use the accent sparingly for:

- microphone button;
- active language;
- primary CTA;
- important metrics;
- selected evidence.

## 4. Typography

Recommended:

- **Inter** for primary UI text.
- **Noto Sans Devanagari** for Hindi.
- **Noto Sans** for English.
- **Noto Sans Devanagari** also covers Marathi.

Use a strong but not oversized heading hierarchy.

### Suggested scale

```text
Hero heading     40–48 px
Page heading     28–32 px
Section heading  20–24 px
Body             15–16 px
Metadata         12–14 px
Metric           24–32 px
```

## 5. Main Screen

The home screen should prioritize the interaction:

```text
+--------------------------------------------------+
| VaaniRAG                              EN HI MR   |
|--------------------------------------------------|
|                                                  |
|        Ask your question                         |
|        in your language                          |
|                                                  |
|   +------------------------------------------+   |
|   | Type your question...              🎙    |   |
|   +------------------------------------------+   |
|                                                  |
|             [ Ask VaaniRAG ]                    |
|                                                  |
|   Retrieval: 42 ms   Total: 168 ms              |
|                                                  |
+--------------------------------------------------+
```

## 6. Answer Area

The answer should appear before the detailed evidence.

```text
Answer
────────────────────────────

Concise grounded answer...

Sources
────────────────────────────

[1] Retrieved passage...
[2] Retrieved passage...
```

Evidence should be clearly distinguishable from generated text.

## 7. Voice Interaction

The microphone control should be visually obvious.

States:

```text
Idle
Listening
Processing
Completed
Error
```

When listening:

- animate subtly;
- show "Listening...";
- do not overwhelm the screen.

When processing:

- show transcript;
- show a compact processing indicator.

## 8. Language Selector

Use:

```text
English
हिन्दी
मराठी
```

Avoid country flags as the primary language indicator.

## 9. Trust / Grounding UI

When an answer is grounded, show a small indicator such as:

```text
✓ Answer grounded in retrieved evidence
```

If evidence is insufficient:

```text
Not enough evidence found
```

Do not use a misleading "100% accurate" badge.

## 10. Performance UI

Show useful, real measurements:

```text
Retrieval   43 ms
Generation  91 ms
Total      157 ms
```

Do not show invented numbers.

## 11. Judge Demo Mode

A small optional technical panel can show:

- language;
- Top-K;
- retrieved chunk count;
- retrieval latency;
- embedding latency;
- end-to-end latency;
- vector DB status.

Keep it secondary to the main user experience.

## 12. Responsive Design

The application should work on:

- desktop;
- tablet;
- mobile.

The microphone interaction should remain easy to access on mobile.

## 13. Design Principle

The application should communicate:

> **Fast retrieval, grounded answers, Indian languages, voice-first interaction.**
