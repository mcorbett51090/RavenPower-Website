# website-design Plugin

This plugin extends `ravenclaude-core` with specialists focused on building high-quality websites.

## Core Principle: Decision Gate First

**Every website project must begin with an explicit decision gate.**

Before any design, architecture, or implementation work begins, the **Web Strategist** (or Team Lead) **must** determine which path the client wants:

### Path A: No/Low-Code Path (Recommended for most small businesses)
- Client wants to easily edit content themselves without touching code.
- Primary recommendation: **Webflow**
- Secondary options: Framer (for more visual/animated sites)

### Path B: Code Path (When client wants ownership + performance)
- Client is comfortable with (or has someone who can maintain) code.
- Primary recommendation: **Next.js + Tailwind CSS + Vercel**
- Strong alternative: Astro + Vercel (for maximum performance)

**This decision fundamentally changes** which agents are involved, what deliverables look like, what tech recommendations are made, and how the site will be maintained long-term.

The Web Strategist is responsible for facilitating this decision early and clearly documenting the chosen path.

## Agents

See individual agent files in `agents/`.

## How to Use

The Team Lead from `ravenclaude-core` should dispatch to these specialists when website work is detected.