import os
import unittest

os.environ["LANGSMITH_TRACING"] = "false"
os.environ["OPENAI_API_KEY"] = "test-key"

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile, get_prospect, score_prospect


SENSITIVE_KEYS = ("billing_qualification", "tax_id", "date_of_birth", "card_on_file", "credit_check_ref")
PROSPECT_ID = "LEAD-18993"


def assert_no_sensitive_keys(test_case, value):
    text = str(value)
    for key in SENSITIVE_KEYS:
        test_case.assertNotIn(key, text)


class ProspectRedactionTest(unittest.TestCase):
    def test_prospect_tools_redact_billing_fields(self):
        data_service._PROFILES.pop(PROSPECT_ID, None)

        built = build_prospect_profile.invoke({"prospect_id": PROSPECT_ID})
        assert_no_sensitive_keys(self, built["prospect_profile"])
        assert_no_sensitive_keys(self, data_service.get_profile_from_db(PROSPECT_ID)["prospect_profile"])

        data_service._PROFILES[PROSPECT_ID] = {
            **data_service._PROFILES[PROSPECT_ID],
            "billing_qualification": {
                "tax_id": None,
                "date_of_birth": None,
                "card_on_file": None,
                "credit_check_ref": None,
            },
        }
        cached = build_prospect_profile.invoke({"prospect_id": PROSPECT_ID})
        assert_no_sensitive_keys(self, cached["prospect_profile"])

        contact = get_prospect.invoke({"prospect_id": PROSPECT_ID})
        assert_no_sensitive_keys(self, contact["prospect"])

        captured = {}

        class FakeScoringLLM:
            def invoke(self, messages):
                captured["user"] = messages[1]["content"]

                class Result:
                    def model_dump(self):
                        return {"score": 1}

                return Result()

        import gtm_agent.gtm_agent as agent_module
        original_scoring_llm = agent_module._scoring_llm
        agent_module._scoring_llm = FakeScoringLLM()
        try:
            score_prospect.invoke({
                "prospect_profile": built["prospect_profile"],
                "offering": {
                    "required_tech_stack": ["AWS"],
                    "min_annual_revenue": 1,
                    "description": "Test offering",
                },
            })
        finally:
            agent_module._scoring_llm = original_scoring_llm
        assert_no_sensitive_keys(self, captured["user"])
