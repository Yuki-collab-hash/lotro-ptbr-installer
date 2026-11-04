"""Static checks for the public download page and its sitemap."""

import unittest
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://yuki-collab-hash.github.io/lotro-ptbr-installer/"
RELEASE = "https://github.com/Yuki-collab-hash/lotro-ptbr-installer/releases/download/v0.2.6-preview/"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.canonical = []
        self.description = []
        self.language = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.language.append(attrs.get("lang"))
        if tag == "a":
            self.links.append(attrs.get("href"))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical.append(attrs.get("href"))
        if tag == "meta" and attrs.get("name") == "description":
            self.description.append(attrs.get("content"))


class LandingPageTests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        self.parser = PageParser()
        self.parser.feed(self.html)

    def test_page_has_portuguese_metadata_and_canonical_url(self):
        self.assertEqual(self.parser.language, ["pt-BR"])
        self.assertEqual(self.parser.canonical, [SITE])
        self.assertEqual(len(self.parser.description), 1)
        self.assertIn("LOTRO", self.parser.description[0])

    def test_downloads_point_to_published_release(self):
        self.assertIn(RELEASE + "LOTRO-PTBR-Windows-0.2.6-preview.zip", self.parser.links)
        self.assertIn(RELEASE + "traducao-ptbr.zip", self.parser.links)
        self.assertIn("não cobre todo o jogo", self.html)

    def test_sitemap_matches_canonical_url(self):
        sitemap = ElementTree.parse(ROOT / "docs/sitemap.xml")
        locations = [element.text for element in sitemap.iter() if element.tag.endswith("}loc")]
        self.assertEqual(locations, self.parser.canonical)

    def test_readme_links_to_page(self):
        self.assertIn(SITE, (ROOT / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
