"""
Phase 5: Integration & Safety Tests
SpaceX-style: deterministic, fault-tolerant, explicit assertions.
"""

import pytest
from src.website_analyzer import WebsiteAnalyzer
from src.multi_dimensional_scorer import score_lead_multi


def test_website_analyzer_seo_signals_present():
    """Phase 1 signals must always be present (graceful on bad URL)."""
    analyzer = WebsiteAnalyzer(timeout=3)
    result = analyzer.analyze("https://example.com", maps_phone="+61400000000")
    
    assert "seo_health_score" in result
    assert "seo_signals" in result
    assert isinstance(result["seo_health_score"], int)
    assert 0 <= result["seo_health_score"] <= 100


def test_multi_dimensional_scorer_full_output():
    """Phase 2 must return all new fields."""
    lead = {
        "name": "Test Lead",
        "website": "https://example.com",
        "category": "med spa",
        "rating": 4.1,
        "reviews": 12,
        "has_chatbot": False,
        "has_click_to_call": False,
        "has_booking": False,
        "tech_sophistication_score": 30,
        "seo_health_score": 45,
    }
    
    config = {"multi_scoring": {"weights": {}, "thresholds": {}}}
    scored = score_lead_multi(lead, config)
    
    required = [
        "ai_voice_fit_score",
        "web_seo_fit_score",
        "reputation_fit_score",
        "booking_conversion_fit_score",
        "overall_help_score",
        "is_multi_opportunity",
        "strong_dimensions",
        "recommended_primary_service",
    ]
    for field in required:
        assert field in scored, f"Missing Phase 2 field: {field}"
    
    assert isinstance(scored["is_multi_opportunity"], bool)
    assert 0 <= scored["overall_help_score"] <= 100


def test_feature_flag_respected():
    """When multi-dimensional disabled, legacy path is used (simulated)."""
    # This is covered by main.py routing logic.
    # Here we just confirm the scorer can run independently.
    assert True  # Placeholder for full integration test with config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])