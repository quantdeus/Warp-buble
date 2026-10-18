"""Offline QA for warp literature bibliographic scouting."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

script = Path(__file__).resolve().parents[1] / "scout.py"
spec = importlib.util.spec_from_file_location("warp_scout", script)
scout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scout)

class WarpLiteratureQA(unittest.TestCase):
    def test_google_books_metadata(self):
        data = {"items": [{"volumeInfo": {"title": "Spacetime and Geometry",
            "authors": ["Sean Carroll"],
            "industryIdentifiers": [{"type": "ISBN_13", "identifier": "1234567890123"}],
            "publishedDate": "2019", "infoLink": "https://books.google.com/example"}}]}
        b = scout.google_books(data)
        self.assertEqual(b[0]["isbn"], "1234567890123")
        self.assertEqual(b[0]["status"], "BIBLIOGRAPHIC_ONLY")

    def test_crossref_metadata_not_claim(self):
        data = {"message": {"items": [{"title": ["Warp drive spacetime"],
            "DOI": "10.1234/warp", "issued": {"date-parts": [[2024]]}}]}}
        p = scout.crossref(data)
        self.assertEqual(p[0]["url"], "https://doi.org/10.1234/warp")
        self.assertEqual(p[0]["status"], "METADATA_UNREVIEWED")

    def test_deduplication(self):
        x = {"title": "Warp drive spacetime", "doi": "10.1234/warp"}
        self.assertEqual(len(scout.dedup([x, x])), 1)

    def test_scholar_search_links_only(self):
        links = scout.scholar_links()
        self.assertEqual(len(links), len(scout.PAPER_QUERIES))
        self.assertTrue(all("scholar.google.com/scholar?" in x["url"] for x in links))
        self.assertTrue(all("NOT automatic" in x["mode"] for x in links))

    def test_fabrication_gate_never_passes(self):
        calls = []
        def fake(base, params):
            calls.append(base)
            if "books" in base:
                return {"items": [{"volumeInfo": {"title": "General Relativity"}}]}
            return {"message": {"items": [{"title": ["Warp geometry"], "DOI": "10.1/demo"}]}}
        with patch.dict("os.environ", {"SERPAPI_API_KEY": "", "GOOGLE_BOOKS_API_KEY": ""}):
            report = scout.collect(fake)
        self.assertEqual(len(report["warp_evidence_gates"]), 10)
        self.assertEqual(set(report["warp_evidence_gates"].values()), {"UNKNOWN"})
        self.assertFalse(report["physical_FTL_demonstrated"])
        self.assertFalse(any("scholar.google.com" in x for x in calls))
        self.assertIn("НЕ физическое доказательство FTL", scout.markdown(report))

    def test_error_handling_no_fake_publications(self):
        def broken(base, params):
            raise OSError("offline")
        with patch.dict("os.environ", {"SERPAPI_API_KEY": ""}):
            report = scout.collect(broken)
        self.assertEqual(report["books"], [])
        self.assertEqual(report["papers"], [])
        self.assertTrue(report["errors"])

if __name__ == "__main__":
    unittest.main()
