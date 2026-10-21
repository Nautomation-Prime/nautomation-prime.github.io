# Nautomation Prime

**"Bridging the gap between Cisco infrastructure and Python-driven automation with line-by-line transparency."**

---

## About This Site

This is the home of **Nautomation Prime**—a collection of production-ready network automation tools, technical guides, and consulting services for Cisco infrastructure.

### What You'll Find Here

- **📖 Technical Deep Dives** — In-depth explanations of Python automation concepts with real Cisco examples
- **📚 Script Library** — Open-source, hardened automation tools ready to deploy
- **🛠️ Services** — Custom automation, portable bundles, and Docker containers
- **🚀 Getting Started** — Guides to help you find what you need

---

## Quick Links

- **[📖 View the Site](https://www.nautomationprime.io/)** — Main documentation
- **[🚀 Getting Started](https://www.nautomationprime.io/getting-started/)** — First-time visitor guide
- **[💬 Contact on LinkedIn](https://www.linkedin.com/company/nautomationprime)** — Reach out for questions or services

---

## 🏗️ Building & Contributing

### Local Development

**Requirements:**
- Python 3.8+
- [MkDocs](https://www.mkdocs.org/) 1.5+
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) 9.5+
- Git revision date plugin (for auto "last updated" dates)

**Setup:**
```bash
# Clone this repository
git clone https://github.com/Nautomation-Prime/Nautomation-Prime.github.io
cd Nautomation-Prime.github.io

# Install dependencies
pip install -r requirements.txt

# Start local server (opens at http://localhost:8000)
mkdocs serve

# Build static site for deployment
mkdocs build
```

### Contributing

Found an issue or want to improve the documentation?

1. Fork the repository
2. Create a feature branch (`git checkout -b improve/documentation`)
3. Make your changes
4. Test locally with `mkdocs serve`
5. Submit a pull request

All contributions help make network automation more transparent and accessible!

---

## Editorial Rules: Site and Book

The site and the forthcoming book cover the same topics in different registers. The site is reference and instruction ("how do I build this?"); the book is narrative and judgement ("why did this break, and how would I have known?"). Two rules keep them from colliding:

1. **The forward rule.** Incidents, near misses, "what this cost me to learn" material, and anything touching the IOS-XE upgrade orchestrator's build story go to the book draft, not the site.
2. **No new cumulative series.** Standalone reference pages, as many as you like. No second cumulative, build-along multi-part series (like the Capstone) until the book ships.

Nothing gets deleted to protect the book: the site's free content stays.

### Site structure

- **Academy**: the free learning content, in three tracks (Learn, Govern, See it done). Track landing pages live in `docs/academy/`; the articles themselves still live under `docs/foundation/` so existing URLs keep working.
- **Foundation**: the charity arm only (`docs/foundation/index.md`, `docs/foundation/charity-services.md`, `docs/legal/foundation-status.md`).
- **Email capture**: `overrides/partials/email-capture.html`, shown on every Academy page. Configure it under `extra.mailing_list` in `mkdocs.yml`.

---

## Our Philosophy

Every tool, script, and guide follows three core principles:

1. **Line-by-Line Transparency** — We explain the *why*, not just the *what*
2. **Hardened for Production** — Enterprise-grade error handling and security
3. **Vendor-Neutral** — Built on industry-standard libraries (Netmiko, Nornir, PyATS)

---

## License

See [LICENSE](LICENSE) for details.

---

> **Mission:** To empower engineers through Python-driven transparency and provide enterprises with hardened automation that eliminates error and accelerates growth.
