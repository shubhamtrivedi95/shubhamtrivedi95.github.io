import argparse
from datetime import date
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from string import Template
from urllib.parse import unquote, urlsplit

import markdown
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"
BASE_URL = "https://shubhamtrivedi95.github.io"
CATEGORIES = {"project", "tutorial", "community", "training"}
CATEGORY_LABELS = {"project": "Project", "tutorial": "Tutorial", "community": "Community", "training": "Training"}
CARD_ACTIONS = {"project": "View project", "tutorial": "Read tutorial", "community": "Read the story", "training": "Read more"}
ARROW = '<span aria-hidden="true">&rarr;</span>'
GITHUB_ICON = '<svg aria-hidden="true" viewBox="0 0 16 16" width="18" height="18"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8"/></svg>'
LINKEDIN_ICON = '<svg aria-hidden="true" viewBox="0 0 16 16" width="18" height="18"><path fill="currentColor" d="M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854zm4.943 12.248V6.169H2.542v7.225zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248S2.4 3.226 2.4 3.934c0 .694.521 1.248 1.327 1.248zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016l.016-.025V6.169h-2.4c.03.678 0 7.225 0 7.225z"/></svg>'


def load_post(path):
    source = path.read_text(encoding="utf-8")
    if not source.startswith("---\n"):
        raise ValueError(f"{path}: expected JSON metadata between --- lines")
    metadata, body = source[4:].split("\n---\n", 1)
    post = json.loads(metadata)
    for field in ("title", "summary", "category", "status"):
        if not isinstance(post.get(field), str) or not post[field].strip():
            raise ValueError(f"{path}: missing {field}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", path.stem):
        raise ValueError(f"{path}: use a lowercase hyphenated slug")
    if post["category"] not in CATEGORIES:
        raise ValueError(f"{path}: unknown category")
    if not isinstance(post.get("draft", False), bool):
        raise ValueError(f"{path}: draft must be a boolean")
    if post.get("date"):
        date.fromisoformat(post["date"])
    post.update(slug=path.stem, body=body, url=f"/posts/{path.stem}.html")
    return post


def pills(post):
    return (f'<ul class="pill-list" aria-label="Category and status"><li class="pill pill-accent">{CATEGORY_LABELS[post["category"]]}</li>'
            f'<li class="pill">{escape(post["status"])}</li></ul>')


def cards(posts):
    items = []
    for post in posts:
        if post.get("image"):
            media = f'<img class="card-media" src="{escape(post["image"])}" alt="{escape(post["image_alt"])}" loading="lazy" width="960" height="640">'
        else:
            media = f'<div class="card-media card-cover card-cover-{post["category"]}" aria-hidden="true"><span>~/{escape(post["slug"])}</span></div>'
        items.append(
            f'<article class="card post-card">{media}<div class="post-card-body">{pills(post)}'
            f'<h3><a class="stretched-link" href="{post["url"]}">{escape(post["title"])}</a></h3>'
            f'<p>{escape(post["summary"])}</p>'
            f'<span class="card-action" aria-hidden="true">{CARD_ACTIONS[post["category"]]} &rarr;</span></div></article>'
        )
    return '<div class="card-grid">' + "".join(items) + "</div>"


def heading(label, title, description):
    return f'<header class="page-header"><p class="eyebrow">{escape(label)}</p><h1>{escape(title)}</h1><p class="lead">{escape(description)}</p></header>'


def readable_date(value):
    parsed = date.fromisoformat(value)
    return f"{parsed:%B} {parsed.day}, {parsed.year}"


