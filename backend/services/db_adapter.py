"""SQLAlchemy database adapter for SkillBridge AI Matching & College Analytics.

This adapter implements the exact 7 methods required by Karthik's blueprints:
- get_student_skills(user_id)
- get_opportunities()
- get_courses()
- get_student_profile(user_id)
- get_college_students()
- get_all_applications()
- get_college_skill_gaps()

Mapping directly to existing SQLAlchemy models (MySQL & SQLite).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


class SQLAlchemySkillBridgeDB:
    def __init__(self, models=None):
        """Optionally pass models dict or import dynamically from app."""
        self._models = models

    def _get_models(self):
        if self._models:
            return self._models
        import app as backend_app
        return {
            "Student": backend_app.Student,
            "Opportunity": backend_app.Opportunity,
            "Application": backend_app.Application,
            "StudentSkill": backend_app.StudentSkill,
            "OpportunitySkill": backend_app.OpportunitySkill,
            "User": backend_app.User,
            "College": backend_app.College,
            "student_public": backend_app.student_public,
        }

    def get_student_skills(self, user_id: Any) -> list[str]:
        models = self._get_models()
        Student = models["Student"]
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            return []

        student = Student.query.filter(
            (Student.user_id == uid) | (Student.id == uid)
        ).first()
        if not student:
            return []
        return [s.skill_name for s in student.skills]

    def get_opportunities(self) -> list[dict[str, Any]]:
        models = self._get_models()
        Opportunity = models["Opportunity"]
        opps = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
        output = []
        for o in opps:
            comp_name = o.company.company_name if o.company else "Company"
            output.append({
                "id": o.id,
                "title": o.title,
                "type": o.type,
                "description": o.description or "",
                "location": o.location or "",
                "company": comp_name,
                "company_name": comp_name,
                "company_id": o.company_id,
                "required_skills": [s.skill_name for s in o.skills],
            })
        return output

    def get_courses(self) -> list[dict[str, Any]]:
        # Return empty list so Karthik's rule-based DEFAULT_COURSES catalog is used
        return []

    def get_student_profile(self, user_id: Any) -> dict[str, Any]:
        models = self._get_models()
        Student = models["Student"]
        student_public = models["student_public"]
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            return {}

        student = Student.query.filter(
            (Student.user_id == uid) | (Student.id == uid)
        ).first()
        if not student:
            return {}
        return student_public(student)

    def get_college_students(self) -> list[dict[str, Any]]:
        models = self._get_models()
        Student = models["Student"]
        Application = models["Application"]
        Opportunity = models["Opportunity"]

        students = Student.query.all()
        opps = Opportunity.query.all()
        all_required = set()
        for o in opps:
            for s in o.skills:
                all_required.add(s.skill_name.strip().lower())

        output = []
        for st in students:
            skills = [s.skill_name for s in st.skills]
            st_skill_set = {s.strip().lower() for s in skills}
            gaps = [r for r in all_required if r not in st_skill_set]

            apps = Application.query.filter_by(student_id=st.id).all()
            has_internship = any(
                str(a.status).lower() in ("accepted", "selected", "shortlisted")
                for a in apps
            )
            placed = any(
                str(a.status).lower() in ("accepted", "selected")
                for a in apps
            )

            output.append({
                "id": st.id,
                "user_id": st.user_id,
                "name": st.user.name if st.user else "Student",
                "degree": "B.Tech",
                "cgpa": "8.8",
                "department": st.department or "Computer Science",
                "skills": skills,
                "top_skills": skills[:5],
                "internship_status": "Participating" if has_internship else "Not Started",
                "placement_status": "Placed" if placed else "Not Placed",
                "skill_gaps": gaps,
                "application_count": len(apps),
            })
        return output

    def get_all_applications(self) -> list[dict[str, Any]]:
        models = self._get_models()
        Application = models["Application"]
        apps = Application.query.all()
        return [
            {
                "id": a.id,
                "student_id": a.student_id,
                "opportunity_id": a.opportunity_id,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in apps
        ]

    def get_college_skill_gaps(self) -> list[dict[str, Any]]:
        students = self.get_college_students()
        counts = Counter()
        for s in students:
            for gap in s.get("skill_gaps", []):
                counts[gap.capitalize()] += 1
        return [
            {"skill": skill, "students": count}
            for skill, count in counts.most_common(10)
        ]
