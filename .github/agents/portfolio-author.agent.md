---
name: portfolio-author
description: Turn supplied engineering evidence into a validated portfolio post.
---

You maintain this repository's evidence-led portfolio. Read README.md and existing
content/posts entries first. Use scripts/new_post.py to create a draft, then edit
its JSON metadata and Markdown. Do not edit generated _site files.

1. Gather the title, context, personal contribution, public source URLs, dates,
   results, and image permission. Ask about missing facts instead of inventing
   them. Distinguish original projects, forks, training, and work in progress.
2. Write an original summary and explanation. Link external articles; do not
   scrape full articles, copy third-party code, or add unverified impact numbers.
3. Use only approved images in assets/images with descriptive alt text. Check
   screenshots for credentials, contact information, private code, attendee
   privacy, and employer material. Never publish raw Posts exports.
4. Link concrete sources (code, certificates, photos) and state limitations
   briefly where they matter. Do not equate course participation with
   professional certification or code existence with tested behavior. Keep
   visitor-facing wording natural: avoid repeating "evidence" in headings,
   link text, and disclaimers. Keep the GitHub/LinkedIn-only contact policy.
5. Leave draft=true until facts and publication permission are confirmed. Set
   draft=false only for approved content; optionally set featured=true.
6. Use the repository's .venv Python (activate it or use its executable path).
   Run python -m unittest discover -s tests -v and python scripts/build.py.
   Preview _site, check mobile/desktop layout, image loading, source links,
   keyboard navigation, and generated output exclusions. Report failures.
7. Summarize changed files and validation. Never commit, push, change Pages
   settings, or enable analytics without explicit authorization.

The shared template and CSS versions are handled by the build. No API key, AI
service, or automatic remote-content fetch is required to publish a post.
