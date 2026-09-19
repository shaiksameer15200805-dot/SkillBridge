"""Explainable SkillBridge opportunity matching.

No ML model is used. Skill names are normalized and required skills are matched
case-insensitively. Punctuation/spacing differences are also normalized.
"""
from __future__ import annotations

import re
from typing import Any, Iterable


def normalize_skill(skill: Any) -> str:
    """Normalize a skill for reliable comparison."""
    value = "" if skill is None else str(skill).strip().lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[/_+\-]+", " ", value)
    value = re.sub(r"[^a-z0-9#.\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def display_skill(skill: Any) -> str:
    return "" if skill is None else str(skill).strip()


def calculate_match(
    student_skills: Iterable[Any],
    required_skills: Iterable[Any],
) -> dict[str, Any]:
    """Return matched skills, missing skills and match percentage.

    Formula:
        matched required skills / total required skills * 100

    Duplicate required skills are counted once after normalization.
    """
    student = {}
    for skill in student_skills or []:
        normalized = normalize_skill(skill)
        if normalized:
            student.setdefault(normalized, display_skill(skill))
            for part in re.split(r"[/|]+", str(skill)):
                norm_part = normalize_skill(part)
                if norm_part:
                    student.setdefault(norm_part, display_skill(skill))

    required = {}
    for skill in required_skills or []:
        normalized = normalize_skill(skill)
        if normalized:
            required.setdefault(normalized, display_skill(skill))

    matched_keys = []
    missing_keys = []
    for key, disp in required.items():
        key_parts = [normalize_skill(p) for p in re.split(r"[/|]+", disp) if normalize_skill(p)]
        if key in student or any(p in student for p in key_parts):
            matched_keys.append(key)
        else:
            missing_keys.append(key)

    total = len(required)
    percentage = round((len(matched_keys) / total) * 100, 2) if total else 0.0

    return {
        "matched_skills": [required[key] for key in matched_keys],
        "missing_skills": [required[key] for key in missing_keys],
        "match_percentage": percentage,
    }


def _as_skill_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        # Supports "Python, SQL, Docker" and "Python;SQL;Docker".
        return [x.strip() for x in re.split(r"[,;|]", value) if x.strip()]
    if isinstance(value, dict):
        return list(value.keys())
    return [str(x).strip() for x in value if str(x).strip()]


def _opportunity_required_skills(opportunity: Any) -> list[str]:
    if isinstance(opportunity, dict):
        for key in ("required_skills", "requirements", "skills"):
            if key in opportunity:
                return _as_skill_list(opportunity[key])
        return []
    return []


def rank_opportunities(
    student_skills: Iterable[Any],
    opportunities: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Rank opportunities by match percentage, highest first.

    Each item contains the original opportunity plus match details and a short,
    deterministic explanation.
    """
    student_skills = list(student_skills or [])
    ranked = []

    for opportunity in opportunities or []:
        required = _opportunity_required_skills(opportunity)
        result = calculate_match(student_skills, required)

        domain = (
            opportunity.get("career_preference")
            or opportunity.get("domain")
            or opportunity.get("category")
            or ""
        )
        student_domains = {
            normalize_skill(x) for x in student_skills if normalize_skill(x)
        }
        domain_aligned = normalize_skill(domain) in student_domains if domain else False

        reason = (
            f"{len(result['matched_skills'])} required skills matched"
            + (" and career domain aligns." if domain_aligned else ".")
        )

        ranked.append({
            "opportunity": opportunity,
            **result,
            "reason": reason,
        })

    ranked.sort(
        key=lambda item: (
            item["match_percentage"],
            len(item["matched_skills"]),
        ),
        reverse=True,
    )
    return ranked
