import unittest
import os
import json
from gh_feed import app


class TestCache(unittest.TestCase):
    def setUp(self):
        self.username = "testuser"
        self.cache_path = app.get_cache_path(self.username)
        # Clean up before test
        if os.path.exists(self.cache_path):
            os.remove(self.cache_path)

    def tearDown(self):
        if os.path.exists(self.cache_path):
            os.remove(self.cache_path)

    def test_save_and_load_cache(self):
        events = [{"type": "PushEvent", "repo": {"name": "test/repo"},
                   "created_at": "2024-06-27T12:00:00Z", "payload": {"commits": [1]}}]
        app.save_cache(self.username, events)
        loaded = app.load_cache(self.username)
        self.assertEqual(loaded, events)


class TestTimeAgo(unittest.TestCase):
    def test_time_ago_seconds(self):
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        iso_time = (now - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.assertIn("s ago", app.time_ago(iso_time))

    def test_time_ago_minutes(self):
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        iso_time = (now - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.assertIn("m ago", app.time_ago(iso_time))

    def test_time_ago_hours(self):
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        iso_time = (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.assertIn("h ago", app.time_ago(iso_time))

    def test_time_ago_days(self):
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        iso_time = (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.assertIn("d ago", app.time_ago(iso_time))


class TestIntegration(unittest.TestCase):
    def test_fetch_user_activity_online(self):
        # This test will hit the real GitHub API, so it may fail if rate-limited or offline
        events = app.fetch_user_activity("octocat", use_cache=False)
        self.assertIsInstance(events, list)
        if not events:
            reason = "No events returned from GitHub API (rate-limited, offline, or no activity). Skipping."
            print(f"SKIP REASON: {reason}")
            self.skipTest(reason)
        self.assertGreater(len(events), 0)


if __name__ == "__main__":
    unittest.main()