def render(path, title, description, body, active, css_version, main_class="", article=False):
    navigation = []
    for href, label in (("/", "Home"), ("/projects.html", "Work"), ("/journal.html", "Journal"), ("/experience.html", "Experience"), ("/about.html", "About"), ("/resume.html", "Resume")):
        current = ' aria-current="page"' if href == active else ""
        navigation.append(f'<li><a href="{href}"{current}>{label}</a></li>')
    html = Template((ROOT / "templates" / "base.html").read_text(encoding="utf-8")).substitute(
        title=escape(title), description=escape(description), canonical=BASE_URL + ("/" if path == "index.html" else "/" + path),
        og_type="article" if article else "website", css_version=css_version,
        navigation="".join(navigation), body=body, main_class=main_class,
        github_icon=GITHUB_ICON, linkedin_icon=LINKEDIN_ICON,
    )
    target = OUTPUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.ids = set()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                raise ValueError(f"Duplicate ID: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "img" and not attrs.get("alt", "").strip():
            raise ValueError("Images require meaningful alt text")
        for field in ("href", "src"):
            if field in attrs:
                self.urls.append(attrs[field])


def validate_site(output):
    pages = {}
    for path in output.rglob("*.html"):
        parser = Links()
        text = path.read_text(encoding="utf-8")
        if re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}|mailto:|tel:", text, re.I):
            raise ValueError(f"Private contact information in {path}")
        parser.feed(text)
        pages[path.resolve()] = parser
    for path, parser in pages.items():
        for url in parser.urls:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc:
                if parts.scheme != "https":
                    raise ValueError(f"{path}: unsupported external URL {url}")
                continue
            relative = unquote(parts.path)
            target = (output / relative.lstrip("/") if relative.startswith("/") else path.parent / relative).resolve() if relative else path
            if not target.is_relative_to(output.resolve()):
                raise ValueError(f"{path}: link escapes site: {url}")
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                raise ValueError(f"{path}: missing local target {url}")
            if parts.fragment and (target not in pages or parts.fragment not in pages[target].ids):
                raise ValueError(f"{path}: missing anchor {url}")
    return len(pages)


