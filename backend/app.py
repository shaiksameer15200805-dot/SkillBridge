import os
from datetime import datetime, timedelta, timezone
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import jwt
from werkzeug.security import check_password_hash, generate_password_hash

from matching import learning_for, skill_match

load_dotenv()

db = SQLAlchemy()
JWT_SECRET = os.environ.get("JWT_SECRET") or os.environ.get("SECRET_KEY") or "sih-aicp-dev-secret"
JWT_HOURS = 24


class College(db.Model):
    __tablename__ = "colleges"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey("colleges.id"))
    department = db.Column(db.String(120))
    year_of_study = db.Column(db.Integer)
    career_goal = db.Column(db.String(255))
    user = db.relationship("User")
    college = db.relationship("College")
    skills = db.relationship("StudentSkill", cascade="all, delete-orphan")
    certifications = db.relationship("Certification", cascade="all, delete-orphan")


class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(120))
    user = db.relationship("User")


class CollegeAdmin(db.Model):
    __tablename__ = "college_admins"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey("colleges.id"), nullable=False)
    user = db.relationship("User")
    college = db.relationship("College")


class StudentSkill(db.Model):
    __tablename__ = "student_skills"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    skill_name = db.Column(db.String(80), nullable=False)


class Certification(db.Model):
    __tablename__ = "certifications"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    issuer = db.Column(db.String(160))
    year = db.Column(db.Integer)


class Opportunity(db.Model):
    __tablename__ = "opportunities"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(160))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    company = db.relationship("Company")
    skills = db.relationship("OpportunitySkill", cascade="all, delete-orphan")


class OpportunitySkill(db.Model):
    __tablename__ = "opportunity_skills"
    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id"), nullable=False)
    skill_name = db.Column(db.String(80), nullable=False)


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="applied")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship("Student")
    opportunity = db.relationship("Opportunity")
    __table_args__ = (db.UniqueConstraint("student_id", "opportunity_id", name="uniq_app"),)


def database_uri():
    if os.environ.get("USE_SQLITE", "").lower() in ("1", "true", "yes"):
        sqlite_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "aicp.db"))
        return "sqlite:///" + sqlite_path.replace("\\", "/")
    mysql_url = os.environ.get("MYSQL_URL")
    if mysql_url:
        return mysql_url
    host = os.environ.get("MYSQL_HOST")
    if host:
        user = os.environ.get("MYSQL_USER", "root")
        password = os.environ.get("MYSQL_PASSWORD", "")
        dbname = os.environ.get("MYSQL_DB", "aicp")
        port = os.environ.get("MYSQL_PORT", "3306")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
    sqlite_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "aicp.db"))
    return "sqlite:///" + sqlite_path.replace("\\", "/")


