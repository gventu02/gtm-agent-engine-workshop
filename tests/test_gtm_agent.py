import unittest
import os

os.environ.setdefault("OPENAI_API_KEY", "test")
from gtm_agent.gtm_agent import send_prospect_email


class SendProspectEmailTests(unittest.TestCase):
    def test_blocks_disqualified_prospect(self):
        result = send_prospect_email.func(
            {"prospect_id": "LEAD-50001", "email": "priya.nair@brightwaveapps.com"},
            "Follow up",
            "Hello",
            runtime=type("Runtime", (), {"config": {}})(),
        )

        self.assertEqual(result["status"], "blocked")

    def test_sends_eligible_prospect(self):
        result = send_prospect_email.func(
            {"prospect_id": "LEAD-71001", "email": "noah.williams@arcadiadata.com"},
            "Follow up",
            "Hello",
            runtime=type("Runtime", (), {"config": {}})(),
        )

        self.assertEqual(result["status"], "sent")


if __name__ == "__main__":
    unittest.main()
