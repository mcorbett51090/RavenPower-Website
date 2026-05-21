#!/usr/bin/env python3
"""Regenerate the Stack section in site/index.html from site/repo-guide.html.

The guide is the source of truth — it's regenerated upstream from the
RavenClaude plugins repo. This script keeps the marketing site's Stack
section in sync by parsing the guide's plugin cards and INDEX literal,
then writing the resulting markup into site/index.html between marker
comments.

Idempotent: run it any number of times, the output is determined entirely
by repo-guide.html.

Usage: python3 scripts/build_stack.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
GUIDE = SITE / "repo-guide.html"
INDEX_HTML = SITE / "index.html"

# Chip + stat ordering. Kinds not listed here are still rendered, appended
# in alphabetical order at the end.
KIND_ORDER = ["agent", "skill", "hook", "rule", "template", "mcp"]

# Which kinds contribute to the top-of-section global counts. Rules and
# MCP are real but quieter — leaving them out of the headline numbers.
STAT_KINDS = ["agent", "skill", "hook", "template"]

# Singular / plural labels for chips. Defaults: capitalize + 's'.
KIND_LABEL_SINGULAR = {
    "agent": "Agent",
    "skill": "Skill",
    "hook": "Hook",
    "rule": "Rule",
    "template": "Template",
    "mcp": "MCP server",
}
KIND_LABEL_PLURAL = {k: v + "s" for k, v in KIND_LABEL_SINGULAR.items()}


# ---------------------------------------------------------------------------
# Parsing repo-guide.html
# ---------------------------------------------------------------------------

PLUGIN_HEADER_RE = re.compile(
    r'<article class="plugin-card" data-plugin="(?P<slug>[^"]+)"[^>]*>\s*'
    r'<header class="plugin-header">\s*'
    r'<div class="plugin-title">\s*'
    r"<h2>(?P<name>[^<]+)</h2>\s*"
    r'<span class="version">(?P<version>[^<]+)</span>\s*'
    r"</div>\s*"
    r'<p class="plugin-desc">(?P<desc>.+?)</p>',
    re.DOTALL,
)


def extract_plugins(guide_html: str) -> list[dict]:
    """Return plugins in DOM order with slug, name, version, desc."""
    plugins = []
    for m in PLUGIN_HEADER_RE.finditer(guide_html):
        plugins.append({
            "slug": m.group("slug"),
            "name": m.group("name").strip(),
            "version": m.group("version").strip(),
            "desc": _clean_text(m.group("desc")),
        })
    if not plugins:
        raise SystemExit("No <article class='plugin-card'> blocks found in repo-guide.html")
    return plugins


def extract_index(guide_html: str) -> list[dict]:
    """Return the flat INDEX list of {plugin, kind, name, description, path}."""
    # INDEX is a single-line JS literal: `  const INDEX = [...];`
    for line in guide_html.splitlines():
        s = line.strip()
        if s.startswith("const INDEX"):
            # strip prefix `const INDEX = ` and trailing `;`
            payload = s[len("const INDEX = "):].rstrip(";").strip()
            return json.loads(payload)
    raise SystemExit("INDEX literal not found in repo-guide.html")


def _clean_text(s: str) -> str:
    """Collapse whitespace runs from an HTML inner text capture."""
    return re.sub(r"\s+", " ", s).strip()


def first_sentence(s: str) -> str:
    """Return the first sentence of s — substring up to first '. '."""
    s = s.strip()
    # Some upstream item descriptions start with markdown-ish 'Purpose:**'
    # or similar leading noise; strip a leading bold marker pair.
    s = re.sub(r"^[A-Za-z]+:\*\*\s*", "", s)
    i = s.find(". ")
    if i == -1:
        return s
    return s[: i + 1]


def short_desc(s: str, cap: int = 280) -> str:
    """Trim description for a marketing card.

    Prefer the first sentence if it fits under `cap`. Otherwise, cut at the
    last clause break (`, `, ` — `, ` (`) before `cap` so we don't snap
    mid-word, and append an ellipsis. Used for plugin-level descriptions
    that are too verbose in the source guide.
    """
    s = s.strip()
    s = re.sub(r"^[A-Za-z]+:\*\*\s*", "", s)
    period = s.find(". ")
    if 0 < period <= cap:
        return s[: period + 1]
    if len(s) <= cap:
        return s
    window = s[:cap]
    candidates = [window.rfind(sep) for sep in (", ", " — ", " (")]
    cut = max(candidates)
    if cut > cap // 3:  # only honour cuts that aren't suspiciously early
        return window[:cut].rstrip(" ,—(") + "…"
    return window.rstrip() + "…"


# ---------------------------------------------------------------------------
# Markup generation
# ---------------------------------------------------------------------------

def kind_sort_key(kind: str) -> tuple[int, str]:
    if kind in KIND_ORDER:
        return (KIND_ORDER.index(kind), kind)
    return (len(KIND_ORDER), kind)


def html_escape(s: str) -> str:
    """Escape `&`, `<`, `>` for safe inclusion in HTML text content.

    Notes:
      * The guide's `plugin-desc` text already contains `&amp;` entities.
        Escaping `&` again would double-encode (`&amp;amp;`). To avoid that,
        only escape `&` if it's not already starting a known entity.
    """
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "&":
            # already an entity? leave as-is.
            m = re.match(r"&(?:#\d+|#x[0-9a-fA-F]+|[A-Za-z]+);", s[i:])
            if m:
                out.append(m.group(0))
                i += len(m.group(0))
                continue
            out.append("&amp;")
        elif ch == "<":
            out.append("&lt;")
        elif ch == ">":
            out.append("&gt;")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def render_stats(index: list[dict], plugins: list[dict]) -> str:
    """Render the global `.stack-stats` row."""
    parts = [
        '          <ul class="stack-stats" role="list" aria-label="Marketplace at a glance">',
        f'            <li class="stack-stat"><strong>{len(plugins)}</strong><span>plugins</span></li>',
    ]
    for kind in STAT_KINDS:
        n = sum(1 for it in index if it["kind"] == kind)
        label = KIND_LABEL_PLURAL.get(kind, kind + "s").lower()
        parts.append(f'            <li class="stack-stat"><strong>{n}</strong><span>{label}</span></li>')
    parts.append("          </ul>")
    return "\n".join(parts)


def render_tabs(plugins: list[dict]) -> str:
    """Render the `.stack-tabs` bar."""
    parts = ['          <div class="stack-tabs" role="tablist" aria-label="Plugins">']
    for i, p in enumerate(plugins):
        is_active = i == 0
        active_class = " is-active" if is_active else ""
        aria_selected = "true" if is_active else "false"
        parts.append(
            f'            <button class="stack-tab{active_class}" role="tab" '
            f'aria-selected="{aria_selected}" aria-controls="stack-panel-{p["slug"]}" '
            f'id="stack-tab-{p["slug"]}" data-stack-tab="{p["slug"]}">'
        )
        parts.append(f'              <span class="stack-tab__name">{html_escape(p["name"])}</span>')
        parts.append(f'              <span class="stack-tab__ver">{html_escape(p["version"])}</span>')
        parts.append("            </button>")
    parts.append("          </div>")
    return "\n".join(parts)


def render_panels(plugins: list[dict], index: list[dict]) -> str:
    """Render the `.stack-panels` block — one panel per plugin."""
    # Group items by plugin slug, then by kind
    by_plugin: dict[str, list[dict]] = {}
    for it in index:
        by_plugin.setdefault(it["plugin"], []).append(it)

    parts = ['          <div class="stack-panels">']
    for i, p in enumerate(plugins):
        items = by_plugin.get(p["slug"], [])
        kind_counts: dict[str, int] = {}
        for it in items:
            kind_counts[it["kind"]] = kind_counts.get(it["kind"], 0) + 1

        is_active = i == 0
        active_class = " is-active" if is_active else ""
        hidden_attr = "" if is_active else " hidden"

        parts.append(
            f'            <div class="stack-panel{active_class}" role="tabpanel" '
            f'id="stack-panel-{p["slug"]}" aria-labelledby="stack-tab-{p["slug"]}" '
            f'data-stack-panel="{p["slug"]}"{hidden_attr}>'
        )
        parts.append(
            f'              <p class="stack-panel__desc">{html_escape(short_desc(p["desc"]))}</p>'
        )

        # Filter chips
        parts.append('              <ul class="stack-counts" role="list" aria-label="Filter by kind">')
        for kind in sorted(kind_counts, key=kind_sort_key):
            n = kind_counts[kind]
            label = KIND_LABEL_SINGULAR[kind] if n == 1 else KIND_LABEL_PLURAL[kind]
            parts.append(
                f'                <li><button type="button" class="stack-chip" '
                f'data-kind="{kind}" aria-pressed="false">'
                f'<strong>{n}</strong> {label}</button></li>'
            )
        parts.append("              </ul>")

        # Items list — grouped by kind in KIND_ORDER, sorted by name within
        sorted_items = sorted(
            items,
            key=lambda it: (kind_sort_key(it["kind"]), it["name"]),
        )
        parts.append('              <ul class="stack-items" role="list">')
        for it in sorted_items:
            desc = first_sentence(it["description"])
            parts.append(
                f'                <li data-kind="{it["kind"]}">'
                f'<code>{html_escape(it["name"])}</code>'
                f'<span>{html_escape(desc)}</span></li>'
            )
        parts.append("              </ul>")
        parts.append(
            '              <p class="stack-empty" hidden role="status">'
            "No items match that filter in this plugin.</p>"
        )
        parts.append("            </div>")

    parts.append("          </div>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Marker-based injection into index.html
# ---------------------------------------------------------------------------

MARKERS = {
    "STACK_STATS": render_stats,
    "STACK_TABS": render_tabs,
    "STACK_PANELS": render_panels,
}


def inject(index_html: str, plugins: list[dict], index: list[dict]) -> str:
    """Replace content between each marker pair with freshly generated markup."""
    out = index_html
    for marker, renderer in MARKERS.items():
        if renderer.__name__ == "render_stats":
            body = renderer(index, plugins)
        elif renderer.__name__ == "render_tabs":
            body = renderer(plugins)
        else:  # render_panels
            body = renderer(plugins, index)

        pattern = re.compile(
            rf"(<!-- {marker}:START -->)(.*?)(<!-- {marker}:END -->)",
            re.DOTALL,
        )
        if not pattern.search(out):
            raise SystemExit(
                f"Marker pair <!-- {marker}:START --> / <!-- {marker}:END --> "
                "not found in site/index.html — add them before running."
            )
        out = pattern.sub(rf"\g<1>\n{body}\n          \g<3>", out)
    return out


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    guide_html = GUIDE.read_text(encoding="utf-8")
    index_html = INDEX_HTML.read_text(encoding="utf-8")

    plugins = extract_plugins(guide_html)
    index = extract_index(guide_html)

    new_html = inject(index_html, plugins, index)

    if new_html == index_html:
        print("Stack section already up to date.")
        return 0

    INDEX_HTML.write_text(new_html, encoding="utf-8")
    print(
        f"Regenerated stack section: {len(plugins)} plugins, "
        f"{len(index)} items, {sum(1 for it in index if it['kind'] in STAT_KINDS)} "
        f"in headline stats."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