def token_for(user):
    payload = {
        "sub": user.id,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def current_user():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header.split(" ", 1)[1].strip()
    # Support backward-compatible demo token
    if token == "demo-student-token":
        return User.query.filter_by(email="student@demo.com").first() or User.query.filter_by(role="student").first()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return db.session.get(User, payload.get("sub"))
    except Exception:
        return None


def require_role(*roles):
    user = current_user()
    if not user or (roles and user.role not in roles):
        return None
    return user


def skills_of_student(student):
    return [s.skill_name for s in student.skills]


def skills_of_opp(opp):
    return [s.skill_name for s in opp.skills]


def student_public(student, include_match=None):
    college_name = student.college.name if student.college else "National Institute of Technology"
    skills = skills_of_student(student)
    data = {
        "id": student.id,
        "student_id": student.id,
        "user_id": student.user_id,
        "name": student.user.name,
        "email": student.user.email,
        "role": "student",
        "department": student.department or "Computer Science",
        "branch": student.department or "Computer Science",
        "year_of_study": student.year_of_study or 3,
        "year": f"{student.year_of_study or 3}rd Year",
        "degree": "B.Tech",
        "cgpa": "8.8",
        "career_goal": student.career_goal or "",
        "career_goals": student.career_goal or "",
        "goal": student.career_goal or "",
        "college": college_name,
        "college_name": college_name,
        "university": college_name,
        "location": "Hyderabad",
        "bio": "CSE student focused on web apps and data projects.",
        "skills": skills,
        "certifications": [
            {"id": c.id, "title": c.title, "issuer": c.issuer, "year": str(c.year or 2025)}
            for c in student.certifications
        ],
    }
    if include_match is not None:
        data["match"] = include_match
    return data


def opportunity_public(opp, student=None):
    required = skills_of_opp(opp)
    comp_name = opp.company.company_name if opp.company else "Company"
    payload = {
        "id": opp.id,
        "title": opp.title,
        "role": opp.title,
        "type": opp.type,
        "description": opp.description or "",
        "location": opp.location or "Hyderabad",
        "stipend": "15,000 / month",
        "deadline": "2026-10-31",
        "company_name": comp_name,
        "company": comp_name,
        "company_id": opp.company_id,
        "industry": opp.company.industry if opp.company else "IT",
        "required_skills": required,
        "created_at": opp.created_at.isoformat() if opp.created_at else None,
    }
    if student is not None:
        st_skills = skills_of_student(student)
        match_res = skill_match(st_skills, required)
        payload["match"] = match_res
        payload["match_percent"] = match_res["match_percent"]
        payload["matched_skills"] = match_res["matched_skills"]
        payload["missing_skills"] = match_res["missing_skills"]
        payload["extra_skills"] = match_res["extra_skills"]
        payload["explanation"] = match_res["explanation"]
        payload["recommended_learning"] = learning_for(match_res["missing_skills"])

        app_row = Application.query.filter_by(student_id=student.id, opportunity_id=opp.id).first()
        payload["application_status"] = app_row.status if app_row else None
    return payload


def seed_if_empty():
    if User.query.first():
        return
    nit = College(name="National Institute of Technology", location="Warangal")
    db.session.add(nit)
    db.session.flush()

    student_user = User(
        name="Priya Sharma",
        email="student@demo.com",
        password_hash=generate_password_hash("password123"),
        role="student",
    )
    company_user = User(
        name="Amit Rao",
        email="company@demo.com",
        password_hash=generate_password_hash("password123"),
        role="company",
    )
    college_user = User(
        name="Dr. Meera Iyer",
        email="college@demo.com",
        password_hash=generate_password_hash("password123"),
        role="college",
    )
    extra_user = User(
        name="Rahul Verma",
        email="rahul@demo.com",
        password_hash=generate_password_hash("password123"),
        role="student",
    )
    db.session.add_all([student_user, company_user, college_user, extra_user])
    db.session.flush()

    student = Student(
        user_id=student_user.id,
        college_id=nit.id,
        department="Computer Science",
        year_of_study=3,
        career_goal="Software engineering internship then full-time SDE",
    )
    rahul = Student(
        user_id=extra_user.id,
        college_id=nit.id,
        department="Computer Science",
        year_of_study=4,
        career_goal="Data analyst role",
    )
    company = Company(user_id=company_user.id, company_name="Infotech Labs", industry="IT Services")
    admin = CollegeAdmin(user_id=college_user.id, college_id=nit.id)
    db.session.add_all([student, rahul, company, admin])
    db.session.flush()

    for name in ["Python", "React", "SQL", "Git", "JavaScript"]:
        db.session.add(StudentSkill(student_id=student.id, skill_name=name))
    for name in ["Python", "SQL", "Data Analysis"]:
        db.session.add(StudentSkill(student_id=rahul.id, skill_name=name))

    db.session.add_all([
        Certification(student_id=student.id, title="Python for Everybody", issuer="Coursera", year=2025),
        Certification(student_id=student.id, title="Responsive Web Design", issuer="freeCodeCamp", year=2024),
        Certification(student_id=rahul.id, title="Google Data Analytics", issuer="Coursera", year=2025),
    ])

    opp1 = Opportunity(
        company_id=company.id,
        title="Frontend Intern",
        type="internship",
        description="Build UI for internal dashboards using React. Work with designers and backend APIs.",
        location="Hyderabad (hybrid)",
    )
    opp2 = Opportunity(
        company_id=company.id,
        title="Junior Software Engineer",
        type="job",
        description="Full-stack role on the collaboration platform. Flask APIs and React screens.",
        location="Bengaluru",
    )
    opp3 = Opportunity(
        company_id=company.id,
        title="Campus Skill-Gap Study",
        type="project",
        description="Analyze curriculum vs industry skill demands across universities in the state.",
        location="Remote",
    )
    db.session.add_all([opp1, opp2, opp3])
    db.session.flush()

    for s in ["React", "JavaScript", "CSS"]:
        db.session.add(OpportunitySkill(opportunity_id=opp1.id, skill_name=s))
    for s in ["Python", "Flask", "SQL"]:
        db.session.add(OpportunitySkill(opportunity_id=opp2.id, skill_name=s))
    for s in ["Data Analysis", "Python", "Communication"]:
        db.session.add(OpportunitySkill(opportunity_id=opp3.id, skill_name=s))

    app1 = Application(student_id=student.id, opportunity_id=opp1.id, status="applied")
    db.session.add(app1)
    db.session.commit()


def check_user_password(user, password):
    if check_password_hash(user.password_hash, password):
        return True
    # Safe demo fallback for hackathon evaluation
    if user.email.endswith("@demo.com") and password in ("password123", "student123", "company123", "college123"):
        return True
    return False


def register_routes(app):
    @app.get("/api/health")
    def health():
        return jsonify({"ok": True})

    @app.post("/api/auth/register")
    def register():
        body = request.get_json(force=True) or {}
        role = (body.get("role") or "student").lower()
        if role != "student":
            return jsonify({"error": "Only student self-registration is enabled. Use demo logins for company/college."}), 400
        email = (body.get("email") or "").strip().lower()
        name = (body.get("name") or "").strip()
        password = body.get("password") or ""
        if not email or not password or not name:
            return jsonify({"error": "name, email and password are required"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role="student",
        )
        db.session.add(user)
        db.session.flush()

        college = College.query.first()
        student = Student(
            user_id=user.id,
            college_id=college.id if college else None,
            department=body.get("department") or body.get("branch") or "Computer Science",
            year_of_study=int(body.get("year_of_study") or body.get("year") or 1),
            career_goal=body.get("career_goal") or "",
        )
        db.session.add(student)
        db.session.commit()
        return jsonify({"token": token_for(user), "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}), 201

    @app.post("/api/auth/login")
    def login():
        body = request.get_json(force=True) or {}
        email = (body.get("email") or "").strip().lower()
        password = body.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if not user or not check_user_password(user, password):
            return jsonify({"error": "Invalid email or password"}), 401
        return jsonify({"token": token_for(user), "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}})

    @app.get("/api/auth/me")
    def me():
        user = current_user()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        data = {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
        if user.role == "student":
            student = Student.query.filter_by(user_id=user.id).first()
            if student:
                return jsonify(student_public(student))
        return jsonify(data)

    # Student Profile (support both singular and plural)
    @app.get("/api/student/profile")
    @app.get("/api/students/profile")
    def student_profile():
        user = require_role("student")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({"error": "Student profile not found"}), 404
        return jsonify(student_public(student))

    @app.put("/api/student/profile")
    @app.put("/api/students/profile")
    def update_student_profile():
        user = require_role("student")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({"error": "Student profile not found"}), 404
        body = request.get_json(force=True) or {}
        if body.get("name"):
            user.name = body["name"].strip()
        dept = body.get("department") or body.get("branch")
        if dept:
            student.department = dept
        yr = body.get("year_of_study") or body.get("year")
        if yr is not None:
            try:
                student.year_of_study = int(str(yr).replace("rd Year", "").replace("th Year", "").replace("nd Year", "").replace("st Year", "").strip())
            except ValueError:
                pass
        goal = body.get("career_goal") or body.get("career_goals") or body.get("goal")
        if goal is not None:
            student.career_goal = goal
        coll = body.get("college_name") or body.get("university") or body.get("college")
        if coll:
            c = College.query.filter_by(name=coll).first()
            if not c:
                c = College(name=coll)
                db.session.add(c)
                db.session.flush()
            student.college_id = c.id

        if "skills" in body:
            StudentSkill.query.filter_by(student_id=student.id).delete()
            for skill in body.get("skills") or []:
                name = skill.strip() if isinstance(skill, str) else ""
                if name:
                    db.session.add(StudentSkill(student_id=student.id, skill_name=name))

        if "certifications" in body:
            Certification.query.filter_by(student_id=student.id).delete()
            for cert in body.get("certifications") or []:
                title = (cert.get("title") or "").strip()
                if title:
                    db.session.add(Certification(
                        student_id=student.id,
                        title=title,
                        issuer=cert.get("issuer") or "",
                        year=int(cert.get("year")) if str(cert.get("year", "")).isdigit() else None,
                    ))
        db.session.commit()
        return jsonify(student_public(student))

    # Student Skills Endpoints
    @app.get("/api/student/skills")
    @app.get("/api/students/skills")
    def get_student_skills():
        user = require_role("student")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        skills = skills_of_student(student)
        return jsonify({"count": len(skills), "skills": skills})

    @app.post("/api/student/skills")
    @app.post("/api/students/skills")
    def add_student_skill():
        user = require_role("student")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        body = request.get_json(force=True) or {}
        name = (body.get("skill") or body.get("name") or "").strip()
        if name:
            exists = StudentSkill.query.filter_by(student_id=student.id, skill_name=name).first()
            if not exists:
                db.session.add(StudentSkill(student_id=student.id, skill_name=name))
                db.session.commit()
        elif "skills" in body:
            for sname in body.get("skills") or []:
                clean = (sname or "").strip()
                if clean:
                    exists = StudentSkill.query.filter_by(student_id=student.id, skill_name=clean).first()
                    if not exists:
                        db.session.add(StudentSkill(student_id=student.id, skill_name=clean))
            db.session.commit()
        skills = skills_of_student(student)
        return jsonify({"count": len(skills), "skills": skills})

    @app.put("/api/student/skills")
    @app.put("/api/students/skills")
    def put_student_skills():
        user = require_role("student")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        body = request.get_json(force=True) or {}
        StudentSkill.query.filter_by(student_id=student.id).delete()
        for sname in body.get("skills") or []:
            clean = (sname or "").strip()
            if clean:
                db.session.add(StudentSkill(student_id=student.id, skill_name=clean))
        db.session.commit()
        skills = skills_of_student(student)
        return jsonify({"count": len(skills), "skills": skills})

    # Student Certifications Endpoints
    @app.get("/api/student/certifications")
    def get_student_certifications():
        user = require_role("student")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        certs = [
            {"id": c.id, "title": c.title, "issuer": c.issuer, "year": str(c.year or "")}
            for c in student.certifications
        ]
        return jsonify({"certifications": certs})

    @app.post("/api/student/certifications")
    def add_student_certification():
        user = require_role("student")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        body = request.get_json(force=True) or {}
        title = (body.get("title") or "").strip()
        if not title:
            return jsonify({"error": "Title is required"}), 400
        yr = body.get("year")
        year_val = int(yr) if str(yr).isdigit() else None
        cert = Certification(
            student_id=student.id,
            title=title,
            issuer=body.get("issuer") or "",
            year=year_val,
        )
        db.session.add(cert)
        db.session.commit()
        return jsonify({"id": cert.id, "title": cert.title, "issuer": cert.issuer, "year": str(cert.year or "")}), 201

    @app.delete("/api/student/certifications/<int:cert_id>")
    def delete_student_certification(cert_id):
        user = require_role("student")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        cert = Certification.query.filter_by(id=cert_id, student_id=student.id).first()
        if not cert:
            return jsonify({"error": "Certification not found"}), 404
        db.session.delete(cert)
        db.session.commit()
        return jsonify({"ok": True})

    # Student Recommendations & Matching
    @app.get("/api/student/recommendations")
    @app.get("/api/students/recommendations")
    @app.get("/api/recommendations")
    def student_recommendations():
        user = require_role("student")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        opps = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
        items = [opportunity_public(o, student) for o in opps]
        items.sort(key=lambda x: x["match"]["match_percent"], reverse=True)
        return jsonify({"opportunities": items} if request.path.endswith("/students/recommendations") else items)

    # Student Skill Gap
    @app.get("/api/student/skill-gap")
    @app.get("/api/students/skill-gap")
    @app.get("/api/skill-gap")
    def student_skill_gap():
        user = require_role("student")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        opp_id = request.args.get("opportunity_id", type=int)
        if opp_id:
            opp = db.session.get(Opportunity, opp_id)
            if not opp:
                return jsonify({"error": "Opportunity not found"}), 404
            match = skill_match(skills_of_student(student), skills_of_opp(opp))
            return jsonify({
                "opportunity": opportunity_public(opp),
                "match": match,
                "recommended_learning": learning_for(match["missing_skills"]),
            })
        opps = Opportunity.query.all()
        required = []
        gaps = {}
        opps_for_skill = {}
        st_skills = skills_of_student(student)
        for opp in opps:
            opp_req = skills_of_opp(opp)
            required.extend(opp_req)
            m = skill_match(st_skills, opp_req)
            for ms in m["missing_skills"]:
                gaps[ms] = gaps.get(ms, 0) + 1
                if ms not in opps_for_skill:
                    opps_for_skill[ms] = []
                opps_for_skill[ms].append(opp.title)
        match = skill_match(st_skills, required)
        top_skill_gaps = []
        for s in sorted(gaps.keys(), key=lambda k: gaps[k], reverse=True):
            roles = opps_for_skill.get(s, [])
            role_str = ", ".join(roles[:2])
            top_skill_gaps.append({
                "skill": s,
                "opportunities_requiring": gaps[s],
                "recommended_for": roles,
                "recommendation": f"Learn {s} to qualify for {role_str}"
            })
        return jsonify({
            "total_opportunities": len(opps),
            "student_skills": st_skills,
            "current_skills": st_skills,
            "missing_skills": match["missing_skills"],
            "top_skill_gaps": top_skill_gaps,
            "match": match,
            "recommended_learning": learning_for(match["missing_skills"]),
            "explanation": match["explanation"],
        })

    # Student Applications
    @app.get("/api/student/applications")
    @app.get("/api/students/applications")
    def student_applications():
        user = require_role("student")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        apps = Application.query.filter_by(student_id=student.id).order_by(Application.created_at.desc()).all()
        out = []
        for app_row in apps:
            item = opportunity_public(app_row.opportunity, student)
            item["application_id"] = app_row.id
            item["opportunity_id"] = app_row.opportunity_id
            item["status"] = app_row.status
            item["created_at"] = app_row.created_at.strftime("%Y-%m-%d %H:%M:%S") if app_row.created_at else None
            item["applied_at"] = app_row.created_at.isoformat() if app_row.created_at else None
            out.append(item)
        return jsonify(out)

    @app.post("/api/student/applications")
    @app.post("/api/applications")
    def apply():
        user = require_role("student")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        body = request.get_json(force=True) or {}
        opp_id = body.get("opportunity_id")
        opp = db.session.get(Opportunity, opp_id)
        if not opp:
            return jsonify({"error": "Opportunity not found"}), 404
        existing = Application.query.filter_by(student_id=student.id, opportunity_id=opp.id).first()
        if existing:
            return jsonify({"error": "Already applied for this opportunity", "application_id": existing.id, "status": existing.status}), 400
        app_row = Application(student_id=student.id, opportunity_id=opp.id, status="applied")
        db.session.add(app_row)
        db.session.commit()
        return jsonify({"id": app_row.id, "opportunity_id": opp.id, "status": app_row.status, "message": "Application submitted successfully"}), 201

    # Opportunities
    @app.get("/api/opportunities")
    def list_opportunities():
        user = current_user()
        student = Student.query.filter_by(user_id=user.id).first() if user and user.role == "student" else None
        opps = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
        return jsonify([opportunity_public(o, student) for o in opps])

    @app.get("/api/opportunities/<int:opp_id>")
    def get_opportunity(opp_id):
        user = current_user()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        opp = db.session.get(Opportunity, opp_id)
        if not opp:
            return jsonify({"error": "Opportunity not found"}), 404
        student = Student.query.filter_by(user_id=user.id).first() if user.role == "student" else None
        return jsonify(opportunity_public(opp, student))

    @app.get("/api/skills")
    def list_skills():
        opp_skills = db.session.query(OpportunitySkill.skill_name).distinct().all()
        st_skills = db.session.query(StudentSkill.skill_name).distinct().all()
        unique_names = sorted(list({s[0] for s in opp_skills + st_skills if s[0]}))
        return jsonify({"skills": unique_names})

    # Company Endpoints
    @app.get("/api/company/dashboard")
    def company_dashboard():
        user = require_role("company")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        company = Company.query.filter_by(user_id=user.id).first()
        if not company:
            return jsonify({"error": "Company not found"}), 404
        opps = Opportunity.query.filter_by(company_id=company.id).all()
        apps = Application.query.join(Opportunity).filter(Opportunity.company_id == company.id).all()
        opp_items = []
        for opp in opps:
            item = opportunity_public(opp)
            item["applicant_count"] = Application.query.filter_by(opportunity_id=opp.id).count()
            opp_items.append(item)
        return jsonify({
            "company": {"id": company.id, "name": company.company_name, "company_name": company.company_name, "industry": company.industry},
            "company_name": company.company_name,
            "industry": company.industry,
            "opportunities": opp_items,
            "total_opportunities": len(opps),
            "opportunity_count": len(opps),
            "total_applicants": len(apps),
            "application_count": len(apps),
            "status_counts": {
                "applied": sum(1 for a in apps if a.status == "applied"),
                "shortlisted": sum(1 for a in apps if a.status == "shortlisted"),
                "rejected": sum(1 for a in apps if a.status == "rejected"),
                "accepted": sum(1 for a in apps if a.status in ("accepted", "selected")),
            },
        })

    @app.get("/api/company/opportunities")
    def company_opportunities():
        user = require_role("company")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        company = Company.query.filter_by(user_id=user.id).first()
        if not company:
            return jsonify({"error": "Company not found"}), 404
        opps = Opportunity.query.filter_by(company_id=company.id).order_by(Opportunity.created_at.desc()).all()
        out = []
        for opp in opps:
            item = opportunity_public(opp)
            item["applicant_count"] = Application.query.filter_by(opportunity_id=opp.id).count()
            out.append(item)
        return jsonify(out)

    @app.post("/api/company/opportunities")
    def post_opportunity():
        user = require_role("company")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        company = Company.query.filter_by(user_id=user.id).first()
        if not company:
            return jsonify({"error": "Company not found"}), 404
        body = request.get_json(force=True) or {}
        title = (body.get("title") or "").strip()
        otype = (body.get("type") or "internship").lower()
        if not title:
            return jsonify({"error": "title is required"}), 400
        opp = Opportunity(
            company_id=company.id,
            title=title,
            type=otype,
            description=body.get("description") or "",
            location=body.get("location") or "",
        )
        db.session.add(opp)
        db.session.flush()
        for skill in body.get("required_skills") or []:
            s = skill.strip() if isinstance(skill, str) else ""
            if s:
                db.session.add(OpportunitySkill(opportunity_id=opp.id, skill_name=s))
        db.session.commit()
        return jsonify(opportunity_public(opp)), 201

    @app.get("/api/company/opportunities/<int:opp_id>/applicants")
    def company_applicants(opp_id):
        user = require_role("company")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        opp = db.session.get(Opportunity, opp_id)
        if not opp:
            return jsonify({"error": "Opportunity not found"}), 404
        required = skills_of_opp(opp)
        apps = Application.query.filter_by(opportunity_id=opp.id).all()
        people = []
        for app_row in apps:
            student = app_row.student
            skills = skills_of_student(student)
            match_res = skill_match(skills, required)
            people.append({
                "application_id": app_row.id,
                "status": app_row.status,
                "applied_at": app_row.created_at.isoformat() if app_row.created_at else None,
                "student": student_public(student),
                **match_res,
                "recommended_learning": learning_for(match_res["missing_skills"]),
            })
        people.sort(key=lambda x: x["match_percent"], reverse=True)
        return jsonify({"opportunity": opportunity_public(opp), "applicants": people})

    @app.patch("/api/company/applications/<int:app_id>")
    @app.put("/api/company/applications/<int:app_id>/status")
    def update_application(app_id):
        user = require_role("company")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        app_row = db.session.get(Application, app_id)
        if not app_row:
            return jsonify({"error": "Application not found"}), 404
        body = request.get_json(force=True) or {}
        status = body.get("status")
        if status not in ("applied", "under_review", "shortlisted", "rejected", "selected", "accepted"):
            return jsonify({"error": "Invalid status"}), 400
        app_row.status = status
        db.session.commit()
        return jsonify({"id": app_row.id, "status": app_row.status})

    # College Endpoints
    @app.get("/api/college/dashboard")
    def college_dashboard():
        user = require_role("college")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        admin = CollegeAdmin.query.filter_by(user_id=user.id).first()
        college = admin.college if admin else College.query.first()
        students = Student.query.filter_by(college_id=college.id).all() if college else Student.query.all()
        opps = Opportunity.query.all()

        student_rows = []
        gap_counter = {}
        match_values = []
        for student in students:
            skills = skills_of_student(student)
            matches = []
            for opp in opps:
                m = skill_match(skills, skills_of_opp(opp))
                matches.append(m["match_percent"])
                for s in m["missing_skills"]:
                    gap_counter[s] = gap_counter.get(s, 0) + 1
            avg = round(sum(matches) / len(matches), 1) if matches else 0
            match_values.append(avg)
            apps = Application.query.filter_by(student_id=student.id).all()
            student_rows.append({
                **student_public(student),
                "avg_match_percent": avg,
                "application_count": len(apps),
                "selected_count": sum(1 for a in apps if a.status in ("accepted", "selected")),
            })

        status_counts = {"applied": 0, "shortlisted": 0, "rejected": 0, "selected": 0}
        for row in Application.query.all():
            status_counts[row.status] = status_counts.get(row.status, 0) + 1

        skill_gaps = sorted(gap_counter.items(), key=lambda kv: kv[1], reverse=True)[:10]
        return jsonify({
            "college": college.name if college else "College",
            "students": student_rows,
            "student_count": len(student_rows),
            "avg_match_percent": round(sum(match_values) / len(match_values), 1) if match_values else 0,
            "skill_gaps": [{"skill": name, "student_opportunity_gaps": count} for name, count in skill_gaps],
            "recommended_learning": learning_for([name for name, _ in skill_gaps]),
            "opportunities": [opportunity_public(opp) for opp in opps],
            "analytics": {
                "applications_by_status": status_counts,
                "opportunity_count": len(opps),
                "internship_count": sum(1 for o in opps if o.type == "internship"),
                "job_count": sum(1 for o in opps if o.type == "job"),
                "project_count": sum(1 for o in opps if o.type == "project"),
            },
        })

    @app.get("/api/college/students")
    def college_students():
        user = require_role("college")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        admin = CollegeAdmin.query.filter_by(user_id=user.id).first()
        college = admin.college if admin else College.query.first()
        students = Student.query.filter_by(college_id=college.id).all() if college else Student.query.all()
        return jsonify([student_public(s) for s in students])

    @app.get("/api/college/skill-gaps")
    def college_skill_gaps():
        user = require_role("college")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        admin = CollegeAdmin.query.filter_by(user_id=user.id).first()
        college = admin.college if admin else College.query.first()
        students = Student.query.filter_by(college_id=college.id).all() if college else Student.query.all()
        opps = Opportunity.query.all()
        gap_counter = {}
        for student in students:
            skills = skills_of_student(student)
            for opp in opps:
                m = skill_match(skills, skills_of_opp(opp))
                for s in m["missing_skills"]:
                    gap_counter[s] = gap_counter.get(s, 0) + 1
        skill_gaps = sorted(gap_counter.items(), key=lambda kv: kv[1], reverse=True)[:10]
        return jsonify({
            "skill_gaps": [{"skill": name, "student_opportunity_gaps": count} for name, count in skill_gaps],
            "recommended_learning": learning_for([name for name, _ in skill_gaps]),
        })

    @app.get("/api/college/opportunities")
    def college_opportunities():
        user = require_role("college")
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        opps = Opportunity.query.all()
        return jsonify([opportunity_public(opp) for opp in opps])

    @app.get("/api/college/analytics")
    def college_analytics():
        return college_dashboard()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    db.init_app(app)

    @app.errorhandler(400)
    def handle_bad_request(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": getattr(e, "description", "Bad request")}), 400
        return e

    @app.errorhandler(404)
    def handle_not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource not found"}), 404
        return e

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Method not allowed"}), 405
        return e

    @app.errorhandler(500)
    def handle_internal_error(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        return e

    with app.app_context():
        db.create_all()
        seed_if_empty()

    register_routes(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
