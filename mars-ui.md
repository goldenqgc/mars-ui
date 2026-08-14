# MARS UI Standard

> On-prem internal-tool UI spec — FastAPI + Jinja2 + Tailwind + HTMX + shadcn-faithful components.
> This document is the binding contract for Claude Code in this repo. All generated UI must conform to it.
> For language rules (conversations in Chinese; code, comments, **user-visible UI text** in English) see `CLAUDE.md`.

---

## 0. Project assumptions (must read)

- **Server-side rendering via `Jinja2Templates`.** No HTML string concatenation in Python.
- **Template layout** (real, current state):
  ```
  templates/
    base.html             # nav + theme toggle + JS bridges (Tabs / Checkbox / theme)
    components/
      mars_ui.html        # all macros — single source of truth
    pages/
      login.html          # show_nav=false → theme toggle floats top-right
      switches_list.html
      switch_detail.html
      logs.html
  static/
    css/base.css          # CSS variables + @font-face + minimal global rules
    fonts/                # inter-latin.woff2 (~48KB) + jetbrains-mono-latin.woff2 (~40KB), self-hosted variable woff2
  app.py                  # FastAPI + Jinja2Templates; routes + fake data + TAILWIND_CONFIG
  tailwind.config.js      # mirrors the tailwind key embedded in base.html
  ```
- **No responsive / mobile support.** Inner-tool, fixed desktop. Use `min-w-[1280px]`; do not write `sm:` / `md:` / `lg:` breakpoint classes.
- **Theme** — `light` (default first visit, **not** OS-aware) and `dark` swapped by toggling `class="light"` ↔ `class="dark"` on `<html>`. CSS variables for both palettes live in §2.1. Toggle is rendered by `ui_theme_toggle()` (§4.13). On pages with the top nav it sits in the right-hand cluster; on nav-less pages (login) `base.html` floats it at `fixed top-4 right-6 z-30`.
- **Server-side first.** Vanilla JS only for pure-client state. The four vanilla-JS areas: select-all checkbox linking in tables, theme toggle, Tabs `data-state` bridge, Checkbox `data-state` bridge. All wired once at the bottom of `base.html` with **delegated** listeners so they survive `hx-swap` re-renders.
- **All UI text is English.** Legacy Chinese UI was removed in v1.2. Mockup tables mock data may use English-only identifiers (e.g. `sw-core-01`) — keep them as-is.

---

## 1. Design philosophy

- **Calm and focused.** Operator-facing tools have high information density; UI must be restrained, free of decorative noise. Critical state (online / offline / warning) must be recognizable at a glance.
- **One source of color.** All visual properties come from CSS variables. No hardcoded HEX/RGB in templates.
- **Server-driven by default.** Anything that touches backend data uses HTMX. Only pure-client UI state (per §6) gets native JS.
- **Auditable writes.** Every button / form submission must have visible in-flight feedback and clear success/error feedback. No silent write.

---

## 2. CSS variables and Tailwind wiring

### 2.1 `static/css/base.css`

CSS variables are **verbatim shadcn/ui (default theme, slate)**, plus two ops-domain extensions (`--success`, `--warning`) and five shadcn chart slots. The same variable names appear in two blocks: `:root, :root.dark` (default) and `:root.light` (override).

```css
/* dark — also bound to :root so plain .dark or no class works */
:root,
:root.dark {
  --background:           240 10% 3.9%;
  --foreground:           0 0% 98%;
  --card:                 240 10% 3.9%;
  --card-foreground:      0 0% 98%;
  --popover:              240 10% 3.9%;
  --popover-foreground:   0 0% 98%;
  --primary:              0 0% 98%;
  --primary-foreground:   240 5.9% 10%;
  --secondary:            240 3.7% 15.9%;
  --secondary-foreground: 0 0% 98%;
  --muted:                240 3.7% 15.9%;
  --muted-foreground:     240 5% 64.9%;
  --accent:               240 3.7% 15.9%;
  --accent-foreground:    0 0% 98%;
  --destructive:         0 62.8% 30.6%;
  --destructive-foreground: 0 0% 98%;
  --border:               240 3.7% 15.9%;
  --input:                240 3.7% 15.9%;
  --ring:                 240 4.9% 83.9%;
  --radius:               0.5rem;

  /* MARS_UI extensions (not in shadcn) */
  --success: 142 71% 45%;
  --warning: 38 92% 50%;

  /* shadcn chart slots (for later use) */
  --chart-1: 220 70% 50%;
  --chart-2: 160 60% 45%;
  --chart-3: 30 80% 55%;
  --chart-4: 280 65% 60%;
  --chart-5: 340 75% 55%;
}

/* light */
:root.light {
  --background:           0 0% 100%;
  --foreground:           240 10% 3.9%;
  --card:                 0 0% 100%;
  --card-foreground:      240 10% 3.9%;
  --popover:              0 0% 100%;
  --popover-foreground:   240 10% 3.9%;
  --primary:              240 5.9% 10%;
  --primary-foreground:   0 0% 98%;
  --secondary:            240 4.8% 95.9%;
  --secondary-foreground: 240 5.9% 10%;
  --muted:                240 4.8% 95.9%;
  --muted-foreground:     240 3.8% 46.1%;
  --accent:               240 4.8% 95.9%;
  --accent-foreground:    240 5.9% 10%;
  --destructive:         0 84.2% 60.2%;
  --destructive-foreground: 0 0% 98%;
  --border:               240 5.9% 90%;
  --input:                240 5.9% 90%;
  --ring:                 240 5% 64.9%;
  --radius:               0.5rem;

  --success: 142 71% 45%;
  --warning: 32 92% 45%;
  --chart-1: 220 70% 50%;
  --chart-2: 160 60% 45%;
  --chart-3: 30 80% 55%;
  --chart-4: 280 65% 60%;
  --chart-5: 340 75% 55%;
}

/* Global font (shadcn modern default = Inter, with platform-first CJK chain). */
html, body {
  font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI',
               Roboto, 'Helvetica Neue', Arial,
               'PingFang SC', 'Microsoft YaHei', 'Hiragino Sans GB',
               'Noto Sans SC', 'Noto Sans CJK SC',
               'Source Han Sans SC', 'WenQuanYi Micro Hei',
               sans-serif;
  background-color: hsl(var(--background));
  color: hsl(var(--foreground));
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-feature-settings: "rlig" 1, "calt" 1;
  text-rendering: optimizeLegibility;
}
```

> Switching timing: a no-flash synchronous `<script>` in `base.html` `<head>` sets the `<html>` class before body renders (see §6 for the contract). As long as `class="dark"` or `class="light"` is on `<html>`, all Tailwind semantic classes (`bg-background`, `text-card-foreground`, etc.) resolve through the right palette automatically.

### 2.2 `tailwind.config.js`

