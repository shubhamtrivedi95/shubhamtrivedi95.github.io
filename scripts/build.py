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


def cards(posts):
    items = []
    for post in posts:
        image = ""
        if post.get("image"):
            image = f'<img src="{escape(post["image"])}" alt="{escape(post["image_alt"])}" loading="lazy" width="960" height="640">'
        items.append(
            f'<article class="card evidence-card">{image}<div class="evidence-copy">'
            f'<p class="eyebrow">{escape(post["category"])} / {escape(post["status"])}</p>'
            f'<h3><a href="{post["url"]}">{escape(post["title"])}</a></h3>'
            f'<p>{escape(post["summary"])}</p>'
            f'<a class="text-link" href="{post["url"]}">See the evidence &rarr;</a></div></article>'
        )
    return '<div class="evidence-grid">' + "".join(items) + "</div>"


def heading(label, title, description):
    return f'<header class="page-header"><p class="eyebrow">{escape(label)}</p><h1>{escape(title)}</h1><p class="lead">{escape(description)}</p></header>'


def render(path, title, description, body, active, css_version, main_class="", article=False):
    navigation = []
    for href, label in (("/", "Home"), ("/projects.html", "Work"), ("/journal.html", "Journal"), ("/experience.html", "Experience"), ("/about.html", "About"), ("/resume.html", "Resume")):
        current = ' aria-current="page"' if href == active else ""
        navigation.append(f'<li><a href="{href}"{current}>{label}</a></li>')
    html = Template((ROOT / "templates" / "base.html").read_text(encoding="utf-8")).substitute(
        title=escape(title), description=escape(description), canonical=BASE_URL + ("/" if path == "index.html" else "/" + path),
        og_type="article" if article else "website", css_version=css_version,
        navigation="".join(navigation), body=body, main_class=main_class,
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
    for name in ("style.css", "site.js"):
        shutil.copyfile(ROOT / name, OUTPUT / name)
    public_assets = OUTPUT / "assets"
    public_assets.mkdir()
    shutil.copyfile(ROOT / "assets" / "Shubham_Trivedi_Resume.pdf", public_assets / "Shubham_Trivedi_Resume.pdf")
    css_version = sha256((ROOT / "style.css").read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]
    for post in posts:
        body = heading(post["category"] + " / " + post["status"], post["title"], post["summary"])
        if post.get("date"):
            body += f'<p class="muted">Event / publication date: <time datetime="{post["date"]}">{post["date"]}</time></p>'
        body += '<article class="article-body">' + markdown.markdown(post["body"], extensions=["fenced_code", "tables"]) + "</article>"
        body += '<p class="article-back"><a href="/journal.html">All stories</a> &middot; <a href="/projects.html">All work</a></p>'
        render("posts/" + post["slug"] + ".html", post["title"] + " | Shubham Trivedi", post["summary"], body, "/projects.html" if post["category"] == "project" else "/journal.html", css_version, article=True)
    featured = sorted(posts, key=lambda p: p.get("featured", False), reverse=True)[:4]
    home = '''<section class="hero"><div><p class="eyebrow">Shubham Trivedi / Engineer &amp; maker</p>
    <h1>Built with curiosity.<br><span class="text-accent">Backed by evidence.</span></h1>
    <p class="hero-copy">Embedded Linux platforms, an Arduino library, hands-on electronics tutorials, and knowledge shared with other engineers. Explore the code, the process, and the work behind the resume.</p>
    <div class="actions"><a class="button button-primary" href="/projects.html">Explore my work &rarr;</a><a class="button" href="/journal.html">Read the journal</a></div></div>
    <figure class="hero-evidence"><img src="/assets/images/bootcamp-day4.jpg" alt="Shubham presenting a Yocto bootcamp session" width="1024" height="768"><figcaption>Teaching Yocto at Atlas Copco &middot; 2026<br><a href="/posts/yocto-bootcamps.html">Two batches. 35 colleagues. Hands-on learning.</a></figcaption></figure></section>'''
    home += '<section class="section"><div class="section-heading"><div><p class="eyebrow">Code / teaching / community</p><h2>Selected evidence</h2></div><a href="/projects.html">Browse all work &rarr;</a></div>' + cards(featured) + "</section>"
    home += '<section class="contact-band"><div><h2>A single home for a decade of making.</h2><p>From early microcontroller experiments to Linux board support and sharing knowledge. Source links distinguish documented work from ongoing exploration.</p></div><a class="button" href="/about.html">About my approach &rarr;</a></section>'
    render("index.html", "Shubham Trivedi | Engineering in practice", "Projects, code, tutorials, workshops, and evidence from Shubham Trivedi's embedded engineering work.", home, "/", css_version)
    catalog = json.loads((ROOT / "content" / "sources.json").read_text(encoding="utf-8"))
    work = heading("Selected work", "From source code to working systems.", "Libraries, Linux platforms, and electronics experiments. Follow the source and distinguish archived examples from active development.")
    work += '<section class="section">' + cards([p for p in posts if p["category"] == "project"]) + "</section>"
    work += '<section class="section"><h2>Public repository directory</h2><p class="muted">Curated snapshot, reviewed November 2026. A repository link is evidence of code, not a claim of production readiness. Forks are labeled.</p><div class="repository-grid">'
    for repo in catalog["repositories"]:
        work += f'<article class="card"><p class="eyebrow">{escape(repo["kind"])}</p><h3><a href="https://github.com/shubhamtrivedi95/{escape(repo["name"])}">{escape(repo["name"])}</a></h3><p>{escape(repo["summary"])}</p></article>'
    work += '</div><p><a href="https://github.com/shubhamtrivedi95?tab=repositories">View the live GitHub directory</a></p></section>'
    render("projects.html", "Work | Shubham Trivedi", "Code-backed projects, UltraDistSensor, Yocto board support, and a public repository directory.", work, "/projects.html", css_version)
    journal = heading("Journal & field notes", "Build it. Explain it. Share it.", "Workshop stories, community contributions, training evidence, and a trail of electronics tutorials.")
    journal += '<section class="section">' + cards([p for p in posts if p["category"] != "project"]) + "</section>"
    journal += '<section class="section" id="tutorials"><h2>Tutorial archive</h2><p class="muted">Original summaries with links to the full articles. Older tutorials may require adaptation for current hardware and software.</p><div class="repository-grid">'
    for entry in catalog["tutorials"]:
        journal += f'<article class="card"><p class="eyebrow">{escape(entry["platform"])}</p><h3><a href="{escape(entry["url"])}">{escape(entry["title"])}</a></h3><p>{escape(entry["summary"])}</p></article>'
    journal += '</div></section>'
    render("journal.html", "Journal & tutorials | Shubham Trivedi", "Documented workshops, certificates, hackathon contributions, and electronics tutorial archives.", journal, "/journal.html", css_version)
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
