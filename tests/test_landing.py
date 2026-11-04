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
        self.images = []

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
        if tag == "img":
            self.images.append(attrs)


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

    def test_public_game_images_have_alternatives_and_source(self):
        self.assertGreaterEqual(len(self.parser.images), 3)
        for image in self.parser.images:
            self.assertTrue(image["src"].startswith("https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/212500/"))
            self.assertTrue(image.get("alt"))
            self.assertEqual(image.get("decoding"), "async")
        self.assertIn("https://store.steampowered.com/app/212500/", self.parser.links)

    def test_layout_has_mobile_styles_and_keyboard_focus(self):
        self.assertIn("@media (max-width:", self.html)
        self.assertIn(":focus-visible", self.html)

    def test_landing_omits_long_provenance_section(self):
        self.assertNotIn("Origem da tradução", self.html)
        self.assertNotIn("André Lobo", self.html)


if __name__ == "__main__":
    unittest.main()
