"""Static release checks for the public landing page (no browser dependency)."""
from html.parser import HTMLParser
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit
import subprocess
import unittest

SITE = Path(__file__).resolve().parents[1] / "sites" / "dennisb-landing"


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.elements = []
        self.text = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


class LandingRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (SITE / "index.html").read_text()
        cls.page = Page(cls.source)

    def test_copy_and_public_links(self):
        text = " ".join(self.page.text)
        self.assertNotIn("Rehovot", self.source)
        self.assertNotIn("Say hello", text)
        self.assertIn("Say Hello", text)
        self.assertIn("Israel", text)
        self.assertNotIn("uptime", self.source.lower())
        hosts = {"dennisb.xyz", "github.com", "www.linkedin.com", "lostboxart.github.io", "steamcommunity.com"}
        for _, attrs in self.page.elements:
            value = attrs.get("href", "")
            url = urlsplit(value)
            if url.netloc:
                self.assertEqual(url.scheme, "https", value)
                self.assertIn(url.netloc, hosts, value)
            self.assertNotIn("javascript:", value.lower())

    def test_ids_anchors_and_accessibility_references(self):
        ids = [a["id"] for _, a in self.page.elements if "id" in a]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(sum(tag == "h1" for tag, _ in self.page.elements), 1)
        for _, attrs in self.page.elements:
            if attrs.get("href", "").startswith("#"):
                self.assertIn(attrs["href"][1:], ids)
            for label in attrs.get("aria-labelledby", "").split():
                self.assertIn(label, ids)
        stories = [a for _, a in self.page.elements if a.get("class") == "story"]
        self.assertEqual({a["id"] for a in stories}, {"work", "home", "agents"})
        self.assertTrue(all("hidden" not in a for a in stories), "No-JS visitors need every chapter")

    def test_local_assets_and_no_editor_runtime(self):
        self.assertNotIn("window.openai", self.source)
        self.assertNotIn("data:image", self.source)
        self.assertNotIn("data:video", self.source)
        scripts = [a for tag, a in self.page.elements if tag == "script"]
        self.assertTrue(scripts)
        for attrs in scripts:
            self.assertIn("src", attrs, "Production scripts must be external")
        for tag, attrs in self.page.elements:
            values = [attrs.get("src", ""), attrs.get("data-src", "")]
            if tag == "link":
                values.append(attrs.get("href", ""))
            if tag == "meta" and attrs.get("property") == "og:image":
                values.append(urlsplit(attrs["content"]).path.lstrip("/"))
            for value in filter(None, values):
                if urlsplit(value).scheme:
                    continue
                target = SITE / urlsplit(value).path
                self.assertTrue(target.is_file(), str(target))
                self.assertLess(target.stat().st_size, 4_000_000)
                if target.parent.name == "assets":
                    self.assertEqual(target.name.rsplit(".", 2)[-2], sha256(target.read_bytes()).hexdigest()[:10])
        self.assertLess(len(self.source.encode()), 20_000)

    def test_script_syntax_and_motion_styles(self):
        scripts = [a["src"] for tag, a in self.page.elements if tag == "script"]
        for script in scripts:
            result = subprocess.run(["node", "--check", str(SITE / script)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotRegex((SITE / script).read_text(), r"\b(?:fetch|XMLHttpRequest|WebSocket|eval)\s*\(")
        styles = [a["href"] for tag, a in self.page.elements if tag == "link" and a.get("rel") == "stylesheet"]
        css = "\n".join((SITE / style).read_text() for style in styles)
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertIn(":focus-visible", css)
        self.assertIn("[hidden]", css)


if __name__ == "__main__":
    unittest.main()
