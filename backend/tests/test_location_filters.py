import unittest
from unittest.mock import patch

from backend.scrapers.company_locations import matches_company_location
from backend.scrapers.zillow import getZillowJobs


class LocationFilterTests(unittest.TestCase):
    def test_boston_metro_and_state_disambiguation(self):
        for location, expected in (
            ("Boston, MA, USA", True),
            ("Boston", True),
            ("US-MA-Natick", True),
            ("Cambridge, Massachusetts", True),
            ("Bangalore, India; Framingham, MA", True),
            ("Watertown, MA", True),
            ("Cambridge, United Kingdom", False),
            ("Cambridge", False),
            ("Burlington, VT", False),
            ("Watertown, NY", False),
            ("Boston, England", False),
            ("Boston, UK", False),
            ("New Boston, NH", False),
            ("Remote - United States", False),
            ("", False),
        ):
            with self.subTest(location=location):
                job = {"location": location}
                self.assertEqual(matches_company_location(job, "MathWorks"), expected)
                self.assertEqual(job, {"location": location})

    def test_seattle_metro_not_every_washington_city(self):
        for location, expected in (
            ("Seattle-WA-2nd Ave", True),
            ("Seattle", True),
            ("Bellevue, WA", True),
            ("Redmond, Washington", True),
            ("Kirkland, WA", True),
            ("Austin, TX; Seattle, WA", True),
            ("Spokane, WA", False),
            ("Remote-WA", False),
            ("Washington, DC", False),
            ("Redmond, OR", False),
            ("Redmond", False),
            ("", False),
        ):
            with self.subTest(location=location):
                self.assertEqual(matches_company_location({"location": location}, "Amazon"), expected)

    def test_remote_evidence_and_explicit_workplace_flags(self):
        for job, expected in (
            ({"location": "Remote - United States"}, True),
            ({"location": "Home based - EMEA"}, True),
            ({"location": "Work-from-home, Canada"}, True),
            ({"location": "Anywhere"}, True),
            ({"location": "United States", "is_remote": True}, True),
            ({"location": "Remote, United States", "is_remote": False}, False),
            ({"location": "Remote / Hybrid"}, False),
            ({"location": "Not remote"}, False),
            ({"location": "Seattle, WA", "title": "Software Engineer - Remote"}, True),
            ({"location": "Seattle, WA", "description": "We offer remote work benefits."}, False),
            ({"location": "Seattle, WA", "title": "Distributed Systems Engineer"}, False),
            ({"location": "Seattle, WA", "title": "Remote Sensing Engineer"}, False),
            ({"location": "United States"}, False),
            ({}, False),
        ):
            with self.subTest(job=job):
                self.assertEqual(matches_company_location(job, "Nvidia"), expected)

    def test_zillow_separate_collection_path_uses_seattle_filter(self):
        seattle = {"job_id": "seattle", "location": "Seattle, WA"}
        remote = {"job_id": "remote", "location": "Remote-USA"}
        with patch("backend.scrapers.zillow.getJobs", return_value=([seattle, remote], 2)), \
                patch("backend.scrapers.zillow.log"):
            self.assertEqual(getZillowJobs([]), ([seattle], 2))


if __name__ == "__main__":
    unittest.main()
