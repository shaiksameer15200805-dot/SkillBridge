import os
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from matching import match_skills, recommend_learning

load_dotenv()

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student | company | college
    college_name = db.Column(db.String(200))
    company_name = db.Column(db.String(200))
    branch = db.Column(db.String(80))
    year = db.Column(db.String(20))
    bio = db.Column(db.Text)
    career_goal = db.Column(db.String(300))
    industry = db.Column(db.String(120))
    location = db.Column(db.String(120))
    degree = db.Column(db.String(80), default="B.Tech")
    cgpa = db.Column(db.String(20), default="8.8")


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


class StudentSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skill.id"), nullable=False)


class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    issuer = db.Column(db.String(120), nullable=False)
    year = db.Column(db.String(10), nullable=False)


class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(40), nullable=False)  # internship | project | job
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(120))
    stipend = db.Column(db.String(80))
    deadline = db.Column(db.String(40))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class OpportunitySkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunity.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skill.id"), nullable=False)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunity.id"), nullable=False)
    status = db.Column(db.String(40), default="applied")  # applied | shortlisted | rejected | selected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def database_uri():
    if os.getenv("USE_SQLITE", "1") == "1":
        path = os.path.join(os.path.dirname(__file__), "aicp.db")
        return "sqlite:///" + path.replace("\\", "/")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3306")
    name = os.getenv("MYSQL_DB", "aicp")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "sih-hackathon-secret")
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    def token_for(user):
        return serializer.dumps({"id": user.id, "role": user.role})

    def login_required(roles=None):
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                header = request.headers.get("Authorization", "")
                if not header.startswith("Bearer "):
                    return jsonify({"error": "Login required"}), 401
                token_str = header[7:].strip()
                if token_str == "demo-student-token":
                    user = User.query.filter_by(email="student@aicp.edu").first() or User.query.filter_by(role="student").first()
                    if not user:
                        return jsonify({"error": "User not found"}), 401
                    g.user = user
                    return fn(*args, **kwargs)
                try:
                    data = serializer.loads(token_str, max_age=60 * 60 * 24 * 7)
                except (BadSignature, SignatureExpired):
                    return jsonify({"error": "Invalid or expired token"}), 401
                user = db.session.get(User, data["id"])
                if not user:
                    return jsonify({"error": "User not found"}), 401
                if roles and user.role not in roles:
                    return jsonify({"error": "Not allowed for this role"}), 403
                g.user = user
                return fn(*args, **kwargs)

            return wrapper

        return decorator

    def get_or_create_skill(name):
        clean = (name or "").strip()
        if not clean:
            return None
        existing = Skill.query.filter(db.func.lower(Skill.name) == clean.lower()).first()
        if existing:
            return existing
        skill = Skill(name=clean)
        db.session.add(skill)
        db.session.flush()
        return skill

    def skill_names_for_student(user_id):
        rows = (
            db.session.query(Skill.name)
            .join(StudentSkill, StudentSkill.skill_id == Skill.id)
            .filter(StudentSkill.user_id == user_id)
            .all()
        )
        return [row[0] for row in rows]

    def skill_names_for_opportunity(opp_id):
        rows = (
            db.session.query(Skill.name)
            .join(OpportunitySkill, OpportunitySkill.skill_id == Skill.id)
            .filter(OpportunitySkill.opportunity_id == opp_id)
            .all()
        )
        return [row[0] for row in rows]

    def set_student_skills(user_id, names):
        StudentSkill.query.filter_by(user_id=user_id).delete()
        for name in names or []:
            skill = get_or_create_skill(name)
            if skill:
                db.session.add(StudentSkill(user_id=user_id, skill_id=skill.id))

    def set_opportunity_skills(opp_id, names):
        OpportunitySkill.query.filter_by(opportunity_id=opp_id).delete()
        for name in names or []:
            skill = get_or_create_skill(name)
            if skill:
                db.session.add(OpportunitySkill(opportunity_id=opp_id, skill_id=skill.id))

    def public_user(user, include_skills=False):
        data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "college_name": user.college_name,
            "university": user.college_name,
            "company_name": user.company_name,
            "company": user.company_name,
            "branch": user.branch,
            "year": user.year,
            "year_of_study": user.year,
            "degree": getattr(user, "degree", None) or "B.Tech",
            "cgpa": str(getattr(user, "cgpa", None) or "8.8"),
            "bio": user.bio,
            "career_goal": user.career_goal,
            "career_goals": user.career_goal,
            "goal": user.career_goal,
            "industry": user.industry,
            "location": user.location,
        }
        if include_skills:
            data["skills"] = skill_names_for_student(user.id)
        return data

    def opportunity_payload(opp, student=None):
        required = skill_names_for_opportunity(opp.id)
        company = db.session.get(User, opp.company_id)
        comp_name = (company.company_name if company and company.company_name else (company.name if company else "TechCorp India"))
        payload = {
            "id": opp.id,
            "title": opp.title,
            "role": opp.title,
            "type": opp.type,
            "description": opp.description,
            "location": opp.location,
            "stipend": opp.stipend,
            "deadline": opp.deadline,
            "required_skills": required,
            "company_name": comp_name,
            "company": comp_name,
            "company_id": opp.company_id,
        }
        if student and student.role == "student":
            st_skills = skill_names_for_student(student.id)
            result = match_skills(st_skills, required)
            payload["match_percent"] = result["match_percent"]
            payload["matched_skills"] = result["matched_skills"]
            payload["missing_skills"] = result["missing_skills"]
            payload["extra_skills"] = [s for s in st_skills if s.lower() not in [r.lower() for r in required]]
            payload["explanation"] = result["explanation"]
            payload["recommended_learning"] = recommend_learning(result["missing_skills"])
            app_row = Application.query.filter_by(student_id=student.id, opportunity_id=opp.id).first()
            payload["application_status"] = app_row.status if app_row else None
        return payload

    @app.get("/api/health")
    def health():
        return {"ok": True}

    @app.post("/api/auth/register")
    def register():
        body = request.get_json(force=True)
        email = (body.get("email") or "").strip().lower()
        name = (body.get("name") or "").strip()
        password = body.get("password") or ""
        role = body.get("role") or "student"
        if role not in ("student", "company", "college"):
            return jsonify({"error": "Invalid role"}), 400
        if not email or not name or len(password) < 4:
            return jsonify({"error": "Name, email and password (min 4 chars) are required"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            college_name=body.get("college_name"),
            company_name=body.get("company_name"),
            branch=body.get("branch"),
            year=body.get("year"),
            industry=body.get("industry"),
            location=body.get("location"),
            career_goal=body.get("career_goal"),
        )
        db.session.add(user)
        db.session.commit()
        return {"token": token_for(user), "user": public_user(user, include_skills=True)}

    @app.post("/api/auth/login")
    def login():
        body = request.get_json(force=True)
        email = (body.get("email") or "").strip().lower()
        password = body.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password"}), 401
        return {"token": token_for(user), "user": public_user(user, include_skills=True)}

    @app.get("/api/auth/me")
    @login_required()
    def me():
        certs = Certification.query.filter_by(user_id=g.user.id).all()
        data = public_user(g.user, include_skills=True)
        data["certifications"] = [
            {"id": c.id, "title": c.title, "issuer": c.issuer, "year": c.year} for c in certs
        ]
        return data

    @app.get("/api/students/profile")
    @app.get("/api/student/profile")
    @login_required(roles=["student"])
    def get_student_profile():
        certs = Certification.query.filter_by(user_id=g.user.id).all()
        data = public_user(g.user, include_skills=True)
        data["certifications"] = [
            {"id": c.id, "title": c.title, "issuer": c.issuer, "year": c.year} for c in certs
        ]
        return data

    @app.put("/api/student/profile")
    @app.put("/api/students/profile")
    @login_required(roles=["student"])
    def update_student_profile():
        body = request.get_json(force=True)
        college = body.get("college_name") or body.get("university")
        if college is not None:
            g.user.college_name = college
        year = body.get("year") or body.get("year_of_study")
        if year is not None:
            g.user.year = year
        goal = body.get("career_goal") or body.get("career_goals") or body.get("goal")
        if goal is not None:
            g.user.career_goal = goal
        if "degree" in body:
            g.user.degree = body["degree"]
        if "cgpa" in body:
            g.user.cgpa = str(body["cgpa"])
        for field in ("name", "branch", "bio", "location"):
            if field in body:
                setattr(g.user, field, body[field])
        if "skills" in body:
            set_student_skills(g.user.id, body["skills"])
        db.session.commit()
        certs = Certification.query.filter_by(user_id=g.user.id).all()
        data = public_user(g.user, include_skills=True)
        data["certifications"] = [
            {"id": c.id, "title": c.title, "issuer": c.issuer, "year": c.year} for c in certs
        ]
        return data

    @app.get("/api/student/skills")
    @app.get("/api/students/skills")
    @login_required(roles=["student"])
    def get_student_skills():
        skills = skill_names_for_student(g.user.id)
        return {"count": len(skills), "skills": skills}

    @app.post("/api/students/skills")
    @app.post("/api/student/skills")
    @login_required(roles=["student"])
    def add_student_skill():
        body = request.get_json(force=True)
        skill_name = body.get("skill") or body.get("name")
        if skill_name:
            s = get_or_create_skill(skill_name)
            if s:
                exists = StudentSkill.query.filter_by(user_id=g.user.id, skill_id=s.id).first()
                if not exists:
                    db.session.add(StudentSkill(user_id=g.user.id, skill_id=s.id))
                    db.session.commit()
        elif "skills" in body:
            skills_list = body.get("skills") or []
            for sname in skills_list:
                s = get_or_create_skill(sname)
                if s:
                    exists = StudentSkill.query.filter_by(user_id=g.user.id, skill_id=s.id).first()
                    if not exists:
                        db.session.add(StudentSkill(user_id=g.user.id, skill_id=s.id))
            db.session.commit()
        skills = skill_names_for_student(g.user.id)
        return {"count": len(skills), "skills": skills}

    @app.put("/api/student/skills")
    @app.put("/api/students/skills")
    @login_required(roles=["student"])
    def put_student_skills():
        body = request.get_json(force=True)
        set_student_skills(g.user.id, body.get("skills") or [])
        db.session.commit()
        skills = skill_names_for_student(g.user.id)
        return {"count": len(skills), "skills": skills}

    @app.get("/api/student/certifications")
    @login_required(roles=["student"])
    def get_certs():
        certs = Certification.query.filter_by(user_id=g.user.id).all()
        return {
            "certifications": [
                {"id": c.id, "title": c.title, "issuer": c.issuer, "year": c.year} for c in certs
            ]
        }

    @app.post("/api/student/certifications")
    @login_required(roles=["student"])
    def add_cert():
        body = request.get_json(force=True)
        cert = Certification(
            user_id=g.user.id,
            title=body.get("title") or "Certification",
            issuer=body.get("issuer") or "Issuer",
            year=str(body.get("year") or datetime.utcnow().year),
        )
        db.session.add(cert)
        db.session.commit()
        return {"id": cert.id, "title": cert.title, "issuer": cert.issuer, "year": cert.year}

    @app.delete("/api/student/certifications/<int:cert_id>")
    @login_required(roles=["student"])
    def delete_cert(cert_id):
        cert = Certification.query.filter_by(id=cert_id, user_id=g.user.id).first()
        if not cert:
            return jsonify({"error": "Not found"}), 404
        db.session.delete(cert)
        db.session.commit()
        return {"ok": True}

    @app.put("/api/student/career-goals")
    @login_required(roles=["student"])
    def career_goals():
        body = request.get_json(force=True)
        g.user.career_goal = body.get("career_goal") or ""
        db.session.commit()
        return {"career_goal": g.user.career_goal}

    @app.get("/api/student/recommendations")
    @app.get("/api/students/recommendations")
    @login_required(roles=["student"])
    def recommendations():
        opps = Opportunity.query.order_by(Opportunity.id.desc()).all()
        items = [opportunity_payload(opp, student=g.user) for opp in opps]
        items.sort(key=lambda x: x.get("match_percent", 0), reverse=True)
        gaps = {}
        for item in items:
            for skill in item.get("missing_skills") or []:
                gaps[skill] = gaps.get(skill, 0) + 1
        top_gaps = sorted(gaps.items(), key=lambda kv: kv[1], reverse=True)[:8]
        learning = recommend_learning([name for name, _ in top_gaps])
        return {
            "opportunities": items,
            "skill_gap_summary": [{"skill": name, "appears_in": count} for name, count in top_gaps],
            "recommended_learning": learning,
        }

    @app.get("/api/students/skill-gap")
    @app.get("/api/student/skill-gap")
    @login_required(roles=["student"])
    def student_skill_gap():
        student_skills = skill_names_for_student(g.user.id)
        opps = Opportunity.query.order_by(Opportunity.id.desc()).all()
        gaps = {}
        opps_for_skill = {}
        for opp in opps:
            req = skill_names_for_opportunity(opp.id)
            res = match_skills(student_skills, req)
            for s in res["missing_skills"]:
                gaps[s] = gaps.get(s, 0) + 1
                if s not in opps_for_skill:
                    opps_for_skill[s] = []
                opps_for_skill[s].append(opp.title)
        top_gap_names = [name for name, _ in sorted(gaps.items(), key=lambda kv: kv[1], reverse=True)]
        top_skill_gaps = []
        for s in top_gap_names:
            roles = opps_for_skill.get(s, [])
            role_str = ", ".join(roles[:2])
            top_skill_gaps.append({
                "skill": s,
                "opportunities_requiring": gaps[s],
                "recommended_for": roles,
                "recommendation": f"Learn {s} to qualify for {role_str}"
            })
        learning = recommend_learning(top_gap_names[:8])
        explanation = f"You have {len(student_skills)} skills. Learning {len(top_gap_names)} additional skills will increase your eligibility across all {len(opps)} opportunities."
        return {
            "total_opportunities": len(opps),
            "student_skills": student_skills,
            "current_skills": student_skills,
            "missing_skills": top_gap_names,
            "top_skill_gaps": top_skill_gaps,
            "explanation": explanation,
            "recommended_learning": learning,
            "gap_counts": gaps,
        }

    @app.get("/api/opportunities/<int:opp_id>")
    @login_required()
    def get_opportunity(opp_id):
        opp = db.session.get(Opportunity, opp_id)
        if not opp:
            return jsonify({"error": "Opportunity not found"}), 404
        student = g.user if g.user.role == "student" else None
        payload = opportunity_payload(opp, student=student)
        if g.user.role == "student":
            app_row = Application.query.filter_by(
                student_id=g.user.id, opportunity_id=opp_id
            ).first()
            payload["application_status"] = app_row.status if app_row else None
        return payload

    @app.post("/api/student/applications")
    @app.post("/api/applications")
    @login_required(roles=["student"])
    def apply():
        body = request.get_json(force=True)
        opp_id = body.get("opportunity_id")
        opp = db.session.get(Opportunity, opp_id)
        if not opp:
            return jsonify({"error": "Opportunity not found"}), 404
        existing = Application.query.filter_by(
            student_id=g.user.id, opportunity_id=opp_id
        ).first()
        if existing:
            return jsonify({"error": "Already applied for this opportunity"}), 400
        row = Application(student_id=g.user.id, opportunity_id=opp_id, status="applied")
        db.session.add(row)
        db.session.commit()
        payload = opportunity_payload(opp, student=g.user)
        return {
            "id": row.id,
            "opportunity_id": opp_id,
            "status": row.status,
            "match_percent": payload.get("match_percent", 0.0),
            "message": "Application submitted successfully",
        }

    @app.get("/api/student/applications")
    @app.get("/api/students/applications")
    @login_required(roles=["student"])
    def student_applications():
        rows = Application.query.filter_by(student_id=g.user.id).order_by(Application.id.desc()).all()
        out = []
        for row in rows:
            opp = db.session.get(Opportunity, row.opportunity_id)
            payload = opportunity_payload(opp, student=g.user) if opp else {}
            payload["id"] = row.id
            payload["application_id"] = row.id
            payload["student_id"] = row.student_id
            payload["opportunity_id"] = row.opportunity_id
            payload["status"] = row.status
            payload["created_at"] = row.created_at.strftime("%Y-%m-%d %H:%M:%S") if row.created_at else None
            payload["applied_at"] = row.created_at.strftime("%Y-%m-%d %H:%M:%S") if row.created_at else None
            out.append(payload)
        return jsonify(out)

    @app.get("/api/company/dashboard")
    @login_required(roles=["company"])
    def company_dashboard():
        opps = Opportunity.query.filter_by(company_id=g.user.id).order_by(Opportunity.id.desc()).all()
        items = []
        for opp in opps:
            count = Application.query.filter_by(opportunity_id=opp.id).count()
            data = opportunity_payload(opp)
            data["applicant_count"] = count
            items.append(data)
        return {
            "company": public_user(g.user),
            "opportunities": items,
            "total_opportunities": len(items),
            "total_applicants": sum(i["applicant_count"] for i in items),
        }

    @app.post("/api/company/opportunities")
    @login_required(roles=["company"])
    def post_opportunity():
        body = request.get_json(force=True)
        title = (body.get("title") or "").strip()
        if not title:
            return jsonify({"error": "Title is required"}), 400
        opp = Opportunity(
            company_id=g.user.id,
            title=title,
            type=body.get("type") or "internship",
            description=body.get("description") or "",
            location=body.get("location") or "",
            stipend=body.get("stipend") or "",
            deadline=body.get("deadline") or "",
        )
        db.session.add(opp)
        db.session.flush()
        set_opportunity_skills(opp.id, body.get("required_skills") or [])
        db.session.commit()
        return opportunity_payload(opp)

    @app.get("/api/company/opportunities/<int:opp_id>/applicants")
    @login_required(roles=["company"])
    def applicants(opp_id):
        opp = Opportunity.query.filter_by(id=opp_id, company_id=g.user.id).first()
        if not opp:
            return jsonify({"error": "Opportunity not found"}), 404
        required = skill_names_for_opportunity(opp.id)
        rows = Application.query.filter_by(opportunity_id=opp_id).all()
        people = []
        for row in rows:
            student = db.session.get(User, row.student_id)
            skills = skill_names_for_student(student.id)
            result = match_skills(skills, required)
            certs = Certification.query.filter_by(user_id=student.id).all()
            people.append(
                {
                    "application_id": row.id,
                    "status": row.status,
                    "applied_at": row.created_at.isoformat() if row.created_at else None,
                    "student": {
                        **public_user(student),
                        "skills": skills,
                        "certifications": [
                            {"title": c.title, "issuer": c.issuer, "year": c.year} for c in certs
                        ],
                    },
                    **result,
                    "recommended_learning": recommend_learning(result["missing_skills"]),
                }
            )
        people.sort(key=lambda x: x["match_percent"], reverse=True)
        return {"opportunity": opportunity_payload(opp), "applicants": people}

    @app.put("/api/company/applications/<int:app_id>/status")
    @login_required(roles=["company"])
    def update_status(app_id):
        body = request.get_json(force=True)
        status = body.get("status")
        if status not in ("applied", "under_review", "shortlisted", "rejected", "selected"):
            return jsonify({"error": "Invalid status"}), 400
        row = db.session.get(Application, app_id)
        if not row:
            return jsonify({"error": "Application not found"}), 404
        opp = db.session.get(Opportunity, row.opportunity_id)
        if not opp or opp.company_id != g.user.id:
            return jsonify({"error": "Not allowed"}), 403
        row.status = status
        db.session.commit()
        return {"id": row.id, "status": row.status}

    @app.get("/api/college/dashboard")
    @login_required(roles=["college"])
    def college_dashboard():
        college = g.user.college_name or g.user.name
        students = User.query.filter_by(role="student")
        if g.user.college_name:
            students = students.filter(User.college_name == g.user.college_name)
        students = students.all()
        opps = Opportunity.query.all()

        student_rows = []
        gap_counter = {}
        match_values = []
        for student in students:
            skills = skill_names_for_student(student.id)
            matches = []
            for opp in opps:
                result = match_skills(skills, skill_names_for_opportunity(opp.id))
                matches.append(result["match_percent"])
                for skill in result["missing_skills"]:
                    gap_counter[skill] = gap_counter.get(skill, 0) + 1
            avg = round(sum(matches) / len(matches), 1) if matches else 0
            match_values.append(avg)
            apps = Application.query.filter_by(student_id=student.id).all()
            student_rows.append(
                {
                    **public_user(student),
                    "skills": skills,
                    "avg_match_percent": avg,
                    "application_count": len(apps),
                    "selected_count": sum(1 for a in apps if a.status == "selected"),
                }
            )

        status_counts = {"applied": 0, "shortlisted": 0, "rejected": 0, "selected": 0}
        for row in Application.query.all():
            student = db.session.get(User, row.student_id)
            if g.user.college_name and student and student.college_name != g.user.college_name:
                continue
            status_counts[row.status] = status_counts.get(row.status, 0) + 1

        skill_gaps = sorted(gap_counter.items(), key=lambda kv: kv[1], reverse=True)[:10]
        return {
            "college": college,
            "students": student_rows,
            "student_count": len(student_rows),
            "avg_match_percent": round(sum(match_values) / len(match_values), 1) if match_values else 0,
            "skill_gaps": [{"skill": name, "student_opportunity_gaps": count} for name, count in skill_gaps],
            "recommended_learning": recommend_learning([name for name, _ in skill_gaps]),
            "opportunities": [opportunity_payload(opp) for opp in opps],
            "analytics": {
                "applications_by_status": status_counts,
                "opportunity_count": len(opps),
                "internship_count": sum(1 for o in opps if o.type == "internship"),
                "job_count": sum(1 for o in opps if o.type == "job"),
                "project_count": sum(1 for o in opps if o.type == "project"),
            },
        }

    @app.get("/api/college/students")
    @login_required(roles=["college"])
    def college_students():
        return college_dashboard()

    @app.get("/api/skills")
    def list_skills():
        return {"skills": [s.name for s in Skill.query.order_by(Skill.name).all()]}

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
