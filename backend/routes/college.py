from __future__ import annotations

from collections import Counter
import jwt

from flask import Blueprint, current_app, jsonify, request

college_bp = Blueprint("college_karthik", __name__, url_prefix="/api/college")


def _db():
    db = current_app.config.get("SKILLBRIDGE_DB")
    if db is None:
        raise RuntimeError("SKILLBRIDGE_DB adapter is not configured.")
    return db


def _require_college():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header.split(" ", 1)[1].strip()
    if token == "demo-college-token":
        return {"role": "college", "sub": 3}
    try:
        secret = current_app.config.get("JWT_SECRET", "sih-aicp-dev-secret")
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        if payload.get("role") != "college":
            return None
        return payload
    except Exception:
        return None


def _filter_students(students):
    q = (request.args.get("search") or "").strip().lower()
    degree = (request.args.get("degree") or "").strip().lower()
    internship = (request.args.get("internship_status") or "").strip().lower()
    placement = (request.args.get("placement_status") or "").strip().lower()

    def keep(s):
        if q and q not in str(s.get("name", "")).lower():
            return False
        if degree and degree != str(s.get("degree", "")).lower():
            return False
        if internship and internship != str(s.get("internship_status", "")).lower():
            return False
        if placement and placement != str(s.get("placement_status", "")).lower():
            return False
        return True

    return [s for s in students if keep(s)]


@college_bp.get("/students")
def students():
    user = _require_college()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = _filter_students(_db().get_college_students())
    return jsonify({"students": data, "total": len(data)})


@college_bp.get("/skill-gaps")
def skill_gaps():
    user = _require_college()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    gaps = _db().get_college_skill_gaps()
    return jsonify({"skill_gaps": gaps})


@college_bp.get("/analytics")
def analytics():
    user = _require_college()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    db = _db()
    students = db.get_college_students()
    applications = db.get_all_applications()
    opportunities = db.get_opportunities()

    skill_counts = Counter(
        skill
        for student in students
        for skill in student.get("skills", [])
    )
    gap_counts = Counter(
        gap
        for student in students
        for gap in student.get("skill_gaps", [])
    )
    application_status = Counter(
        str(row.get("status", "Unknown")) for row in applications
    )
    internship_status = Counter(
        str(row.get("internship_status", "Not Started")) for row in students
    )
    placement_status = Counter(
        str(row.get("placement_status", "Not Placed")) for row in students
    )

    placed = sum(v for k, v in placement_status.items() if k.lower() == "placed")
    participating = sum(
        v for k, v in internship_status.items()
        if k.lower() in {"participating", "completed", "active"}
    )

    return jsonify({
        "cards": {
            "total_students": len(students),
            "active_opportunities": len(opportunities),
            "internship_participation": participating,
            "students_placed": placed,
        },
        "top_skills": skill_counts.most_common(10),
        "top_skill_gaps": gap_counts.most_common(10),
        "application_status": dict(application_status),
        "internship_statistics": dict(internship_status),
        "placement_statistics": dict(placement_status),
    })