def build():
    posts = [load_post(path) for path in sorted((ROOT / "content" / "posts").glob("*.md"))]
    posts = [post for post in posts if not post.get("draft", False)]
    posts.sort(key=lambda post: (post.get("date", ""), post["slug"]), reverse=True)
    # Recreate only our fixed generated directory, never a caller-provided path.
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    for name in ("style.css", "site.js", "favicon.svg"):
        shutil.copyfile(ROOT / name, OUTPUT / name)
    public_assets = OUTPUT / "assets"
    public_assets.mkdir()
    shutil.copyfile(ROOT / "assets" / "Shubham_Trivedi_Resume.pdf", public_assets / "Shubham_Trivedi_Resume.pdf")
    css_version = sha256((ROOT / "style.css").read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]
    for post in posts:
        is_project = post["category"] == "project"
        back_url, back_label = ("/projects.html", "All work") if is_project else ("/journal.html", "Journal")
        body = f'<header class="page-header post-header"><a class="back-link" href="{back_url}"><span aria-hidden="true">&larr;</span> {back_label}</a>{pills(post)}<h1>{escape(post["title"])}</h1><p class="lead">{escape(post["summary"])}</p>'
        if post.get("date"):
            body += f'<p class="post-meta"><time datetime="{post["date"]}">{readable_date(post["date"])}</time></p>'
        body += "</header>"
        body += '<article class="article-body">' + markdown.markdown(post["body"], extensions=["fenced_code", "tables"]) + "</article>"
        related = [other for other in posts if other is not post and (other["category"] == "project") == is_project][:2]
        if related:
            body += f'<section class="section related" aria-labelledby="related-title"><div class="section-heading"><h2 id="related-title">Keep reading</h2><a class="text-link" href="{back_url}">{back_label} {ARROW}</a></div>{cards(related)}</section>'
        render("posts/" + post["slug"] + ".html", post["title"] + " | Shubham Trivedi", post["summary"], body, "/projects.html" if is_project else "/journal.html", css_version, article=True)
    featured = sorted(posts, key=lambda p: p.get("featured", False), reverse=True)[:4]
    home = f'''<section class="hero"><div class="hero-text">
    <p class="hero-badge"><span class="hero-badge-dot" aria-hidden="true"></span>Senior Engineer, Embedded Systems &middot; Atlas Copco</p>
    <h1>Building Embedded Linux systems, <span class="text-gradient">from bootloader to application.</span></h1>
    <p class="hero-copy">I'm Shubham Trivedi, an embedded engineer with 7+ years of experience across Yocto, BSP and kernel work, C++ applications, secure software updates, and CI/CD on ARM platforms. I also share what I learn through workshops, open-source code, and tutorials.</p>
    <div class="actions"><a class="button button-primary" href="/projects.html">View my work {ARROW}</a><a class="button" href="/resume.html">Resume</a></div>
    <ul class="social-links" aria-label="Profiles"><li><a href="https://github.com/shubhamtrivedi95">{GITHUB_ICON}GitHub</a></li><li><a href="https://www.linkedin.com/in/shubhamtrivedi95">{LINKEDIN_ICON}LinkedIn</a></li></ul></div>
    <figure class="hero-media"><img src="/assets/images/bootcamp-day4.jpg" alt="Shubham presenting a Yocto bootcamp session" width="1024" height="768"><figcaption><span class="pill pill-accent">Knowledge sharing</span><a href="/posts/yocto-bootcamps.html">Teaching Yocto to 35 engineers at Atlas Copco</a></figcaption></figure></section>
    <section class="stats" aria-label="Highlights"><dl>
    <div><dt>Years in embedded engineering</dt><dd>7+</dd></div>
    <div><dt>Companies across embedded &amp; IoT</dt><dd>5</dd></div>
    <div><dt>Engineers trained in Yocto</dt><dd>35</dd></div>
    <div><dt>Smart India Hackathon 2018 team</dt><dd>Winner</dd></div></dl></section>'''
    home += '''<section class="section" aria-labelledby="capabilities-title"><div class="section-heading"><div><p class="eyebrow">What I do</p><h2 id="capabilities-title">Core expertise</h2></div><a class="text-link" href="/about.html">Skills &amp; toolkit <span aria-hidden="true">&rarr;</span></a></div>
    <div class="capability-grid">
    <article class="card capability"><p class="capability-index">01</p><h3>Embedded Linux &amp; Yocto</h3><p>Custom distributions, layers, and BitBake recipes with Yocto Scarthgap and kas for AM64xx and i.MX8 platforms.</p></article>
    <article class="card capability"><p class="capability-index">02</p><h3>BSP, boot &amp; kernel</h3><p>U-Boot, kernel configuration, device trees, board bring-up, and boot-time optimization.</p></article>
    <article class="card capability"><p class="capability-index">03</p><h3>Applications &amp; integration</h3><p>C/C++ and Qt5 applications, IPC, gRPC, BLE, and Linux system integration and debugging.</p></article>
    <article class="card capability"><p class="capability-index">04</p><h3>Updates, CI &amp; testing</h3><p>SWUpdate with read-only root filesystems, Azure DevOps and GitHub Actions pipelines, and automated testing.</p></article>
    </div></section>'''
    home += f'<section class="section" aria-labelledby="featured-title"><div class="section-heading"><div><p class="eyebrow">Selected work</p><h2 id="featured-title">Featured projects &amp; stories</h2></div><a class="text-link" href="/projects.html">All work {ARROW}</a></div>' + cards(featured) + "</section>"
    home += f'''<section class="section" aria-labelledby="career-title"><div class="section-heading"><div><p class="eyebrow">Career</p><h2 id="career-title">Where I've worked</h2></div><a class="text-link" href="/experience.html">Full experience {ARROW}</a></div>
    <ol class="career-list">
    <li><span class="career-period">2024 &ndash; Present</span><strong>Atlas Copco</strong><span>Senior Engineer, Embedded Systems</span></li>
    <li><span class="career-period">2023 &ndash; 2024</span><strong>LG Soft India</strong><span>Senior Research Engineer</span></li>
    <li><span class="career-period">2023</span><strong>Apexon</strong><span>Senior Engineer</span></li>
    <li><span class="career-period">2020 &ndash; 2023</span><strong>Inpixon</strong><span>Embedded System Engineer</span></li>
    <li><span class="career-period">2019</span><strong>Wideeye Technologies</strong><span>IoT Embedded Software Developer</span></li>
    </ol></section>
    <section class="cta-band"><div><p class="eyebrow">Let's connect</p><h2>Working on Embedded Linux, Yocto, or BSP challenges?</h2><p>I'm always glad to connect with engineers and teams. Reach out on LinkedIn or explore my code on GitHub.</p></div>
    <div class="actions"><a class="button button-primary" href="https://www.linkedin.com/in/shubhamtrivedi95">{LINKEDIN_ICON}Connect on LinkedIn</a><a class="button" href="https://github.com/shubhamtrivedi95">{GITHUB_ICON}Follow on GitHub</a></div></section>'''
    render("index.html", "Shubham Trivedi | Embedded Linux & Yocto Engineer", "Shubham Trivedi is a Senior Embedded Engineer specializing in Embedded Linux, Yocto, BSP, and C++. Explore projects, open-source code, workshops, and tutorials.", home, "/", css_version)
    catalog = json.loads((ROOT / "content" / "sources.json").read_text(encoding="utf-8"))
    work = heading("Work", "Projects & open source", "Embedded Linux platforms, reusable libraries, and hardware experiments, each with links to the source code.")
    work += '<section class="section section-flush">' + cards([p for p in posts if p["category"] == "project"]) + "</section>"
    work += f'<section class="section" id="repositories" aria-labelledby="repositories-title"><div class="section-heading"><div><p class="eyebrow">Open source</p><h2 id="repositories-title">Public repositories</h2><p class="section-intro">A curated selection from GitHub, reviewed November 2026. Forks are labeled.</p></div><a class="text-link" href="https://github.com/shubhamtrivedi95?tab=repositories">View on GitHub {ARROW}</a></div><div class="repo-grid">'
    for repo in catalog["repositories"]:
        tone = "pill" if repo["kind"].startswith("Fork") else "pill pill-accent"
        work += f'<article class="card repo-card"><div class="repo-top">{GITHUB_ICON}<span class="{tone}">{escape(repo["kind"])}</span></div><h3><a class="stretched-link" href="https://github.com/shubhamtrivedi95/{escape(repo["name"])}">{escape(repo["name"])}</a></h3><p>{escape(repo["summary"])}</p></article>'
    work += "</div></section>"
    render("projects.html", "Work | Shubham Trivedi", "Projects and open-source work by Shubham Trivedi, including yocto-board-lab, UltraDistSensor, and early electronics examples.", work, "/projects.html", css_version)
    journal = heading("Journal", "Workshops, community & learning", "Stories from teaching Yocto, competing in and evaluating hackathons, and hands-on training, plus an archive of electronics tutorials.")
    journal += '<section class="section section-flush">' + cards([p for p in posts if p["category"] != "project"]) + "</section>"
    journal += '<section class="section" id="tutorials" aria-labelledby="tutorials-title"><div class="section-heading"><div><p class="eyebrow">Archive</p><h2 id="tutorials-title">Electronics tutorials</h2><p class="section-intro">Guides I published on Instructables and my Electro Passion blog. Older tutorials may need adapting for current hardware and software.</p></div></div><div class="repo-grid">'
    for entry in catalog["tutorials"]:
        journal += f'<article class="card repo-card"><div class="repo-top"><span class="pill">{escape(entry["platform"])}</span><span class="external-mark" aria-hidden="true">&nearr;</span></div><h3><a class="stretched-link" href="{escape(entry["url"])}">{escape(entry["title"])}</a></h3><p>{escape(entry["summary"])}</p></article>'
    journal += "</div></section>"
    render("journal.html", "Journal & tutorials | Shubham Trivedi", "Yocto workshops, hackathon stories, hands-on training, and electronics tutorials by Shubham Trivedi.", journal, "/journal.html", css_version)
    for name in ("experience", "about", "resume"):
        text = (ROOT / "templates" / "pages" / (name + ".html")).read_text(encoding="utf-8")
        body = re.search(r"<main\b[^>]*>(.*?)</main>", text, re.S).group(1)
        body = re.sub(r'(href|src)="(?!https://|#|/)([^"]+)"', r'\1="/\2"', body)
        title = re.search(r"<title>(.*?)</title>", text).group(1).replace("&amp;", "&")
        description = re.search(r'<meta name="description" content="([^"]+)"', text).group(1)
        render(name + ".html", title, description, body, "/" + name + ".html", css_version, "resume-page" if name == "resume" else "")
    referenced_images = set()
    for page in OUTPUT.rglob("*.html"):
        parser = Links()
        parser.feed(page.read_text(encoding="utf-8"))
        referenced_images.update(url for url in parser.urls if url.startswith("/assets/images/"))
    for url in referenced_images:
        relative = Path(url.lstrip("/"))
        image_path = (ROOT / relative).resolve()
        if image_path.parent != (ROOT / "assets" / "images").resolve() or image_path.suffix != ".jpg":
            raise ValueError(f"Only direct JPEG files in assets/images can be published: {url}")
        target = OUTPUT / relative
        target.parent.mkdir(exist_ok=True)
        with Image.open(image_path) as image:
            clean = ImageOps.exif_transpose(image).convert("RGB")
            clean.thumbnail((1600, 1600))
            clean.save(target, "JPEG", quality=85, optimize=True, exif=b"")
    (OUTPUT / ".nojekyll").touch()
    count = validate_site(OUTPUT)
    print(f"Built and validated {count} pages, {len(posts)} published posts. Output: {OUTPUT}")


if __name__ == "__main__":
    argparse.ArgumentParser(description="Build and validate the portfolio into _site").parse_args()
    build()
