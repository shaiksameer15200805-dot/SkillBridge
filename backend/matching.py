"""Explainable skill-match scoring. No ML — set overlap only."""


def normalize(skill):
    return (skill or "").strip().lower()


def unique_keep_order(items):
    seen = set()
    out = []
    for item in items or []:
        key = normalize(item)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item.strip())
    return out


def skill_match(student_skills, required_skills):
    student_list = unique_keep_order(student_skills or [])
    required_list = unique_keep_order(required_skills or [])
    student_set = {normalize(s) for s in student_list}

    matched = [s for s in required_list if normalize(s) in student_set]
    missing = [s for s in required_list if normalize(s) not in student_set]
    extra = [s for s in student_list if normalize(s) not in {normalize(r) for r in required_list}]

    total = len(required_list)
    percent = round(100 * len(matched) / total) if total else 0

    if total == 0:
        explanation = "This opportunity has no required skills listed, so match is shown as 0%."
    elif not matched:
        explanation = (
            f"0 of {total} required skills match. Missing: {', '.join(missing)}."
        )
    elif not missing:
        explanation = f"All {total} required skills match: {', '.join(matched)}."
    else:
        explanation = (
            f"{len(matched)} of {total} required skills match "
            f"({', '.join(matched)}). Gap: {', '.join(missing)}."
        )

    return {
        "match_percent": percent,
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
        "required_count": total,
        "matched_count": len(matched),
        "explanation": explanation,
    }


# Aliases for compatibility
match_skills = skill_match


LEARNING_CATALOG = {
    "python": {
        "title": "Python for Everybody",
        "provider": "Coursera",
        "url": "https://www.coursera.org/specializations/python",
    },
    "javascript": {
        "title": "JavaScript Basics",
        "provider": "MDN",
        "url": "https://developer.mozilla.org/en-US/docs/Learn/JavaScript",
    },
    "react": {
        "title": "React Quick Start",
        "provider": "React.dev",
        "url": "https://react.dev/learn",
    },
    "sql": {
        "title": "Intro to SQL",
        "provider": "Khan Academy",
        "url": "https://www.khanacademy.org/computing/computer-programming/sql",
    },
    "mysql": {
        "title": "MySQL Getting Started",
        "provider": "MySQL Docs",
        "url": "https://dev.mysql.com/doc/mysql-getting-started/en/",
    },
    "flask": {
        "title": "Flask Mega-Tutorial",
        "provider": "Miguel Grinberg",
        "url": "https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world",
    },
    "docker": {
        "title": "Docker Get Started",
        "provider": "Docker",
        "url": "https://docs.docker.com/get-started/",
    },
    "aws": {
        "title": "AWS Cloud Practitioner Essentials",
        "provider": "AWS Skill Builder",
        "url": "https://skillbuilder.aws/",
    },
    "java": {
        "title": "Java Programming",
        "provider": "Oracle",
        "url": "https://dev.java/learn/",
    },
    "data analysis": {
        "title": "Data Analysis with Python",
        "provider": "freeCodeCamp",
        "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/",
    },
    "machine learning": {
        "title": "Machine Learning Crash Course",
        "provider": "Google",
        "url": "https://developers.google.com/machine-learning/crash-course",
    },
    "communication": {
        "title": "Technical Communication",
        "provider": "Coursera",
        "url": "https://www.coursera.org/learn/technical-communication",
    },
    "git": {
        "title": "Git Handbook",
        "provider": "GitHub",
        "url": "https://guides.github.com/introduction/git-handbook/",
    },
    "node.js": {
        "title": "Node.js Guides",
        "provider": "nodejs.org",
        "url": "https://nodejs.org/en/learn",
    },
}


def learning_for(missing_skills):
    recs = []
    for skill in unique_keep_order(missing_skills or []):
        item = LEARNING_CATALOG.get(normalize(skill), {
            "title": f"Learn {skill}",
            "provider": "Search",
            "url": f"https://www.google.com/search?q=learn+{skill.replace(' ', '+')}+course",
        })
        recs.append({"skill": skill, **item})
    return recs


# Aliases for compatibility
recommend_learning = learning_for