**Required.** Without it `bg-background`, `text-card-foreground`, `border-border` etc. resolve to nothing.

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border) / <alpha-value>)",
        input:   "hsl(var(--input) / <alpha-value>)",
        ring:    "hsl(var(--ring) / <alpha-value>)",
        background: "hsl(var(--background) / <alpha-value>)",
        foreground: "hsl(var(--foreground) / <alpha-value>)",
        primary: {
          DEFAULT: "hsl(var(--primary) / <alpha-value>)",
          foreground: "hsl(var(--primary-foreground) / <alpha-value>)",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary) / <alpha-value>)",
          foreground: "hsl(var(--secondary-foreground) / <alpha-value>)",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive) / <alpha-value>)",
          foreground: "hsl(var(--destructive-foreground) / <alpha-value>)",
        },
        muted: {
          DEFAULT: "hsl(var(--muted) / <alpha-value>)",
          foreground: "hsl(var(--muted-foreground) / <alpha-value>)",
        },
        accent: {
          DEFAULT: "hsl(var(--accent) / <alpha-value>)",
          foreground: "hsl(var(--accent-foreground) / <alpha-value>)",
        },
        popover: {
          DEFAULT: "hsl(var(--popover) / <alpha-value>)",
          foreground: "hsl(var(--popover-foreground) / <alpha-value>)",
        },
        card: {
          DEFAULT: "hsl(var(--card) / <alpha-value>)",
          foreground: "hsl(var(--card-foreground) / <alpha-value>)",
        },
        /* MARS_UI extensions */
        success: "hsl(var(--success) / <alpha-value>)",
        warning: "hsl(var(--warning) / <alpha-value>)",
        "chart-1": "hsl(var(--chart-1) / <alpha-value>)",
        "chart-2": "hsl(var(--chart-2) / <alpha-value>)",
        "chart-3": "hsl(var(--chart-3) / <alpha-value>)",
        "chart-4": "hsl(var(--chart-4) / <alpha-value>)",
        "chart-5": "hsl(var(--chart-5) / <alpha-value>)",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",   /* 6px when --radius=0.5rem */
        sm: "calc(var(--radius) - 4px)",
        xl: "calc(var(--radius) + 4px)",   /* 12px */
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI',
               'Roboto', 'Helvetica Neue', 'Arial',
               'PingFang SC', 'Microsoft YaHei', 'Hiragino Sans GB',
               'Noto Sans SC', 'Noto Sans CJK SC', 'Source Han Sans SC',
               'WenQuanYi Micro Hei', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
};
```

> shadcn's `borderRadius` is derived from `--radius`. Adjusting `--radius` in §2.1 (e.g. to `0.625rem` for a roomier feel) automatically tightens every component, **no template code changes needed**.
>
> The same dict is also embedded into `app.py`'s `TAILWIND_CONFIG` constant and injected into `base.html` via `tailwind.config = {{ tailwind_config | tojson }};` for the CDN build. Keep the three copies in lockstep.

---

## 3. Design conventions

- **Spacing**: 4px grid. Card padding `p-6`, table cell padding `p-4` (or `px-4 py-3` when tighter is needed).
- **Border radius**: derived from `--radius` (default `0.5rem` → `lg=8px / md=6px / sm=4px / xl=12px`). Use `rounded-xl` for cards/tables, `rounded-md` for buttons/inputs/badges, `rounded-lg` for general surfaces. shadcn does **not** use `rounded-full` for status pills.
- **Transitions**: every interactive element carries `transition-colors duration-150 ease-in-out` (shadcn modern; narrower than `transition-all duration-200`).
- **Typography**: body inherits `font-sans` → Inter (from `base.css`). Page h1 is `text-3xl font-semibold tracking-tight`. Card titles `text-lg font-semibold leading-none tracking-tight`.
- **Focus ring**: `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background` — applied uniformly to every interactive element (Button, Input, Select, Checkbox, Badge, Alert, Pagination link, Tabs trigger). **No `ring-1` thin rings.**
- **Disabled**: `disabled:opacity-50 disabled:pointer-events-none`. Never use `disabled:cursor-not-allowed` (different convention).
- **Class ordering**: `[layout] [spacing] [border/background] [text/font] [interactive/state]`. Keep it consistent for grep-ability.

---

## 4. Mars UI Component Library

**Source of truth**: `templates/components/mars_ui.html`. Page templates do `{% import "components/mars_ui.html" as ui %}` at the top. **Do not write equivalents inline in page templates** — if a needed macro is missing, add it here first.

> All macros mirror shadcn/ui's React primitives 1:1 — same DOM structure, same class strings, same focus ring, same disabled handling. The only translation is React → Jinja2 (cva → inline `{% set %}` maps). When in doubt, compare against the live shadcn docs at `https://ui.shadcn.com/docs/components`.

Macros are grouped below by shadcn family:

| § | Family | Macros |
|---|---|---|
| 4.1 | Card | `ui_card_root`, `ui_card_header`, `ui_card_title`, `ui_card_description`, `ui_card_content`, `ui_card_footer`, `ui_card` |
| 4.2 | Button | `ui_button` |
| 4.3 | Badge | `ui_badge`, `ui_status_badge`, `ui_result_badge` |
| 4.4 | Table | `ui_table`, `ui_thead`, `ui_tbody`, `ui_tr`, `ui_th`, `ui_td`, `ui_tr_checkbox` |
| 4.5 | Form | `ui_input`, `ui_select` |
| 4.6 | Alert | `ui_alert`, `ui_alert_title`, `ui_alert_description`, `ui_error_state` (shim) |
| 4.7 | Empty | `ui_empty_root`, `ui_empty_header`, `ui_empty_media`, `ui_empty_title`, `ui_empty_description`, `ui_empty_content`, `ui_empty_state` (shim) |
| 4.8 | Skeleton | `ui_skeleton`, `ui_skeleton_row` |
| 4.9 | Tabs | `ui_tabs`, `ui_tabs_list`, `ui_tabs_trigger`, `ui_tabs_content` |
| 4.10 | Pagination | `ui_pagination_root`, `ui_pagination_content`, `ui_pagination_item`, `ui_pagination_link`, `ui_pagination_previous`, `ui_pagination_next`, `ui_pagination_ellipsis`, `ui_pager` (convenience) |
| 4.11 | Typography | `ui_h1`, `ui_h2`, `ui_h3`, `ui_h4`, `ui_lead`, `ui_large`, `ui_small`, `ui_muted`, `ui_inline_code` |
| 4.12 | Page helpers | `ui_page_header`, `ui_kv` |
| 4.13 | Theme | `ui_theme_toggle` |

### 4.1 Card (shadcn/ui Card — verbatim 1:1)

shadcn's `<Card>` is decomposed into 6 sub-components. We expose all 6 plus a `ui_card(title="…", …)` convenience that internally composes Root + Header + Title + Content, so existing call-sites stay terse.

```jinja
{% macro ui_card_root(class="") %}
<div class="rounded-xl border bg-card text-card-foreground shadow {{ class }}">{{ caller() }}</div>
{% endmacro %}

{% macro ui_card_header(class="") %}
<div class="flex flex-col space-y-1.5 p-6 {{ class }}">{{ caller() }}</div>
{% endmacro %}

{% macro ui_card_title(class="") %}
<h3 class="text-lg font-semibold leading-none tracking-tight {{ class }}">{{ caller() }}</h3>
{% endmacro %}

{% macro ui_card_description(class="") %}
<p class="text-sm text-muted-foreground {{ class }}">{{ caller() }}</p>
{% endmacro %}

{% macro ui_card_content(class="") %}
<div class="p-6 pt-0 {{ class }}">{{ caller() }}</div>
{% endmacro %}

{% macro ui_card_footer(class="") %}
<div class="flex items-center p-6 pt-0 {{ class }}">{{ caller() }}</div>
{% endmacro %}

{% macro ui_card(title=None, class="") %}
<div class="rounded-xl border bg-card text-card-foreground shadow {{ class }}">
  {% if title %}
  <div class="flex flex-col space-y-1.5 p-6">
    <h3 class="text-lg font-semibold leading-none tracking-tight">{{ title }}</h3>
  </div>
  {% endif %}
  <div class="{{ 'p-6 pt-0' if title else 'p-6' }}">{{ caller() }}</div>
</div>
{% endmacro %}
```

### 4.2 Button (shadcn/ui Button — 6 variants × 4 sizes)

