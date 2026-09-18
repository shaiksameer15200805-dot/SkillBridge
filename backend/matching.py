"""Explainable skill matching — no ML model.

Match % = (shared skills / required skills) * 100
"""

LEARNING_CATALOG = {
    "python": {
        "title": "Python Essentials",
        "provider": "NPTEL / freeCodeCamp",
        "hours": 20,
        "link": "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
    },
    "java": {
        "title": "Java Programming",
        "provider": "NPTEL",
        "hours": 24,
        "link": "https://onlinecourses.nptel.ac.in/",
    },
    "javascript": {
        "title": "JavaScript Algorithms",
        "provider": "freeCodeCamp",
        "hours": 18,
        "link": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
    },
    "react": {
        "title": "React — Official Tutorial",
        "provider": "react.dev",
        "hours": 12,
        "link": "https://react.dev/learn",
    },
    "sql": {
        "title": "SQL for Beginners",
        "provider": "Mode Analytics",
        "hours": 10,
        "link": "https://mode.com/sql-tutorial/",
    },
    "mysql": {
        "title": "MySQL Crash Course",
        "provider": "MySQL Docs",
        "hours": 8,
        "link": "https://dev.mysql.com/doc/",
    },
    "flask": {
        "title": "Flask Mega-Tutorial (intro)",
        "provider": "Flask Docs",
        "hours": 10,
        "link": "https://flask.palletsprojects.com/",
    },
    "machine learning": {
        "title": "Intro to Machine Learning",
        "provider": "Kaggle",
        "hours": 16,
        "link": "https://www.kaggle.com/learn/intro-to-machine-learning",
    },
    "data analysis": {
        "title": "Pandas Data Analysis",
        "provider": "Kaggle",
        "hours": 8,
        "link": "https://www.kaggle.com/learn/pandas",
    },
    "communication": {
        "title": "Workplace Communication",
        "provider": "Coursera (audit)",
        "hours": 6,
        "link": "https://www.coursera.org/",
    },
    "git": {
        "title": "Git & GitHub",
        "provider": "GitHub Skills",
        "hours": 4,
        "link": "https://skills.github.com/",
    },
    "ui/ux": {
        "title": "UI Design Foundations",
        "provider": "Figma Learn",
        "hours": 8,
        "link": "https://www.figma.com/resource-library/",
    },
    "aws": {
        "title": "AWS Cloud Practitioner Essentials",
        "provider": "AWS Skill Builder",
        "hours": 12,
        "link": "https://skillbuilder.aws/",
    },
    "excel": {
        "title": "Excel for Data",
        "provider": "Microsoft Learn",
        "hours": 6,
        "link": "https://learn.microsoft.com/excel/",
    },
}


def normalize_skill(name):
    return (name or "").strip().lower()


def unique_normalized(skills):
    seen = []
    used = set()
    for skill in skills or []:
        key = normalize_skill(skill)
        if key and key not in used:
            used.add(key)
            seen.append(key)
    return seen


def match_skills(student_skills, required_skills):
    student = set(unique_normalized(student_skills))
    required = unique_normalized(required_skills)

    if not required:
        return {
            "match_percent": 100.0,
            "matched_skills": sorted(student),
            "missing_skills": [],
            "extra_skills": sorted(student),
            "required_count": 0,
            "matched_count": 0,
            "explanation": "This opportunity lists no required skills, so match is 100%.",
        }

    matched = sorted(student.intersection(required))
    missing = [skill for skill in required if skill not in student]
    extra = sorted(student.difference(required))
    percent = round(100.0 * len(matched) / len(required), 1)

    parts = [
        f"Matched {len(matched)} of {len(required)} required skills ({percent}%)."
    ]
    if matched:
        parts.append("Matched: " + ", ".join(matched) + ".")
    else:
        parts.append("No overlapping skills yet.")
    if missing:
        parts.append("Skill gaps: " + ", ".join(missing) + ".")
    else:
        parts.append("No skill gaps.")

    return {
        "match_percent": percent,
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
        "required_count": len(required),
        "matched_count": len(matched),
        "explanation": " ".join(parts),
    }


def recommend_learning(missing_skills):
    recs = []
    for skill in unique_normalized(missing_skills):
        course = LEARNING_CATALOG.get(skill)
        if course:
            recs.append({"skill": skill, **course})
        else:
            recs.append(
                {
                    "skill": skill,
                    "title": f"Learn {skill.title()}",
                    "provider": "YouTube / NPTEL search",
                    "hours": 8,
                    "link": f"https://www.google.com/search?q={skill}+nptel+course",
                }
            )
    return recs
