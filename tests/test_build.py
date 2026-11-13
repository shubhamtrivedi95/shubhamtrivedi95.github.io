from hashlib import sha256
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.build import OUTPUT, ROOT, build, load_post, validate_site
from scripts.new_post import create_post


class PortfolioBuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()

    def test_build_uses_current_css_and_checks_links(self):
        version = sha256((ROOT / "style.css").read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]
        pages = list(OUTPUT.rglob("*.html"))
        self.assertGreater(len(pages), 6)
        for page in pages:
            with self.subTest(page=page.name):
                self.assertIn(f'/style.css?v={version}', page.read_text(encoding="utf-8"))
        self.assertEqual(validate_site(OUTPUT), len(pages))

    def test_only_public_assets_are_built(self):
        self.assertNotIn("Posts", {path.name for path in OUTPUT.iterdir()})
        self.assertFalse(list(OUTPUT.rglob("Post-*")))
        self.assertFalse((OUTPUT / "content").exists())
        self.assertEqual([p.name for p in OUTPUT.rglob("*.pdf")], ["Shubham_Trivedi_Resume.pdf"])
        self.assertTrue((OUTPUT / "assets" / "images" / "bootcamp-day4.jpg").is_file())
        from PIL import Image
        for path in (OUTPUT / "assets" / "images").glob("*.jpg"):
            with Image.open(path) as image:
                self.assertFalse(image.getexif(), path)

    def test_missing_image_or_anchor_fails_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for markup in ('<img src="/missing.jpg" alt="Evidence">', '<a href="#missing">Broken</a>'):
                with self.subTest(markup=markup):
                    (root / "index.html").write_text(markup, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        validate_site(root)

    def test_invalid_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "post.md"
            for text in ('No metadata', '---\n{"title":"Test"}\n---\nBody'):
                with self.subTest(text=text):
                    path.write_text(text, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_post(path)

    def test_scaffolder_creates_excluded_draft_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "content" / "posts").mkdir(parents=True)
            with patch("scripts.new_post.ROOT", root):
                path = create_post("New work", "project", "new-work")
                self.assertTrue(load_post(path)["draft"])
                with self.assertRaises(FileExistsError):
                    create_post("Replacement", "project", "new-work")
                with self.assertRaises(ValueError):
                    create_post("Invalid", "project", "../escape")
                self.assertEqual(load_post(path)["title"], "New work")

    def test_drafts_do_not_leak_into_output(self):
        draft = ROOT / "content" / "posts" / "test-unpublished-draft.md"
        image = ROOT / "assets" / "images" / "test-unpublished-draft.jpg"
        self.assertFalse(draft.exists())
        self.assertFalse(image.exists())
        try:
            from PIL import Image
            Image.new("RGB", (20, 20)).save(image)
            draft.write_text('---\n{"title":"Private draft","summary":"Not public","category":"project","status":"Draft","draft":true}\n---\n![Private evidence](/assets/images/test-unpublished-draft.jpg)', encoding="utf-8")
            build()
            self.assertFalse((OUTPUT / "posts" / "test-unpublished-draft.html").exists())
            self.assertFalse((OUTPUT / "assets" / "images" / image.name).exists())
            self.assertNotIn("Private draft", (OUTPUT / "index.html").read_text(encoding="utf-8"))
            self.assertNotIn("Private draft", (OUTPUT / "projects.html").read_text(encoding="utf-8"))
        finally:
            draft.unlink()
            image.unlink()


if __name__ == "__main__":
    unittest.main()