```jinja
{% macro ui_button(text, variant="default", size="default",
                   hx_post=None, hx_get=None, hx_target=None, hx_swap=None,
                   hx_confirm=None, type="button", extra_class="") %}
{% set variant_class = {
  "default":     "bg-primary text-primary-foreground hover:bg-primary/90",
  "destructive": "bg-destructive text-destructive-foreground hover:bg-destructive/90",
  "outline":     "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
  "secondary":   "bg-secondary text-secondary-foreground hover:bg-secondary/80",
  "ghost":       "hover:bg-accent hover:text-accent-foreground",
  "link":        "text-primary underline-offset-4 hover:underline"
} %}
{% set size_class = {
  "default": "h-9 px-4 py-2",
  "sm":      "h-8 rounded-md px-3 text-xs",
  "lg":      "h-10 rounded-md px-8",
  "icon":    "h-9 w-9"
} %}
<button type="{{ type }}"
  class="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:opacity-50 disabled:pointer-events-none {{ variant_class[variant] }} {{ size_class[size] }} {{ extra_class }}"
  {% if hx_post %}hx-post="{{ hx_post }}"{% endif %}
  {% if hx_get %}hx-get="{{ hx_get }}"{% endif %}
  {% if hx_target %}hx-target="{{ hx_target }}"{% endif %}
  {% if hx_swap %}hx-swap="{{ hx_swap }}"{% endif %}
  {% if hx_confirm %}hx-confirm="{{ hx_confirm }}"{% endif %}
  hx-indicator="#global-spinner">
  <span>{{ text }}</span>
</button>
{% endmacro %}
```

