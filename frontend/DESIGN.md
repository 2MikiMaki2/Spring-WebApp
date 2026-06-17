# frenchat — Redesigned Design System

A snapshot of the app's **new** visual design, produced from the redesign brief:
*"modern and responsive; brighter colors that stay warm and gentle on the eyes;
rounded components."* This replaces the leftover default-Vue palette documented in
the previous version. It is the **target spec** — the system the screens should
adopt.

**App:** frenchat — a language-practice web app (voice + text chat with an AI
conversation partner). Vue 3 SPA.

**What changed:** the cold near-black dark theme and generic Vue teal-green are
gone. The app now sits on a **warm cream surface** with a single **coral brand
scale** (voice / primary), a **gentle teal** secondary (text), softened neutrals,
larger radii, and a friendly serif accent for greetings. The ad-hoc ~30 hardcoded
hexes collapse into the named tokens below — components should reference tokens,
not literals.

---

## 1. Design principles

- **Warm, not cold.** Every neutral carries a slight warm cast; pure grays and
  blue-blacks are retired. Backgrounds are cream, not white-on-black.
- **Bright but gentle.** Accents are saturated enough to feel fresh, but kept at
  mid lightness so nothing glares. No neon, no pure-black text.
- **Soft geometry.** Generous corner radii and low-contrast warm shadows give
  every surface a rounded, approachable feel.
- **One brand scale, one secondary.** The voice/text semantic split is preserved
  (coral = voice/brand, teal = text), but each is now a single coherent scale
  with a pale tint instead of three near-duplicate values.

---

## 2. Brand & accent colors

### Primary — Coral (brand, primary actions, "voice" mode)
| Role | Hex | Where |
|------|-----|-------|
| Brand / primary | `#EE8A5F` | wordmark, primary CTAs, active nav, "View all" link |
| Primary hover / deep | `#D9774C` | hovers, "VOICE" badge text |
| Coral tint (bg) | `#FCEAE0` | voice icon circle, voice badge bg, log-out hover |
| Coral tint (alt / hairline) | `#F6D9C6` | voice card hover border |
| Pulse ring | `rgba(238,138,95,0.30 → 0)` | voice icon pulse animation |

### Secondary — Teal ("text" mode accent)
| Role | Hex | Where |
|------|-----|-------|
| Teal accent | `#3FA095` | text icon, "TEXT" badge text |
| Teal tint (bg) | `#E5F3F0` | text icon circle, text badge bg |
| Teal tint (border) | `#C8E6E1` | text card hover border |

### Danger — Soft red (stop / destructive)
| Role | Hex | Where |
|------|-----|-------|
| Danger | `#E5705E` | Stop button, delete, errors |
| Danger hover | `#C7553F` | destructive hover |

> Accents share a common mid-lightness / soft-chroma feel and differ mainly in
> hue (coral ≈ warm orange-red, teal ≈ cool green) so voice vs. text stays legible
> while the whole palette reads warm.

---

## 3. Neutrals (warm ramp)

A single warm-tinted scale replaces the old ad-hoc grays. Names are indicative.

| Token | Hex | Use |
|-------|-----|-----|
| `surface-page` | `#FBF6EF` | app background (with warm radial glow to `#FFF6EC`) |
| `surface-raised` | `#FFFFFF` | cards, list container |
| `surface-hover` | `#FCF7F0` | row / list hover |
| `border` | `#F0E6D7` | card & container borders |
| `border-soft` | `#F4ECDF` | inner dividers / list row separators |
| `border-control` | `#E4D8C7` | outlined buttons |
| `text-strong` | `#2E2A26` | headings, card titles |
| `text-body` | `#5C544B` | body, conversation previews |
| `text-muted` | `#9A8F80` | subtitles, descriptions |
| `text-faint` | `#A6967F` | meta dates, section labels |

Page background uses a subtle warm radial gradient:
`radial-gradient(120% 90% at 50% -10%, #FFF6EC, #FBF6EF 46%, #F7F0E6)`.

Shadows are warm and low-contrast, never neutral black:
`0 6px 22px rgba(120,90,55,0.06)` at rest → `0 16px 38px rgba(120,90,55,0.13)` on
hover.

---

## 4. Typography

- **Display / greeting:** `Instrument Serif` (400, occasional italic) — used for
  the "Bonjour, {name}" greeting to add warmth and personality.
- **Logo / wordmark:** `Baloo 2` (700) — rounded, friendly display face used
  *only* for the "frenchat" wordmark (nav + footers). Keeps the brand mark warm
  and distinct from UI text.
- **UI / body:** `Hanken Grotesk` (400/500/600/700), then system stack
  (`-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`).
- **Rendering:** antialiased, `text-rendering: optimizeLegibility`.
- **Common sizes:** greeting `clamp(2.4rem, 5.6vw, 3.6rem)`; card title
  `1.32rem`; body `~1rem`; meta/date `0.86rem`; uppercase section labels
  `0.82rem` with `letter-spacing: 0.08em`.
