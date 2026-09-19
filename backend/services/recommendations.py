"""Rule-based learning recommendations for SkillBridge."""
from __future__ import annotations

from typing import Any, Iterable

DEFAULT_COURSES = {
    "docker": {"title": "Docker Fundamentals", "description": "Containers, images and Docker workflows."},
    "aws": {"title": "AWS Basics", "description": "Core AWS cloud services and deployment basics."},
    "statistics": {"title": "Statistics for Data Science", "description": "Probability, distributions and practical statistics."},
    "machine learning": {"title": "Machine Learning Fundamentals", "description": "Core supervised and unsupervised ML concepts."},
    "sql": {"title": "SQL Fundamentals", "description": "Queries, joins, aggregation and relational data."},
    "python": {"title": "Python Programming", "description": "Python fundamentals for software and data work."},
    "javascript": {"title": "JavaScript Essentials", "description": "Modern JavaScript for web applications."},
    "git": {"title": "Git & GitHub Basics", "description": "Version control, branching and collaboration."},
    "kubernetes": {"title": "Kubernetes Fundamentals", "description": "Containers, deployments, services and clusters."},
    "linux": {"title": "Linux Fundamentals", "description": "Command line, files, permissions and processes."},
    "terraform": {"title": "Terraform Fundamentals", "description": "Infrastructure as code with Terraform."},
    "react": {"title": "React.js Complete Guide", "description": "Components, state, hooks, and modern frontend development."},
    "flask": {"title": "Flask Web Development", "description": "REST APIs, database integration, and microservices in Python."},
    "data analysis": {"title": "Data Analysis with Python", "description": "Pandas, NumPy, visualization, and exploratory analysis."},
    "communication": {"title": "Professional Technical Communication", "description": "Writing documentation, presentations, and team collaboration."},
    "css": {"title": "Modern CSS & Responsive Design", "description": "Flexbox, Grid, animations, and modern layout techniques."},
}


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().replace("&", " and ").split())


def recommend_courses(
    missing_skills: Iterable[Any],
    courses: Iterable[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Match missing skills to course titles using transparent keyword rules."""
    catalog = list(courses or [])
    results = []

    for skill in missing_skills or []:
        skill_text = _norm(skill)
        if not skill_text:
            continue

        matches = []
        for course in catalog:
            haystack = _norm(
                " ".join(
                    str(course.get(k, ""))
                    for k in ("name", "title", "description", "skills")
                )
            )
            if skill_text in haystack or any(
                token in haystack for token in skill_text.split() if len(token) >= 3
            ):
                matches.append(course)

        if not matches:
            fallback = DEFAULT_COURSES.get(skill_text)
            if fallback:
                matches = [{"name": fallback["title"], **fallback, "source": "rule_based"}]

        for course in matches[:3]:
            results.append({
                "missing_skill": str(skill).strip(),
                "course": course,
                "reason": f"Recommended because {skill} is a missing required skill.",
            })

    # De-duplicate by course name/id while preserving order.
    seen = set()
    unique = []
    for item in results:
        course = item["course"]
        key = course.get("id") or course.get("name") or course.get("title")
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique
