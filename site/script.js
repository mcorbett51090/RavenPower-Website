/* =========================================================
   Raven Power — script.js
   Vanilla JS. No build step. Defer-loaded.
   ========================================================= */
(function () {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Year stamp ---------- */
  const yr = document.getElementById('year');
  if (yr) yr.textContent = new Date().getFullYear();

  /* ---------- Nav: scroll state + mobile toggle ---------- */
  const nav = document.getElementById('nav');
  const onScroll = () => {
    if (!nav) return;
    nav.classList.toggle('is-scrolled', window.scrollY > 12);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  const toggle = document.querySelector('.nav__toggle');
  const mobile = document.getElementById('nav-mobile');
  if (toggle && mobile) {
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      mobile.hidden = open;
      mobile.classList.toggle('is-open', !open);
    });
    mobile.addEventListener('click', (e) => {
      if (e.target instanceof HTMLAnchorElement) {
        toggle.setAttribute('aria-expanded', 'false');
        mobile.hidden = true;
        mobile.classList.remove('is-open');
      }
    });
  }

  /* ---------- Reveal on scroll ---------- */
  const revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const delay = parseInt(el.getAttribute('data-reveal-delay') || '0', 10);
        if (delay > 0) {
          setTimeout(() => el.classList.add('is-in'), delay);
        } else {
          el.classList.add('is-in');
        }
        io.unobserve(el);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('is-in'));
  }

  /* ---------- Hero canvas: subtle constellation field ---------- */
  const canvas = document.getElementById('hero-canvas');
  const heroEl = document.querySelector('.hero');
  if (canvas && canvas.getContext && !reduceMotion) {
    const ctx = canvas.getContext('2d');
    let w = 0, h = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);
    let particles = [];
    let raf = 0;
    let visible = true;      // hero in viewport
    let pageVisible = true;  // tab focused
    const running = () => visible && pageVisible;

    const ACCENT = [201, 162, 73];
    const WHITE = [220, 222, 228];

    function resize() {
      const rect = canvas.getBoundingClientRect();
      w = rect.width;
      h = rect.height;
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      seed();
    }

    function seed() {
      // Density scaled to viewport area; capped for perf
      const area = w * h;
      const count = Math.max(40, Math.min(110, Math.floor(area / 16000)));
      particles = new Array(count).fill(0).map(() => {
        const accent = Math.random() < 0.22;
        return {
          x: Math.random() * w,
          y: Math.random() * h,
          vx: (Math.random() - 0.5) * 0.18,
          vy: (Math.random() - 0.5) * 0.18,
          r: Math.random() * 1.2 + 0.4,
          a: Math.random() * 0.55 + 0.25,
          accent
        };
      });
    }

    function step() {
      if (!running()) { raf = 0; return; }
      ctx.clearRect(0, 0, w, h);

      // Draw connections — short range only
      const MAX = 130;
      const MAX_SQ = MAX * MAX;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const a = particles[i], b = particles[j];
          const dx = a.x - b.x, dy = a.y - b.y;
          const d2 = dx * dx + dy * dy;
          if (d2 < MAX_SQ) {
            const t = 1 - d2 / MAX_SQ;
            const useAccent = a.accent || b.accent;
            const c = useAccent ? ACCENT : WHITE;
            ctx.strokeStyle = `rgba(${c[0]},${c[1]},${c[2]},${(t * 0.16).toFixed(3)})`;
            ctx.lineWidth = 0.6;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
      }

      // Move + draw
      for (const p of particles) {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < -10) p.x = w + 10;
        if (p.x > w + 10) p.x = -10;
        if (p.y < -10) p.y = h + 10;
        if (p.y > h + 10) p.y = -10;

        const c = p.accent ? ACCENT : WHITE;
        ctx.fillStyle = `rgba(${c[0]},${c[1]},${c[2]},${p.a.toFixed(3)})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }

      raf = requestAnimationFrame(step);
    }

    function startLoop() {
      if (raf === 0 && running()) {
        raf = requestAnimationFrame(step);
      }
    }

    resize();
    startLoop();

    window.addEventListener('resize', () => {
      cancelAnimationFrame(raf); raf = 0;
      resize();
      startLoop();
    }, { passive: true });

    // Pause animation when tab is hidden
    document.addEventListener('visibilitychange', () => {
      pageVisible = !document.hidden;
      if (pageVisible) startLoop();
      else { cancelAnimationFrame(raf); raf = 0; }
    });

    // Pause animation when hero scrolls off screen
    if ('IntersectionObserver' in window && heroEl) {
      const heroIO = new IntersectionObserver((entries) => {
        for (const entry of entries) {
          visible = entry.isIntersecting;
          if (visible) startLoop();
          else { cancelAnimationFrame(raf); raf = 0; }
        }
      }, { threshold: 0 });
      heroIO.observe(heroEl);
    }
  }

  /* ---------- Contact form ---------- */
  /*
    Submission strategy:
      1. If data-endpoint is set (e.g. a Formspree URL), POST JSON to it.
      2. Otherwise, fall back to a `mailto:` link so the form still works
         on a vanilla static host with no backend.
  */
  const form = document.getElementById('contact-form');
  const status = document.getElementById('form-status');

  function setStatus(msg, kind) {
    if (!status) return;
    status.textContent = msg || '';
    status.classList.remove('is-ok', 'is-err');
    if (kind === 'ok') status.classList.add('is-ok');
    if (kind === 'err') status.classList.add('is-err');
  }

  function buildMailto(data) {
    const subject = `New project inquiry — ${data.name || 'Raven Power'}`;
    const lines = [
      `Name: ${data.name || ''}`,
      `Email: ${data.email || ''}`,
      `Company: ${data.company || ''}`,
      '',
      data.message || ''
    ];
    return `mailto:matt@ravenpower.net?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join('\n'))}`;
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!form.reportValidity()) return;

      const fd = new FormData(form);
      const data = {
        name:    String(fd.get('name')    || '').trim(),
        email:   String(fd.get('email')   || '').trim(),
        company: String(fd.get('company') || '').trim(),
        message: String(fd.get('message') || '').trim()
      };

      const endpoint = form.getAttribute('data-endpoint');
      const submitBtn = form.querySelector('button[type="submit"]');

      if (endpoint) {
        try {
          submitBtn && (submitBtn.disabled = true);
          setStatus('Sending…', '');
          const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          });
          if (!res.ok) throw new Error('Bad response');
          form.reset();
          setStatus('Thanks — your message is on its way. We’ll reply soon.', 'ok');
        } catch (err) {
          setStatus('Couldn’t send via the form. Opening your email app instead…', 'err');
          window.location.href = buildMailto(data);
        } finally {
          submitBtn && (submitBtn.disabled = false);
        }
      } else {
        // No endpoint configured — use mailto fallback.
        setStatus('Opening your email app — your message will be sent from matt@ravenpower.net.', 'ok');
        window.location.href = buildMailto(data);
      }
    });
  }

  /* ---------- Smooth scroll for in-page anchors (offset for sticky nav) ---------- */
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const href = a.getAttribute('href');
      if (!href || href === '#' || href.length < 2) return;
      const target = document.getElementById(href.slice(1));
      if (!target) return;
      e.preventDefault();
      const top = target.getBoundingClientRect().top + window.scrollY - 56;
      window.scrollTo({ top, behavior: reduceMotion ? 'auto' : 'smooth' });
      // Move focus for a11y without re-scrolling
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    });
  });
})();