> shadcn Button has no per-button loading spinner. In-flight feedback is the global `#global-spinner` overlay (`base.html`'s `<div id="global-spinner">` + `htmx-request` class). `disabled:pointer-events-none` and an inline `<svg>` spinner fight each other; the global spinner is the clean solution.

### 4.3 Badge (status pills always use **outline** form)

Three macros: the generic `ui_badge(variant="…")`, the ops-status alias `ui_status_badge("UP"|"DOWN"|"WARNING"|"UNKNOWN")`, and the log-result alias `ui_result_badge("success"|"failed"|"partial")`. **All status indicators use the outline form** — colored border + text on transparent background, matching Meraki / Fortinet / Datadog. Filled `default` is reserved for non-status labels (e.g. "Beta").

```jinja
{% macro ui_badge(variant="default", class="") %}
{% set variant_class = {
  "default":     "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
  "secondary":   "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
  "destructive": "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
  "outline":     "text-foreground border-border",
  "success":     "border-transparent bg-success/15 text-success",
  "warning":     "border-transparent bg-warning/15 text-warning",
  "muted":       "border-transparent bg-muted text-muted-foreground"
} %}
<span class="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 {{ variant_class.get(variant, variant_class['default']) }} {{ class }}">{{ caller() }}</span>
{% endmacro %}

{% macro ui_status_badge(status) %}
{% set tone = {
  "UP":      "border-success/40 text-success",
  "DOWN":    "border-destructive/40 text-destructive",
  "WARNING": "border-warning/40 text-warning",
  "UNKNOWN": "border-border text-muted-foreground bg-muted/30"
} %}
<span class="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 {{ tone.get(status, tone['UNKNOWN']) }}">{{ status }}</span>
{% endmacro %}

{% macro ui_result_badge(result) %}
{% set tone = {
  "success": "border-success/40 text-success",
  "failed":  "border-destructive/40 text-destructive",
  "partial": "border-warning/40 text-warning"
} %}
{% set text = {"success":"Succeeded","failed":"Failed","partial":"Partial"} %}
<span class="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 {{ tone.get(result, 'border-border text-muted-foreground bg-muted/30') }}">{{ text.get(result, result) }}</span>
{% endmacro %}
```

### 4.4 Table (shadcn/ui Table — 9 macros, decoration-free)

**Critical convention: `ui_table` is a scroll container only — no `rounded-xl` / `border` / `bg-card`.** Visual layering comes from the surrounding `<ui_card>` (mirrors shadcn's `<Card><Table/></Card>` usage). Border rules live on the parent nodes (`<thead>` and `<tbody>`), never on individual `<tr>`/`<td>`.

```jinja
{% macro ui_table(class="") %}
<div class="relative w-full overflow-auto {{ class }}">
  <table class="w-full caption-bottom text-sm">{{ caller() }}</table>
</div>
{% endmacro %}

{% macro ui_thead(class="") %}
<thead class="[&_tr]:border-b {{ class }}">{{ caller() }}</thead>
{% endmacro %}

{% macro ui_tbody(id="", class="") %}
<tbody {% if id %}id="{{ id }}"{% endif %} class="[&_tr:last-child]:border-0 {{ class }}">{{ caller() }}</tbody>
{% endmacro %}

{% macro ui_tr(class="") %}
<tr class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted {{ class }}">{{ caller() }}</tr>
{% endmacro %}

{% macro ui_th(text, class="") %}
<th class="h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px] {{ class }}">{{ text }}</th>
{% endmacro %}

{% macro ui_td(class="") %}
<td class="p-4 align-middle [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px] {{ class }}">{{ caller() }}</td>
{% endmacro %}

{% macro ui_tr_checkbox(value, name="selected_ids", id="") %}
{% set cb_id = id if id else "cb-" ~ value %}
{{ ui_checkbox(name=name, value=value, id=cb_id) }}
{% endmacro %}
```

**Canonical example** (`switches_list.html`):

```jinja
{% call ui.ui_card(title="Devices") %}
  {% call ui.ui_table() %}
    {% call ui.ui_thead() %}
      {% call ui.ui_tr() %}
        {{ ui.ui_th("", class="w-10") }}
        {{ ui.ui_th("Name") }}
        {{ ui.ui_th("IP") }}
        {{ ui.ui_th("Model") }}
        {{ ui.ui_th("Status") }}
        {{ ui.ui_th("Last heartbeat") }}
        {{ ui.ui_th(text="Actions", class="text-right") }}
      {% endcall %}
    {% endcall %}
    {% call ui.ui_tbody(id="switch-table-body") %}
      {% for s in switches %}
        {% call ui.ui_tr() %}
          {% call ui.ui_td() %}{{ ui.ui_tr_checkbox(s.id) }}{% endcall %}
          {% call ui.ui_td() %}<a href="/switches/{{ s.id }}" class="font-medium text-primary hover:underline">{{ s.name }}</a>{% endcall %}
          {% call ui.ui_td() %}<code class="font-mono">{{ s.ip }}</code>{% endcall %}
          {% call ui.ui_td() %}{{ s.model }}{% endcall %}
          {% call ui.ui_td() %}{{ ui.ui_status_badge(s.status) }}{% endcall %}
          {% call ui.ui_td() %}{{ s.last_seen }}{% endcall %}
          {% call ui.ui_td(class="text-right") %}
            {{ ui.ui_button("Details", variant="ghost", size="sm",
               hx_get="/switches/" + s.id|string, hx_target="#detail-panel") }}
            {{ ui.ui_button("Reboot", variant="destructive", size="sm",
               hx_post="/switches/" + s.id|string + "/reboot",
               hx_confirm="Reboot " + s.name + "? This action cannot be undone.",
               hx_target="#status-" + s.id|string) }}
          {% endcall %}
        {% endcall %}
      {% endfor %}
    {% endcall %}
  {% endcall %}
{% endcall %}
```

> **Cell-content styling rule** (apply uniformly across all tables). The whole project uses **one font family (Inter)** — no monospace, no second family. Every cell inherits `text-foreground` from the table; only the identifier cell gets a per-cell override:
> - **Identifier cell** (the device name link, the device link in logs): `font-medium text-primary hover:underline`. Bold + branded color so the row has a single visual anchor.
> - **All other cells** (IP, model, timestamp, actor, action label, notes): no inline class. Inherits Inter (sans-serif) like the rest of the page.
> - **Status / result cell**: badge component (carries its own color + small text).
> - **Actions cell**: button variants (each button self-styled).
>
> Result per row: at most **1 inline-class token on text content** (`font-medium text-primary` on the link). IP / model / timestamps / actor / notes are bare strings — same font, same color, no class divergence.
>
> **Project-wide rule: one font, always Inter. No exceptions in rendered UI.**
>
> - **Don't use `<code>` for non-code tokens** (IPs, timestamps, model numbers, MAC addresses, identifiers). Browsers and Tailwind preflight both force mono on `<code>`; use plain `<span>` (or bare strings) so they inherit Inter.
> - **For `<pre>` blocks** (network config snippets, code dumps): keep `<pre>` for whitespace preservation, but add `class="font-sans ..."` to opt out of Tailwind's mono preflight default.
> - **Never** include `font-mono` or any second-family declaration in any cell / label / link / span. The macro library is single-font.
> - The `ui_inline_code` macro (defined in §4.11) renders an inline code-styled pill. It uses `<span>` (not `<code>`) — single font. To make it look truly mono, callers can pass `class="font-mono"`. Until then, it inherits Inter.
>
> Style guide history: an early version loaded JetBrains Mono as a second font and used `font-mono` on IP / timestamp / inline-code classes. Auditing it exposed three way mono could leak through (Tailwind `fontFamily.mono`, the `<code>` browser default, the user agent stylesheet for `<pre>`). v1.2.2 simplified this by removing the second font entirely + switching non-code tokens to `<span>` + adding `font-sans` on the few `<pre>` blocks that need to render in Inter. The `base.css` rule for `code { font-family: inherit }` was tried and abandoned — Tailwind's runtime-injected preflight loads after `base.css`, so any reset was dead.

> **Forbidden**: writing `<table>` / `<thead>` / `<tbody>` / `<tr>` directly in a page template; re-declaring `border-b` or `hover:bg-muted/50` on a `<tr>` or `<td>`. shadcn owns those rules — re-declaring creates the duplicated-border / extra-row bugs we already debugged twice.

### 4.5 Form (Input / Select / Label / Checkbox)

`ui_input` / `ui_select` carry their own `<label>` (server-rendered `<label for="…">`). `ui_tr_checkbox` is the shadcn Checkbox primitive adapted to plain `<input type=checkbox>` — the `data-state` attribute is set on `change` by the JS bridge in §6.

```jinja
{% macro ui_input(name, label, type="text", value="", placeholder="", required=False, class="") %}
<div class="flex flex-col gap-1.5">
  <label for="{{ name }}" class="text-sm font-medium leading-none text-muted-foreground">{{ label }}</label>
  <input type="{{ type }}" id="{{ name }}" name="{{ name }}" value="{{ value }}"
         placeholder="{{ placeholder }}" {% if required %}required{% endif %}
         class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm text-foreground shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 {{ class }}" />
</div>
{% endmacro %}

{% macro ui_select(name, label, options, selected=None, class="") %}
<div class="flex flex-col gap-1.5">
  <label for="{{ name }}" class="text-sm font-medium leading-none text-muted-foreground">{{ label }}</label>
  <select id="{{ name }}" name="{{ name }}"
    class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm text-foreground shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 {{ class }}">
    {% for value, text in options %}
    <option value="{{ value }}" {% if value == selected %}selected{% endif %}>{{ text }}</option>
    {% endfor %}
  </select>
</div>
{% endmacro %}

```



### 4.6 Alert (shadcn/ui Alert + `ui_error_state` back-compat shim)

```jinja
{% macro ui_alert(variant="default", class="") %}
{% set variant_class = {
  "default":     "bg-background text-foreground",
  "destructive": "border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive"
} %}
<div role="alert" class="relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground {{ variant_class.get(variant, variant_class['default']) }} {{ class }}">{{ caller() }}</div>
{% endmacro %}

{% macro ui_alert_title(class="") %}
<h5 class="mb-1 font-medium leading-none tracking-tight {{ class }}">{{ caller() }}</h5>
{% endmacro %}

{% macro ui_alert_description(class="") %}
<div class="text-sm [&_p]:leading-relaxed {{ class }}">{{ caller() }}</div>
{% endmacro %}

{# shim for any old call-site — renders the destructive variant #}
{% macro ui_error_state(message="Operation failed — please retry") %}
{% call ui_alert(variant="destructive") %}
  <svg ...><!-- lucide-style alert icon --></svg>
  {% call ui_alert_title() %}Error{% endcall %}
  {% call ui_alert_description() %}{{ message }}{% endcall %}
{% endcall %}
{% endmacro %}
```

> The `dark:` modifier inside the `border-destructive` rule is harmless here (we're already inside `hsl(var(--...))` resolved per theme), kept verbatim from shadcn.

### 4.7 Empty (shadcn 2024+ Empty primitive — 7 macros + shim)

```jinja
{% macro ui_empty_root(class="") %}
<div class="flex min-h-[400px] flex-col items-center justify-center gap-6 rounded-lg border-dashed border p-6 text-center text-sm text-muted-foreground {{ class }}">{{ caller() }}</div>
{% endmacro %}

{% macro ui_empty_header(class="") %}
<div class="flex max-w-sm flex-col items-center gap-2 text-center {{ class }}">{{ caller() }}</div>
{% endmacro %}

{% macro ui_empty_media(variant="default", class="") %}
{% set variant_class = {
  "default": "flex shrink-0 items-center justify-center [&_svg]:size-8 bg-transparent",
  "icon":    "flex shrink-0 items-center justify-center [&_svg]:size-6 mb-2 [&_svg]:text-foreground bg-muted text-foreground rounded-md border border-border p-2"
} %}
<div class="{{ variant_class.get(variant, variant_class['default']) }} {{ class }}">{{ caller() }}</div>
{% endmacro %}

{% macro ui_empty_title(class="") %}
<h3 class="text-base font-semibold tracking-tight text-foreground {{ class }}">{{ caller() }}</h3>
{% endmacro %}

{% macro ui_empty_description(class="") %}
<p class="text-sm text-muted-foreground {{ class }}">{{ caller() }}</p>
{% endmacro %}

{% macro ui_empty_content(class="") %}
<div class="flex items-center justify-center gap-2 {{ class }}">{{ caller() }}</div>
{% endmacro %}

{% macro ui_empty_state(message="No data") %}
{% call ui_empty_root() %}
  {% call ui_empty_header() %}
    {% call ui_empty_media(variant="icon") %}
      <svg ...><!-- folder icon --></svg>
    {% endcall %}
    {% call ui_empty_title() %}{{ message }}{% endcall %}
  {% endcall %}
{% endcall %}
{% endmacro %}
```

### 4.8 Skeleton

```jinja
{% macro ui_skeleton(class="") %}
<div class="animate-pulse rounded-md bg-muted/50 {{ class }}">{{ caller() }}</div>
{% endmacro %}

{# Row-level helper used by the loadingskeletonshowcase. #}
{% macro ui_skeleton_row(cols=5) %}
<tr class="animate-pulse">
  {% for _ in range(cols) %}
  <td class="p-4 align-middle [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]"><div class="h-4 w-full rounded-md bg-muted/50"></div></td>
  {% endfor %}
</tr>
{% endmacro %}
```

### 4.9 Tabs (shadcn/ui Tabs primitives + JS data-state bridge)

```jinja
{% macro ui_tabs(default_value="", class="") %}
<div data-state="active" data-tabs-root data-default-value="{{ default_value }}" class="{{ class }}">{{ caller() }}</div>
{% endmacro %}

{% macro ui_tabs_list(class="") %}
<div role="tablist" class="inline-flex h-9 items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground {{ class }}">{{ caller() }}</div>
{% endmacro %}

{% macro ui_tabs_trigger(value="", class="") %}
<button type="button" role="tab" data-tabs-trigger data-value="{{ value }}"
  class="inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow {{ class }}">{{ caller() }}</button>
{% endmacro %}

{% macro ui_tabs_content(value="", class="") %}
<div role="tabpanel" data-tabs-content data-value="{{ value }}"
  class="mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 {{ class }}">{{ caller() }}</div>
{% endmacro %}
```

> Click-bridge: a delegated `click` handler in `base.html` reads `[data-tabs-trigger]`, finds the root via `[data-tabs-root]`, flips `data-state="active"` on the clicked trigger (clearing it from siblings), and toggles `hidden` on the matching `[data-tabs-content]`. On first paint the script surfaces whatever `data-state="active"` the server emitted, hiding the rest.
>
> Keyboard navigation (left/right arrows, Home/End) is **not** implemented — Radix provides that, but we don't depend on Radix. Add it by extending the JS bridge if needed.

### 4.10 Pagination (shadcn/ui Pagination — 8 macros + `ui_pager` convenience)

```jinja
{% macro ui_pagination_root(class="") %}
<nav role="navigation" aria-label="pagination" class="mx-auto flex w-full justify-center {{ class }}">{{ caller() }}</nav>
{% endmacro %}

{% macro ui_pagination_content(class="") %}
<ul class="flex flex-row items-center gap-1 {{ class }}">{{ caller() }}</ul>
{% endmacro %}

{% macro ui_pagination_item(class="") %}
<li class="{{ class }}">{{ caller() }}</li>
{% endmacro %}

{% macro ui_pagination_link(href="#", active=False, disabled=False, class="") %}
<a href="{{ href }}" {% if active %}aria-current="page" data-state="active"{% endif %}
  class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-9 w-9 {% if active %}bg-primary text-primary-foreground hover:bg-primary/90{% endif %} {{ class }}">{{ caller() }}</a>
{% endmacro %}

{% macro ui_pagination_previous(href="#", disabled=False, class="") %}
<a href="{{ href }}" rel="prev" {% if disabled %}aria-disabled="true" data-state="disabled"{% endif %}
  class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-9 px-3 gap-1 {{ class }}"><svg .../><span>Previous</span></a>
{% endmacro %}

{% macro ui_pagination_next(href="#", disabled=False, class="") %}
<a href="{{ href }}" rel="next" {% if disabled %}aria-disabled="true" data-state="disabled"{% endif %}
  class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-9 px-3 gap-1 {{ class }}"><span>Next</span><svg .../></a>
{% endmacro %}

{% macro ui_pagination_ellipsis(class="") %}
<span aria-hidden="true" class="flex h-9 w-9 items-center justify-center {{ class }}"><svg .../><span class="sr-only">More pages</span></span>
{% endmacro %}

{# Convenience: render a full shadcn pagination from (current, total). #}
{% macro ui_pager(current=1, total=12, total_count="287 total", class="") %}
{% call ui_pagination_root() %}
  {% call ui_pagination_content(class=class) %}
    {% call ui_pagination_item() %}{{ ui_pagination_previous(disabled=(current <= 1), href="?page=" ~ (current - 1)|string) }}{% endcall %}
    {% call ui_pagination_item() %}{% call ui_pagination_link(active=(current == 1), href="?page=1") %}1{% endcall %}{% endcall %}
    {% if total >= 2 %}
    {% call ui_pagination_item() %}{% call ui_pagination_link(active=(current == 2), href="?page=2") %}2{% endcall %}{% endcall %}
    {% endif %}
    {% if total >= 3 %}
    {% call ui_pagination_item() %}{% call ui_pagination_link(active=(current == 3), href="?page=3") %}3{% endcall %}{% endcall %}
    {% endif %}
    {% if total > 3 %}
    {% call ui_pagination_item() %}{{ ui_pagination_ellipsis() }}{% endcall %}
    {% call ui_pagination_item() %}{% call ui_pagination_link(active=(current == total), href="?page=" ~ total|string) %}{{ total }}{% endcall %}{% endcall %}
    {% endif %}
    {% call ui_pagination_item() %}{{ ui_pagination_next(disabled=(current >= total), href="?page=" ~ (current + 1)|string) }}{% endcall %}
  {% endcall %}
{% endcall %}
<p class="mt-3 text-center text-xs text-muted-foreground">{{ total_count }} · Page {{ current }} of {{ total }}</p>
{% endmacro %}
```

### 4.11 Typography (shadcn docs Typography — 9 macros)

Verbatim from shadcn docs/Typography. Use these when the page-level layout doesn't already provide the right heading scale.

```jinja
{% macro ui_h1(class="") %}<h1 class="scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl {{ class }}">{{ caller() }}</h1>{% endmacro %}
{% macro ui_h2(class="") %}<h2 class="scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight first:mt-0 {{ class }}">{{ caller() }}</h2>{% endmacro %}
{% macro ui_h3(class="") %}<h3 class="scroll-m-20 text-2xl font-semibold tracking-tight {{ class }}">{{ caller() }}</h3>{% endmacro %}
{% macro ui_h4(class="") %}<h4 class="scroll-m-20 text-xl font-semibold tracking-tight {{ class }}">{{ caller() }}</h4>{% endmacro %}
{% macro ui_lead(class="") %}<p class="text-xl text-muted-foreground {{ class }}">{{ caller() }}</p>{% endmacro %}
{% macro ui_large(class="") %}<div class="text-lg font-semibold {{ class }}">{{ caller() }}</div>{% endmacro %}
{% macro ui_small(class="") %}<small class="text-sm font-medium leading-none {{ class }}">{{ caller() }}</small>{% endmacro %}
{% macro ui_muted(class="") %}<p class="text-sm text-muted-foreground {{ class }}">{{ caller() }}</p>{% endmacro %}
{% macro ui_inline_code(class="") %}<code class="relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm font-semibold {{ class }}">{{ caller() }}</code>{% endmacro %}
```

### 4.12 Page-level helpers

```jinja
{% macro ui_page_header(title, subtitle="") %}
<div class="flex items-end justify-between mb-6">
  <div>
    <h1 class="text-3xl font-semibold tracking-tight text-foreground">{{ title }}</h1>
    {% if subtitle %}<p class="text-sm text-muted-foreground mt-1">{{ subtitle }}</p>{% endif %}
  </div>
  <div class="flex items-center gap-2">{{ caller() }}</div>
</div>
{% endmacro %}

{% macro ui_kv(label, value) %}
<div class="flex items-center justify-between py-2 border-b border-border last:border-b-0">
  <span class="text-sm text-muted-foreground">{{ label }}</span>
  <span class="text-sm text-foreground font-medium">{{ value }}</span>
</div>
{% endmacro %}
```

### 4.13 Theme toggle

```jinja
{% macro ui_theme_toggle(class="rounded-md border border-border bg-transparent px-2.5 py-1 text-card-foreground transition-all duration-200 hover:bg-accent") %}
<button id="theme-toggle" type="button" aria-label="Toggle theme" class="{{ class }}">
  <span data-icon="light">🌙</span>
  <span data-icon="dark"  class="hidden">☀</span>
</button>
{% endmacro %}
```

`id="theme-toggle"` is fixed — the global `theme` handler in `base.html` looks it up. Two appearance modes:

- **With nav** (default pages): inlined in the right-hand cluster of the nav header.
- **Without nav** (login): wrapped in a `fixed top-4 right-6 z-30` container with `bg-card/80 backdrop-blur shadow-sm` for visibility against the centered card.

### 4.14 Editable cells + dirty buffer + apply-on-confirm

**Pattern**: cells render as two parallel elements — a `<span data-cell>` (display, default visible) and an `<input>` / `<select data-cell-edit class="hidden">` (edit, swapped in on click). On click, the span hides and the input shows. JS commits the diff into an in-memory `stagedChanges` map on edit/change/blur, marks the cell dirty via `bg-warning/15` (only on the cell content, not the whole `<td>`), and updates the toolbar. Apply opens a confirm modal listing every change. Discard reverts all edits.

This is **shadcn-faithful**: shadcn's `Data Table` demo uses inline click-to-edit for simple per-field changes; bulk apply via a confirm modal is canonical operator-tool UX (Cisco DNA Center / Meraki style).

> Three orthogonal **interaction paths** coexist on one table:
> 1. **Cell click-to-edit** — single port, single field, fastest.
> 2. **Bulk-VLAN toolbar** — checkbox + VLAN `<select>` + Stage button → bulk applies the same VLAN to all selected ports in one cell-staged buffer.
> 3. **Full-row Sheet editor** — pending task; for editing 4+ fields per port in a side panel.
>
> `description` and `PoE` are per-row only (paths 1 and 3); bulk-VLAN only changes VLAN (path 2).

#### 4.14.1 Cell markup

Each editable cell renders **both** modes inline. Only the display span is visible by default; the input/select is `hidden` until clicked.

```jinja
{% call ui.ui_tbody() %}
  {% for port in ports %}
    <tr class="border-b hover:bg-muted/50" data-port-row="{{ port.num }}">

      {% call ui.ui_td() %}
        <input type="checkbox" name="port_ids" value="{{ port.num }}"
               data-port-checkbox role="checkbox" class="..." />
      {% endcall %}

      {% call ui.ui_td() %}<span class="font-medium">{{ port.name }}</span>{% endcall %}

      {% call ui.ui_td() %}
        {% if port.status == "up" %}
          <span class="inline-flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-success"></span><span>Up</span></span>
        {% else %}
          <span class="inline-flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-destructive"></span><span class="text-destructive">Down</span></span>
        {% endif %}
      {% endcall %}

      {# VLAN — click span to swap in <select> with allowed VLAN IDs only. #}
      {% call ui.ui_td() %}
        <span data-cell data-port="{{ port.num }}" data-port-field="vlan"
              data-current="{{ port.vlan }}" data-original="{{ port.vlan }}"
              class="port-cell-anchor inline-flex items-center rounded-md border border-transparent px-2 py-0.5 text-sm font-medium hover:border-input min-w-[5rem] justify-center cursor-pointer">
          {{ port.vlan }}
        </span>
        <select data-cell-edit
                data-port="{{ port.num }}" data-port-field="vlan" data-original="{{ port.vlan }}"
                class="hidden port-edit w-24 rounded-md border border-input bg-background px-2 py-0.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1">
          {% for v in allowed_vlans %}
          <option value="{{ v }}" {% if v == port.vlan %}selected{% endif %}>{{ v }}</option>
          {% endfor %}
        </select>
      {% endcall %}

      {# Mode — read-only badge. Use Sheet for full edit. #}
      {% call ui.ui_td() %}
        {% call ui.ui_badge(variant="secondary") %}{{ port.mode }}{% endcall %}
      {% endcall %}

      {# PoE — click span to swap in <select on/off>. #}
      {% call ui.ui_td() %}
        <span data-cell data-port="{{ port.num }}" data-port-field="poe"
              data-current="{{ 'on' if port.poe else 'off' }}"
              data-original="{{ 'on' if port.poe else 'off' }}"
              class="port-cell-anchor inline-flex items-center rounded-md border border-transparent px-2 py-0.5 text-sm font-medium hover:border-input min-w-[3rem] justify-center cursor-pointer">
          {{ 'on' if port.poe else 'off' }}
        </span>
        <select data-cell-edit
                data-port="{{ port.num }}" data-port-field="poe"
                data-original="{{ 'on' if port.poe else 'off' }}"
                class="hidden port-edit w-20 rounded-md border border-input bg-background px-2 py-0.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1">
          <option value="off" {% if not port.poe %}selected{% endif %}>off</option>
          <option value="on"  {% if     port.poe %}selected{% endif %}>on</option>
        </select>
      {% endcall %}

      {% call ui.ui_td() %}<span class="text-xs text-muted-foreground">{{ port.speed }}</span>{% endcall %}

      {# Description — click span to swap in text input. blur commits + collapses. #}
      {% call ui.ui_td(class="min-w-[14rem]") %}
        <span data-cell data-port="{{ port.num }}" data-port-field="description"
              data-current="{{ port.description }}"
              data-original="{{ port.description }}"
              class="port-cell-anchor inline-flex items-center rounded-md border border-transparent px-2 py-0.5 text-sm hover:border-input cursor-pointer {% if not port.description %}text-muted-foreground italic{% endif %}">
          {{ port.description if port.description else "(no description)" }}
        </span>
        <input type="text" data-cell-edit
               data-port="{{ port.num }}" data-port-field="description"
               data-original="{{ port.description }}"
               value="{{ port.description }}"
               placeholder="(no description)"
               class="hidden port-edit w-full rounded-md border border-input bg-background px-2 py-0.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1" />
      {% endcall %}
    </tr>
  {% endfor %}
{% endcall %}
```

Key attributes on each cell:
- `data-cell` — the display span (default visible)
- `data-cell-edit` — input/select (default `hidden`)
- `data-port` — which port this cell belongs to
- `data-port-field` — which field (`vlan` / `poe` / `description`)
- `data-current` — span's currently displayed value (single source of truth for display)
- `data-original` — the original value before any edit (used to detect dirty state)

#### 4.14.2 Staged-changes toolbar (top of ports card)

Sticky warning-tinted toolbar that appears whenever there's ≥ 1 staged change:

```jinja
<div id="ports-staged-toolbar"
     class="sticky top-14 z-20 -mx-6 -mt-6 mb-4 hidden flex items-center justify-between border-b border-warning/40 bg-warning/10 px-6 py-2 text-sm"
     data-staged-toolbar role="alert" aria-live="polite">
  <div class="flex items-center gap-3">
    <span class="h-2 w-2 rounded-full bg-warning"></span>
    <span><span data-staged-count class="font-semibold">0</span> changes pending</span>
    <button type="button" data-staged-details class="rounded-md px-2 py-0.5 text-xs underline-offset-2 hover:underline">View changes</button>
  </div>
  <div class="flex items-center gap-2">
    <button type="button" data-staged-discard class="...">Discard</button>
    <button type="button" data-staged-apply class="...">Apply changes</button>
  </div>
</div>
```

#### 4.14.3 Apply-confirm modal

shadcn-faithful `<Dialog>` structure (mockup-grade: rendered hidden in DOM, no Radix portal):

```jinja
<div data-confirm-modal
     class="hidden fixed inset-0 z-40 items-center justify-center bg-background/80 backdrop-blur-sm">
  <div role="alertdialog" aria-modal="true" aria-labelledby="confirm-title"
       class="w-full max-w-lg rounded-xl border border-border bg-card text-card-foreground shadow-lg">
    <div class="flex flex-col space-y-1.5 p-6">
      <h2 id="confirm-title" class="text-lg font-semibold tracking-tight">Confirm staged changes</h2>
      <p class="text-sm text-muted-foreground">
        The following <span data-confirm-count>0</span> change(s) will be applied to {{ sw.name }} ({{ sw.ip }}):
      </p>
    </div>
    <div class="px-6 pb-2 max-h-72 overflow-y-auto">
      <ul data-confirm-list class="space-y-1 text-sm"></ul>
    </div>
    <div class="flex items-center justify-end gap-2 p-6 pt-2">
      <button type="button" data-confirm-cancel class="...">Cancel</button>
      <button type="button" data-confirm-submit class="...">Apply <span data-confirm-count-cta>0</span> change(s)</button>
    </div>
  </div>
</div>
```

#### 4.14.4 Server endpoint

```python
@app.post("/switches/{device_id}/ports/bulk-apply")
async def ports_bulk_apply(device_id: int, request: Request):
    form = await request.form()
    raw = form.get("payload", "{}")
    import json as _json
    changes = _json.loads(raw)
    # Real project would commit each change; mockup just counts + replies.
    n_ports = len(changes)
    n_fields = sum(len(v) if isinstance(v, dict) else 1 for v in changes.values())
    return HTMLResponse(
        f'<div class="rounded-md border border-success/30 bg-success/10 px-4 py-3 text-sm text-success">'
        f'Applied <span class="font-semibold">{n_fields}</span> change(s) across '
        f'<span class="font-semibold">{n_ports}</span> port(s) on device #{device_id} (mockup).</div>'
    )
```

> **Note**: declare this route BEFORE any `/switches/{id}/ports/{port_num:int}` route — Starlette evaluates routes in declaration order and the literal `bulk-apply` segment would otherwise be parsed as `port_num="bulk-apply"`.

#### 4.14.5 JS bridge (delegated, in `base.html`)

```js
(function () {
  const staged = {};   // { <port_num>: { <field>: { old, new } } }

  // Click display span → fade out display, fade in editor, focus.
  function enterEdit(display) {
    const td = display.closest('td');
    const edit = td.querySelector('[data-cell-edit]');
    if (!edit) return;
    if (edit.tagName === 'SELECT') edit.value = display.dataset.current;
    display.classList.add('hidden');
    edit.classList.remove('hidden');
    edit.focus();
    if (edit.tagName === 'INPUT' && edit.type === 'text' && typeof edit.select === 'function') {
      setTimeout(() => edit.select(), 0);
    }
  }

  // Edit committed → write back to display, mark dirty, refresh toolbar.
  function exitEdit(display, edit, td, current) {
    const orig = display.dataset.original ?? '';
    const port = display.dataset.port;
    const field = display.dataset.portField;
    display.dataset.current = current;
    const empty = !current;
    display.textContent = empty ? (field === 'description' ? '(no description)' : '') : current;
    if (field === 'description') {
      display.classList.toggle('text-muted-foreground', empty);
      display.classList.toggle('italic', empty);
    }
    edit.classList.add('hidden');
    display.classList.remove('hidden');
    // Dirty highlight applies to the cell content (span or input), NOT the
    // whole <td> — keeps the rest of the row visually clean.
    if (current === orig) {
      delete (staged[port] ?? {})[field];
      if (staged[port] && Object.keys(staged[port]).length === 0) delete staged[port];
      display.classList.remove('bg-warning/15', 'text-warning-foreground', 'border-warning');
      edit.classList.remove('bg-warning/15');
    } else {
      (staged[port] = staged[port] ?? {})[field] = { old: orig, new: current };
      display.classList.add('bg-warning/15', 'text-warning-foreground', 'border-warning');
      edit.classList.add('bg-warning/15');
    }
    refreshToolbar();
  }

  function refreshToolbar() {
    const bar = document.querySelector('[data-staged-toolbar]');
    if (!bar) return;
    const n = Object.values(staged).reduce((s, f) => s + Object.keys(f).length, 0);
    bar.classList.toggle('hidden', n === 0);
    const countEl = bar.querySelector('[data-staged-count]');
    if (countEl) countEl.textContent = String(n);
  }

  // Click span → enter edit.
  document.addEventListener('click', (e) => {
    const display = e.target.closest('[data-cell]');
    if (!display) return;
    enterEdit(display);
  });

  // Change on <select> → commit + exit (select fires change on pick).
  document.addEventListener('change', (e) => {
    const edit = e.target.closest('[data-cell-edit]');
    if (!edit) return;
    const td = edit.closest('td');
    const display = td.querySelector('[data-cell]');
    exitEdit(display, edit, td, edit.value);
  });

  // Blur on <input> → commit + exit (input fires blur on focus loss).
  document.addEventListener('focusout', (e) => {
    const edit = e.target.closest('[data-cell-edit]');
    if (!edit || edit.tagName !== 'INPUT') return;
    setTimeout(() => {
      const td = edit.closest('td');
      if (!td) return;
      const display = td.querySelector('[data-cell]');
      if (!display || edit.classList.contains('hidden')) return;
      exitEdit(display, edit, td, edit.value);
    }, 0);
  });

  // Bulk-VLAN checkbox → count + bulk bar visibility.
  document.addEventListener('change', (e) => {
    const cb = e.target.closest('[data-port-checkbox]');
    if (!cb) return;
    const tbody = cb.closest('tbody');
    const checked = tbody.querySelectorAll('[data-port-checkbox]:checked');
    const n = checked.length;
    const counter = document.querySelector('[data-bulk-selected-count]');
    if (counter) counter.textContent = String(n);
    const bar = document.getElementById('ports-bulk-vlan-bar');
    if (bar) bar.classList.toggle('hidden', n === 0);
  });

  // Toolbar / modal / bulk-VLAN stage — all delegated clicks.
  document.addEventListener('click', (e) => {
    const discard = e.target.closest('[data-staged-discard]');
    if (discard) {
      Object.keys(staged).forEach(p => delete staged[p]);
      document.querySelectorAll('[data-cell]').forEach(display => {
        display.dataset.current = display.dataset.original ?? '';
        display.textContent = display.dataset.current || (display.dataset.portField === 'description' ? '(no description)' : '');
        if (display.dataset.portField === 'description') {
          display.classList.toggle('text-muted-foreground', !display.dataset.current);
          display.classList.toggle('italic', !display.dataset.current);
        }
        display.classList.remove('bg-warning/15', 'text-warning-foreground', 'border-warning');
      });
      document.querySelectorAll('[data-cell-edit]').forEach(e => {
        e.classList.add('hidden');
        e.classList.remove('bg-warning/15');
      });
      document.querySelectorAll('[data-cell]').forEach(d => d.classList.remove('hidden'));
      refreshToolbar();
      return;
    }

    const open = e.target.closest('[data-staged-apply]');
    if (open) { openConfirm(); return; }
    const det = e.target.closest('[data-staged-details]');
    if (det) { openConfirm(); return; }

    const submit = e.target.closest('[data-confirm-submit]');
    if (submit) { closeConfirm(); applyChanges(); return; }
    const cancel = e.target.closest('[data-confirm-cancel]');
    if (cancel) { closeConfirm(); return; }

    // Bulk-VLAN: stage button. Apply the same VLAN to all selected ports.
    const bulk = e.target.closest('[data-bulk-apply-vlan]');
    if (bulk) {
      const sel = document.querySelector('[data-bulk-vlan]');
      const vlan = sel && sel.value;
      if (!vlan) return;
      const ports = [...document.querySelectorAll('[data-port-checkbox]:checked')].map(c => c.value);
      if (!ports.length) return;
      ports.forEach(port => {
        const display = document.querySelector(`[data-cell][data-port="${port}"][data-port-field="vlan"]`);
        if (!display) return;
        const td = display.closest('td');
        if (!td) return;
        display.dataset.current = String(vlan);
        display.textContent = String(vlan);
        const edit = td.querySelector('[data-cell-edit]');
        if (edit) {
          edit.value = String(vlan);
          edit.classList.remove('hidden');
          display.classList.add('hidden');
          setTimeout(() => {
            edit.classList.add('hidden');
            display.classList.remove('hidden');
            exitEdit(display, edit, td, String(vlan));
          }, 80);
        }
      });
      document.querySelectorAll('[data-port-checkbox]:checked]').forEach(c => { c.checked = false; });
      document.getElementById('ports-bulk-vlan-bar')?.classList.add('hidden');
      const counter = document.querySelector('[data-bulk-selected-count]');
      if (counter) counter.textContent = '0';
      return;
    }

    const modal = e.target.closest('[data-confirm-modal]');
    if (modal) { closeConfirm(); }   // backdrop click
  });

  function openConfirm() {
    const modal = document.querySelector('[data-confirm-modal]');
    if (!modal) return;
    const n = Object.values(staged).reduce((s, f) => s + Object.keys(f).length, 0);
    modal.querySelector('[data-confirm-count]').textContent = String(n);
    modal.querySelector('[data-confirm-count-cta]').textContent = String(n);
    const list = modal.querySelector('[data-confirm-list]');
    list.innerHTML = '';
    Object.keys(staged).sort((a,b) => +a - +b).forEach(port => {
      Object.entries(staged[port]).forEach(([field, {old, new: nu}]) => {
        const li = document.createElement('li');
        li.className = 'flex items-center gap-2';
        li.innerHTML = `<span class="font-mono text-warning">Gi1/${port}</span>` +
                       `<span class="rounded bg-muted px-1.5 py-0.5 text-xs">${field}</span>` +
                       `<span class="text-muted-foreground text-xs">${old || '\u2205'} \u2192 <span class="text-foreground font-medium">${nu || '\u2205'}</span></span>`;
        list.appendChild(li);
      });
    });
    modal.classList.replace('hidden', 'flex');
  }
  function closeConfirm() {
    document.querySelector('[data-confirm-modal]')?.classList.replace('flex', 'hidden');
  }

  function applyChanges() {
    const m = location.pathname.match(/\/switches\/(\d+)/);
    const deviceId = m ? m[1] : '0';
    const result = document.getElementById('apply-result');
    fetch(`/switches/${deviceId}/ports/bulk-apply`, {
      method: 'POST',
      body: new URLSearchParams({ payload: JSON.stringify(staged) }),
      headers: { 'HX-Request': 'true', 'HX-Target': 'apply-result', 'HX-Swap': 'innerHTML' },
    }).then(r => r.text()).then(html => {
      htmx.swap(result, html);
      Object.keys(staged).forEach(p => delete staged[p]);
      document.querySelectorAll('[data-cell]').forEach(display => {
        display.dataset.current = display.dataset.original ?? '';
        display.textContent = display.dataset.current || (display.dataset.portField === 'description' ? '(no description)' : '');
        if (display.dataset.portField === 'description') {
          display.classList.toggle('text-muted-foreground', !display.dataset.current);
          display.classList.toggle('italic', !display.dataset.current);
        }
        const td = display.closest('td');
        if (td) td.classList.remove('bg-warning/15');
      });
      refreshToolbar();
    });
  }

  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeConfirm(); });
})();
```

#### 4.14.6 Why this pattern

Click-to-edit keeps the table **read-only by default**: visual noise is minimal until the user engages with a cell. Toggle-based always-edit makes the table feel like a spreadsheet regardless of intent and turns every cell into a noisy input form. The user's eye is drawn to the things they're actually touching.

| Approach | Clicks per single edit | Clicks per bulk-apply same VLAN to N ports | DOM cost | Staged buffer |
| --- | --- | --- | --- | --- |
| Per-row view↔edit toggle (deprecated v1.2.2, removed in v1.2.3) | 3 (Edit → input → Save) | N × 3 + select-all + apply | 2× table rows | No |
| Always-edit inputs (spreadsheet mode) | 1 (typing) | N × 1 + select-all + apply | 1× table rows | No |
| Sheet per row | 3 (Edit → sheet → Apply) | N × 3 + select-all | 1 hidden Sheet | No |
| **Click-to-edit cell + staged buffer (v1.2.3+ canonical)** | **2** (click → input → blur) | **2** (Stage + Apply once) | **1× table rows** | **Yes** |

For "high-density operator tools with bulk operations", the staged-buffer pattern wins on every axis. The always-edit spreadsheet variant is faster per-edit but loses the at-a-glance scanability of a quiet table.
## 5. Operations scenarios: confirmations and config two-step flow

**Confirmation prompts** — all destructive operations go through HTMX's `hx-confirm`, no custom modal:

```jinja
{{ ui.ui_button("Reboot", variant="destructive",
   hx_post="/switches/" + s.id|string + "/reboot",
   hx_confirm="Reboot " + s.name + "? This action cannot be undone.",
   hx_target="#status-" + s.id|string) }}
```

**Config push (two-step, never merged)** — required for any operation that pushes configuration beyond a single action:

1. `hx-post` to `/switches/{id}/preview-config` → returns the diff fragment, swap into the preview region.
2. After user confirmation, `hx-post` to `/switches/{id}/apply-config` → real action.

A single combined endpoint is not allowed.

**Bulk operations** — toolbar above the table drives selected rows; selection state is local (no server roundtrip), per §6.

**In-flight feedback** — every write button specifies `hx-indicator="#global-spinner"` (the button macro hard-codes this). The `#global-spinner` overlay in `base.html` covers the page during the request and is removed on `htmx:afterRequest`.

---

## 6. Pure-client JavaScript (where it's allowed)

**Forbidden** (use HTMX): anything that fetches, submits, or mutates server-side state.

**Allowed** (and should use plain JS — never roundtrip):
- Bulk-action select-all checkbox linkage in tables
- Pure-client filtering of already-loaded data
- Dropdown, Tabs, pagination purely-presentational toggles
- Form validation hints (immediate, before submit)
- Theme toggle (writes `localStorage`, never the server)
- Tabs `data-state` bridge (so shadcn-canonical CSS selectors fire)
- Checkbox `data-state` bridge (translates native `checked` to Radix-style attribute)

**Where the JS lives**: a single script block at the bottom of `<body>` in `base.html`. **Delegated handlers** on `document`, scoped via selectors (`[data-tabs-trigger]`, `#theme-toggle`, `[role="checkbox"]`). Delegation matters because `hx-swap` re-renders DOM nodes without re-binding local listeners — delegation survives re-renders.

**Forbidden** in pages: per-page `<script>` blocks that re-bind on every load. If a page truly needs a one-off handler, attach it inside `{% block scripts %}` using **the same delegated pattern** (`document.addEventListener('change', …)`), not `document.getElementById(...)` which dies on swap.

Example (select-all linkage in `switches_list.html`):

```html
<script>
  document.getElementById('select-all').addEventListener('change', (e) => {
    document.querySelectorAll('input[name="selected_ids"]').forEach(cb => cb.checked = e.target.checked);
    document.getElementById('selected-count').textContent =
      e.target.checked ? document.querySelectorAll('input[name="selected_ids"]').length : 0;
  });
  document.querySelectorAll('input[name="selected_ids"]').forEach(cb => {
    cb.addEventListener('change', () => {
      const total = document.querySelectorAll('input[name="selected_ids"]:checked').length;
      document.getElementById('selected-count').textContent = total;
    });
  });
</script>
```

---

## 7. Claude Code execution contract

1. **Macros first.** Before writing inline styles / divs in a page, check whether `mars_ui.html` already has a macro for it. If not, **add the macro**; do not re-invent the style in the page.
2. **Variables only.** No hardcoded HEX/RGB. Use the Tailwind semantic classes from §2.2 (`bg-background`, `text-card-foreground`, etc.).
3. **JS boundary.** HTMX for any server-data interaction. Native JS only for §6 cases, in `base.html` body-end with delegated listeners.
4. **Write feedback.** Every `hx-post` / `hx-delete` carries `hx-indicator="#global-spinner"`. Config-push operations follow the preview → confirm → execute flow in §5.
5. **Empty / error / loading.** Any list/detail region uses the components from §4.6 / §4.7 / §4.8. Never let an empty list render as a blank table.
6. **No responsive.** Fixed desktop width; never use `sm:` / `md:` / `lg:`.
7. **English UI.** Per `CLAUDE.md`, all user-visible strings are English; spec / comments / identifiers stay English. Conversations with the user are in Chinese.
8. **Mockup = fake data only.** During mockup stage the FastAPI server uses hardcoded `SWITCHES` / `LOGS` lists in `app.py`. No database, no real auth, no Playwright, no responsive work.
9. **Coherent style across shadcn families.** When a new component family is adopted (Alert, Empty, Pagination, etc.) pull the verbatim shadcn class strings. Match `radius`, focus-ring, disabled, hover, padding conventions of existing macros in the same family.
10. **Modify spec before code** for any design change. Update `mars-ui.md` in lockstep with `templates/components/mars_ui.html`. Drift between spec and code is a bug.

---

## 8. Mockup-stage runtime summary

For convenience when working on this stage (not a binding spec for production code):

```bash
cd /opt/mars/mar-ui/mockup
python3 -m uvicorn app:app --host 0.0.0.0 --port 8765
```

Then visit:
- http://127.0.0.1:8765/login (default = light theme; toggle floats top-right)
- http://127.0.0.1:8765/switches
- http://127.0.0.1:8765/switches/1
- http://127.0.0.1:8765/logs

LAN-accessible: http://192.168.25.221:8765/. Firewall has `firewalld` rule `tcp/8765` in zone `public` (runtime + permanent).

---

## Appendix: macro coverage checklist (mockup-stage acceptance)

When the user asks "is everything wired up?" run this:

```bash
grep -rE 'ui\.(card|button|badge|status_badge|result_badge|table|thead|tbody|tr|th|td|tr_checkbox|input|select|alert|empty|skeleton|tabs|pagination|pager|label|checkbox|theme_toggle|page_header|kv|h[1-4]|large|small|muted|inline_code)' templates/pages
```

Every page template referencing a macro should match the official shadcn definition; component-coverage checks (e.g. `[[&_tr]:border-b` for `ui_thead`) can grep the served HTML.
