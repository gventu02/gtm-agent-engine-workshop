import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile


def test_update_prospect_info_persists_technology_and_invalidates_profile():
    prospect_id = "LEAD-39002"
    original_tech_stack = list(data_service.PROSPECTS[prospect_id]["tech_stack"])
    original_profile = data_service._PROFILES.pop(prospect_id, None)

    try:
        build_prospect_profile.invoke({"prospect_id": prospect_id})
        result = data_service.update_prospect_info(prospect_id, "Terraform")

        assert result["updated"] is True
        assert "Terraform" in data_service.fetch_tech_stack(prospect_id)
        profile = build_prospect_profile.invoke({"prospect_id": prospect_id})
        assert "Terraform" in profile["prospect_profile"]["tech_stack"]
    finally:
        data_service.PROSPECTS[prospect_id]["tech_stack"] = original_tech_stack
        data_service._PROFILES.pop(prospect_id, None)
        if original_profile is not None:
            data_service._PROFILES[prospect_id] = original_profile
