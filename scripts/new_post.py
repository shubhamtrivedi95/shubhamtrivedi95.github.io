import argparse
from datetime import date
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def create_post(title, category, slug):
    if category not in {"project", "tutorial", "community", "training"}:
        raise ValueError("Unknown post category")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("Use a lowercase, hyphenated slug")
    path = ROOT / "content" / "posts" / (slug + ".md")
    metadata = dict(title=title, summary="Describe the work and the available evidence.", category=category, status="Draft", date=date.today().isoformat(), draft=True)
    with path.open("x", encoding="utf-8", newline="\n") as output:
        output.write("---\n" + json.dumps(metadata, indent=2) + "\n---\n\n## Problem\n\n## My contribution\n\n## Implementation\n\n## Evidence\n\n## Results and limitations\n")
    print(f"Created draft: {path}")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a draft portfolio post without overwriting existing work")
    parser.add_argument("slug")
    parser.add_argument("--title", required=True)
    parser.add_argument("--category", choices=["project", "tutorial", "community", "training"], default="project")
    args = parser.parse_args()
    create_post(args.title, args.category, args.slug)
