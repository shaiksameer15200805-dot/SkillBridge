import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.matching_engine import calculate_match, rank_opportunities


def test_case_is_ignored():
    result = calculate_match(["Python"], ["python"])
    assert result["match_percentage"] == 100
    assert result["matched_skills"] == ["python"]
    assert result["missing_skills"] == []


def test_spacing_and_punctuation_are_normalized():
    result = calculate_match(
        ["GitHub", "Machine-Learning", "SQL"],
        ["git/github", "machine learning", "sql", "Docker"],
    )
    assert result["match_percentage"] == 75
    assert len(result["matched_skills"]) == 3
    assert result["missing_skills"] == ["Docker"]


def test_missing_skills():
    result = calculate_match(["Python", "SQL"], ["Python", "SQL", "Docker"])
    assert abs(result["match_percentage"] - 66.67) < 0.1
    assert result["missing_skills"] == ["Docker"]


def test_empty_required_skills():
    result = calculate_match(["Python"], [])
    assert result["match_percentage"] == 0
    assert result["matched_skills"] == []
    assert result["missing_skills"] == []


def test_duplicate_required_skills_count_once():
    result = calculate_match(["Python"], ["Python", "python", "PYTHON"])
    assert result["match_percentage"] == 100


def test_rank_opportunities_highest_first():
    opportunities = [
        {"id": 1, "title": "A", "required_skills": ["Python", "SQL", "Docker"]},
        {"id": 2, "title": "B", "required_skills": ["Python"]},
        {"id": 3, "title": "C", "required_skills": ["Java"]},
    ]
    ranked = rank_opportunities(["Python", "SQL"], opportunities)
    assert [x["opportunity"]["id"] for x in ranked] == [2, 1, 3]
    assert ranked[0]["match_percentage"] == 100


if __name__ == "__main__":
    test_case_is_ignored()
    test_spacing_and_punctuation_are_normalized()
    test_missing_skills()
    test_empty_required_skills()
    test_duplicate_required_skills_count_once()
    test_rank_opportunities_highest_first()
    print("ALL KARTHIK MATCHING ENGINE TESTS PASSED!")