- **Weights:** body `400`; nav/links/buttons `500–600`; brand, card titles,
  badges, section labels `700`.

---

## 4b. Logo / brand mark

The wordmark **frenchat** is set in **Baloo 2 700**, colored brand coral
`#EE8A5F`. It is paired with a **"typing…" chat-bubble logomark**:

- A white rounded speech bubble (`border-radius: 12px 12px 12px 4px` — the small
  bottom-left corner is the chat tail), `2px` border in `#F0E0D0`.
- Three dots inside: coral `#EE8A5F`, light-coral `#F0A877`, and warm-dark
  `#2E2A26` (the third dot is intentionally dark, not teal, for contrast).
- The mark scales: ~42×35px bubble in the home/welcome nav, ~34×29px in footers.

> The earlier coral mic tile is retired as the primary logo. The mic icon lives
> on only as the **voice-mode** affordance, not the brand mark.

---

## 4c. Typography

- **Container:** main column max-width `980px`, centered; page padding
  `clamp(20px, 4vw, 52px)`.
- **Radii (rounder than before):** mode cards `26px`; list container `20px`;
  buttons / log-out `12px`; badges & pills `999px`; icon circles / avatars `50%`.
- **Buttons:** outlined log-out `9px 18px`, `1.5px` border, `border-radius: 12px`.
- **Borders:** `1px solid` warm tokens (`#F0E6D7` / `#F4ECDF`) for cards, lists,
  dividers.
- **Transitions:** cards `transform/box-shadow/border .2s ease`; links & buttons
  `.15–.18s ease`.
- **Motion:** voice icon retains a gentle `fc-pulse` keyframe (expanding coral
  box-shadow ring, `2.6s` infinite); mode cards lift `translateY(-5px)` on hover;
  "View all" link widens its gap on hover.

---

## 6. Layout & responsiveness

- **Desktop:** top nav bar with warm hairline bottom border. Left: coral wordmark
  + links (Voice / Text / History / Settings). Right: user name + outlined
  Log out button.
- **Responsive strategy — intrinsic, no media-query breakpoints:**
  - Mode cards: `grid-template-columns: repeat(auto-fit, minmax(260px, 1fr))` —
    two-up on wide screens, stacks on narrow.
  - Nav uses `flex-wrap` so links wrap gracefully.
  - Fluid type and spacing via `clamp()` throughout.
- **Icons:** inline stroked SVGs (Feather-style, `stroke-width: 2`,
  `stroke="currentColor"`) — mic (voice) and message bubble (text).

---

## 7. Component-to-color mapping (quick reference)

| Component / view | Dominant colors |
|------------------|-----------------|
| Nav | logo: typing-bubble mark + Baloo 2 coral wordmark `#EE8A5F`, warm neutrals, `#F0E6D7` border |
| Voice card | coral `#EE8A5F` + tint `#FCEAE0`, pulse ring |
| Text card | teal `#3FA095` + tint `#E5F3F0` |
| Greeting | serif `text-strong #2E2A26`, muted subtitle `#9A8F80` |
| Recent list | raised surface `#FFFFFF`, VOICE (coral) / TEXT (teal) pill badges |
| View all link | coral `#EE8A5F` |
| (Stop / delete / errors) | danger `#E5705E` / hover `#C7553F` |

---

## 8. Semantic roles (preserved)

- **Primary / brand** — coral. Wordmark, primary CTAs, active nav, **voice**.
- **Secondary accent** — teal. Distinguishes the **text** experience (badges,
  icon, hover border).
- **Danger** — soft red. Stop, delete, error states.
- **Neutrals** — warm ramp for text hierarchy, borders, surfaces.
- **Tints** — each accent keeps a pale background tint for badges / icon circles /
  card hovers.

---

## 9. Tokens at a glance

```
/* brand — coral */
--brand:          #EE8A5F;
--brand-deep:     #D9774C;
--brand-tint:     #FCEAE0;
--brand-tint-2:   #F6D9C6;

/* secondary — teal */
--accent:         #3FA095;
--accent-tint:    #E5F3F0;
--accent-tint-2:  #C8E6E1;

/* danger */
--danger:         #E5705E;
--danger-deep:    #C7553F;

/* warm neutrals */
--surface-page:   #FBF6EF;
--surface-raised: #FFFFFF;
--surface-hover:  #FCF7F0;
--border:         #F0E6D7;
--border-soft:    #F4ECDF;
--border-control: #E4D8C7;
--text-strong:    #2E2A26;
--text-body:      #5C544B;
--text-muted:     #9A8F80;
--text-faint:     #A6967F;

/* type */
--font-display:   'Instrument Serif', Georgia, serif;
--font-logo:      'Baloo 2', sans-serif;
--font-ui:        'Hanken Grotesk', -apple-system, sans-serif;

/* shape */
--radius-card:    26px;
--radius-panel:   20px;
--radius-control: 12px;
--radius-pill:    999px;
--shadow-rest:    0 6px 22px rgba(120,90,55,0.06);
--shadow-hover:   0 16px 38px rgba(120,90,55,0.13);
```
