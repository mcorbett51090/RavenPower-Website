# Raven Power LLC — website

Hand-coded static marketing site. No build step, no framework.

## Run locally

Just open `index.html` in a browser — everything works as static files.

For a clean local server (recommended, so font preconnects and relative paths behave like prod):

```
# from this site/ directory
python -m http.server 8080
# then visit http://localhost:8080
```

## Deploy

Deploy this `site/` directory as the publish root on any static host:

- **Cloudflare Pages** — point the build output at `site/`, build command blank.
- **GitHub Pages** — set Pages source to this directory.
- **Netlify / Vercel** — drop-in static deploy.

## Activate the contact form (≈ 2 minutes, ready to paste)

The contact form ships in a "ready-to-activate" state:

- **Default (no setup):** submissions open the visitor's email client with
  the message pre-filled to `matt@ravenpower.net`. Works on any static
  host with zero config.
- **One paste away from live:** drop a Formspree (or Basin / Web3Forms /
  Netlify Forms) endpoint URL into the form's `data-endpoint` attribute
  and submissions will POST directly to your inbox / dashboard. The
  `mailto:` flow still kicks in if the request fails.

### Step-by-step — Formspree

1. Sign up at [formspree.io](https://formspree.io/) (free tier is fine to start).
2. Create a new form. Copy the endpoint URL — it looks like:
   ```
   https://formspree.io/f/XXXXXXXX
   ```
3. Open `index.html`, find the contact form (search for `id="contact-form"`),
   and paste your URL into `data-endpoint`:
   ```html
   <form id="contact-form" data-endpoint="https://formspree.io/f/XXXXXXXX">
   ```
4. Save and redeploy. That's it — submissions now go to your Formspree inbox.

Any provider that accepts a JSON POST works the same way (Basin, Web3Forms,
Netlify Forms, your own endpoint). The visitor-facing email
`matt@ravenpower.net` is also shown in plain text next to the form, so a
visitor can always reach out directly even if JavaScript is disabled.

## Fill in the placeholders

The v2 site has a handful of clearly-commented placeholders the owner
should fill in before going live:

- **HQ location & LLC jurisdiction** — the site currently presents as
  "Remote, worldwide" everywhere a location appears (hero eyebrow,
  About → Location fact, footer, JSON-LD). LinkedIn lists the Raven Power
  role as Jacksonville, FL (Remote) but Matt's profile location is
  Hamilton, Bermuda. Once the registered LLC jurisdiction is confirmed,
  search for `LOCATION CAVEAT` in `index.html` and update each of those
  five spots, then update `addressLocality` / `addressCountry` in the
  JSON-LD block at the top.
- **By-the-numbers strip** — the four figures (13+, 2, 4, 1) are
  verified against Matt's record; adjust the year counts as time passes.
  Search for `STATS STRIP` in `index.html`.
- **Work-card outcome metrics** (each `.proj` card) — replace the
  `14d → 3d` style placeholders inside `.proj__metric` with real before/
  after numbers, or delete the whole `<p class="proj__metric">` block if
  you don't have a number yet for that engagement.
- **Headshot** — drop a square (~600×600) photo at `assets/matt.jpg` and
  uncomment the `<img>` tag inside `.about__portrait` in `index.html`.
  The placeholder ring with initials stays in place until you do.
- **Testimonial** — the `<section class="testimonial" hidden>` block is
  hidden by default. Remove the `hidden` attribute and replace the quote
  + attribution when you have a real one.
- **LLC registration number** — search for `Reg. No.` in the footer of
  `index.html` and replace `[pending]` with the issued number once the
  LLC jurisdiction is confirmed.

## Edit the placeholder project cards

Each card in the **Work** section is a self-contained `<article class="proj">`
in `index.html`, clearly commented. Replace the title, copy,
`data-tag` value, and the `.proj__metric` figures to swap in real
engagements. The motif (SVG block at the top of the card) is keyed to
`data-tag` (`ai`, `pp`, `bi`, `fabric`, `web`); reuse the matching motif
when adding new cards, or extend the set in `index.html` and add a
matching CSS rule for `--tag-tint`.

## About bio

The bio in the **About** section is written from Matt's verified
LinkedIn record — see the HTML comment above that section. It can be
tightened or expanded freely, but the underlying facts (13+ years,
BMA tenure Jan 2024 – Nov 2025, MBA + BS Finance from University of
South Alabama, the four certifications) are accurate as of writing.
The LinkedIn link is already wired to
[linkedin.com/in/matthewlcorbett](https://www.linkedin.com/in/matthewlcorbett).
