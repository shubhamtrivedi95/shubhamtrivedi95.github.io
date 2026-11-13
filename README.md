# Engineering portfolio

An evidence-led home for projects, open-source code, tutorials, workshops, and
training. The resume remains available, but the homepage leads with the work.

## Local workflow (Python 3.11+)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\build.py
.\.venv\Scripts\python.exe -m http.server 8765 --bind 127.0.0.1 --directory _site
```

Open http://127.0.0.1:8765/. Stop the server with Ctrl+C. Rebuild and refresh after
changes. No Node installation, runtime API, or AI subscription is needed to serve
the generated website. Never serve the repository root publicly.

## Write a post

```powershell
.\.venv\Scripts\python.exe scripts\new_post.py my-project --title "My project" --category project
```

Edit the new file in `content\posts`. Its metadata is JSON between `---` lines,
followed by standard Markdown (including fenced code and tables).

- Required: `title`, `summary`, `category`, `status`.
- Category: `project`, `tutorial`, `community`, or `training`.
- `draft: true` excludes the entire post from the published site and indexes.
  Remove it or set false only when ready.
- Optional `date`: an exact ISO date when supported by evidence; omit uncertain dates.
- Optional `featured: true`: gives priority in the homepage's four selected cards.
- Optional `image` and `image_alt`: a root-relative image path and meaningful text.
- Body images use `![Meaningful description](/assets/images/example.jpg)`.
- Place approved JPEG images in `assets\images`; the build strips EXIF and resizes
  referenced images for the site. Unreferenced images (including draft-only
  images) are excluded. Other image formats are not currently imported.
- Use problem, personal contribution, implementation, evidence, and limitations
  sections where applicable. Distinguish measured results from plans.

Indexes and navigation update automatically. Build-time CSS hashing prevents
stale styles without manually editing page links. Markdown is trusted author
input, not an anonymous upload interface: review HTML and links before merging.

## Copilot authoring agent

Use the **portfolio-author** agent in a Copilot client supporting repository
custom agents (`.github\agents\portfolio-author.agent.md`). Example request:

> Create a draft project post from these notes and photos. Link the public code,
> distinguish tested results from planned work, and run local validation.

The agent assists authoring; it does not run autonomously on visitors' machines
or require an API token in the website. Normal editing and the post command work
even in clients that do not support custom agents.

## Repository structure

| Path | Role |
| --- | --- |
| `content\posts\*.md` | Author-maintained posts |
| `content\sources.json` | Curated repository and tutorial directory |
| `templates\base.html` | Shared page shell, navigation, metadata |
| `templates\pages` | Existing About, Experience, Resume source pages; build extracts their main content |
| `assets\images` | Approved photographic/certificate evidence |
| `assets\Shubham_Trivedi_Resume.pdf` | Privacy-reviewed downloadable resume |
| `style.css`, `site.js` | Shared appearance and footer-year behavior |
| `scripts` | Post scaffolding, deterministic offline build, internal-link validation |
| `tests` | Draft exclusion, metadata, assets, links, CSS cache-version checks |
| `_site` | Generated deployable output, ignored by Git; do not hand-edit |
| `Posts` | Local input exports, ignored and never copied by the build |

The published artifact is allowlisted: generated HTML, CSS, JS, processed JPEGs,
the reviewed resume PDF, and `.nojekyll`. Source PDFs, raw exports, tests,
dependencies, and agent files are not deployed.

## Evidence and privacy

Seed content uses original summaries with links to the supplied LinkedIn posts,
Electro Passion, Instructables, Arduino Libraries, and public GitHub repositories.
Repository descriptions and status were reviewed in November 2026; the
directory excludes this portfolio repository. No build fetches external content
or claims current compatibility. Forks are labeled.
Old tutorials remain historical references, not freshly validated instructions.

The supplied Yocto post documents two batches and 35 colleagues. The SIH project
story uses the supplied first-hand account for the Food Corporation of India
requirement and RS232/ESP8266/Django data flow. Photographs document the prototype
demonstration and award, not measured production impact; certificates document
course completion. The SIH year follows the supplied original 2018 post,
despite a differing year in another public profile.

Only GitHub and LinkedIn are contact channels. Keep phone numbers, email
addresses, postal addresses, private code, credentials, and unapproved employer
material out of posts/images. Workshop and certificate images were supplied for
publication; review attendee privacy and visible screens before pushing.
Removing an image reference does not remove a tracked source image or Git
history. Remove unwanted files before the first public commit.

The build checks internal links, image alt text, page anchors, metadata fields,
and text contact patterns. It cannot establish consent, image privacy, truth of
claims, or remote link availability. Review those manually.

## Validation and publishing

Run the local tests and build, then inspect mobile/desktop layouts, light/dark
themes, keyboard access, images, evidence links, and resume download.

```powershell
git -c core.whitespace=cr-at-eol --no-pager diff --check
git --no-pager status --short
```

**One-time setup:** in repository **Settings > Pages**, choose **GitHub Actions**
as the deployment source, replacing branch/root publishing. The root no longer
contains generated HTML. This setting must be changed before deploying this
structure. No repository setting is changed automatically by local edits.

After review, commit and push source changes to `main`. The Pages workflow runs
tests/build and uploads **only `_site`**; deployment depends on build success.
Pull requests validate but do not deploy. Verify the Pages workflow and live
https://shubhamtrivedi95.github.io/ after publication. Do not commit `_site`,
`.venv`, or raw post exports. This task does not itself commit or push changes.

## Resume updates

Edit `templates\pages\resume.html`, rebuild, and print
http://127.0.0.1:8765/resume.html to PDF using A4 and no browser headers/footers.
Save as `assets\Shubham_Trivedi_Resume.pdf`, then rebuild again. Inspect all PDF
pages, selectable text, metadata, and link annotations for private information.
Never publish the original input resume.

## Visitor counts (disabled)

No analytics request, cookie, fake count, or browser-local counter is included.
GitHub Pages cannot persist visitor totals by itself.

If needed later, choose a privacy-reviewed analytics provider (or self-hosted
service), register the public domain, document data retention/consent, and add
its approved integration to the shared template. A public count needs a
provider-supported read-only public endpoint; never expose a secret API key.
Label page views versus unique visitors accurately and show an explicit
unavailable state on errors. Enable tracking only after a separate review.
