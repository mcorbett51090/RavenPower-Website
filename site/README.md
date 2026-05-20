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

## Activate the contact form (optional)

By default the contact form falls back to a `mailto:` link to
`matt@ravenpower.net` — it works out of the box on any static host.

To capture submissions to a Formspree-style inbox instead, edit
`index.html` and set the form's `data-endpoint` attribute:

```html
<form id="contact-form" data-endpoint="https://formspree.io/f/XXXXXXXX">
```

The JavaScript will POST JSON to that endpoint, and fall back to the
`mailto:` flow only if the request fails.

## Edit the placeholder project cards

Each card in the **Work** section is a self-contained `<article class="proj">`
in `index.html`, clearly commented. Replace the title, copy, and
`data-tag` value to swap in real engagements.

## About bio

The bio in the **About** section is a *draft* — see the HTML comment
above that section. Replace the three paragraphs with Matt's final
LinkedIn "About" text when ready.
