"""Load demo users, skills, opportunities and applications."""

from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app import (
    Application,
    Certification,
    Opportunity,
    OpportunitySkill,
    Skill,
    StudentSkill,
    User,
    create_app,
    db,
)


def skill(name):
    row = Skill.query.filter(db.func.lower(Skill.name) == name.lower()).first()
    if row:
        return row
    row = Skill(name=name)
    db.session.add(row)
    db.session.flush()
    return row


def add_skills(user_id, names):
    for name in names:
        s = skill(name)
        exists = StudentSkill.query.filter_by(user_id=user_id, skill_id=s.id).first()
        if not exists:
            db.session.add(StudentSkill(user_id=user_id, skill_id=s.id))


def add_opp_skills(opp_id, names):
    for name in names:
        s = skill(name)
        exists = OpportunitySkill.query.filter_by(opportunity_id=opp_id, skill_id=s.id).first()
        if not exists:
            db.session.add(OpportunitySkill(opportunity_id=opp_id, skill_id=s.id))


def user(**kwargs):
    existing = User.query.filter_by(email=kwargs["email"]).first()
    if existing:
        return existing
    kwargs["password_hash"] = generate_password_hash(kwargs.pop("password"))
    row = User(**kwargs)
    db.session.add(row)
    db.session.flush()
    return row


def seed():
    flask_app = create_app()
    with flask_app.app_context():
        db.create_all()

        college = user(
            name="College Admin",
            email="college@demo.com",
            password="college123",
            role="college",
            college_name="National Institute of Technology Demo",
            location="Hyderabad",
        )

        acme = user(
            name="Priya Sharma",
            email="company@demo.com",
            password="company123",
            role="company",
            company_name="Acme Analytics",
            industry="Software / Analytics",
            location="Bengaluru",
        )
        nimbus = user(
            name="Rahul Mehta",
            email="nimbus@demo.com",
            password="company123",
            role="company",
            company_name="Nimbus Cloud",
            industry="Cloud",
            location="Pune",
        )
        pixel = user(
            name="Anita Rao",
            email="pixel@demo.com",
            password="company123",
            role="company",
            company_name="Pixel Labs",
            industry="Product Design",
            location="Hyderabad",
        )

        student = user(
            name="Teja Varma",
            email="student@demo.com",
            password="student123",
            role="student",
            college_name=college.college_name,
            branch="CSE",
            year="3rd Year",
            career_goal="Full-stack intern then SDE",
            bio="CSE student focused on web apps and data projects.",
            location="Hyderabad",
        )
        aisha = user(
            name="Aisha Khan",
            email="aisha@demo.com",
            password="student123",
            role="student",
            college_name=college.college_name,
            branch="CSE",
            year="4th Year",
            career_goal="ML intern",
            bio="Interested in applied machine learning.",
            location="Hyderabad",
        )
        ravi = user(
            name="Ravi Patel",
            email="ravi@demo.com",
            password="student123",
            role="student",
            college_name=college.college_name,
            branch="IT",
            year="3rd Year",
            career_goal="Frontend intern",
            bio="UI-focused developer.",
            location="Hyderabad",
        )
        meera = user(
            name="Meera Iyer",
            email="meera@demo.com",
            password="student123",
            role="student",
            college_name=college.college_name,
            branch="ECE",
            year="2nd Year",
            career_goal="Data analyst intern",
            bio="Learning SQL and Excel for analytics.",
            location="Hyderabad",
        )

        add_skills(student.id, ["Python", "JavaScript", "React", "SQL", "Git"])
        add_skills(aisha.id, ["Python", "Machine Learning", "SQL", "Data Analysis"])
        add_skills(ravi.id, ["JavaScript", "React", "UI/UX", "Git"])
        add_skills(meera.id, ["Excel", "SQL", "Communication"])

        if not Certification.query.filter_by(user_id=student.id).first():
            db.session.add(
                Certification(
                    user_id=student.id,
                    title="Responsive Web Design",
                    issuer="freeCodeCamp",
                    year="2025",
                )
            )
            db.session.add(
                Certification(
                    user_id=aisha.id,
                    title="Intro to Machine Learning",
                    issuer="Kaggle",
                    year="2025",
                )
            )

        if Opportunity.query.count() == 0:
            intern = Opportunity(
                company_id=acme.id,
                title="Data Analyst Intern",
                type="internship",
                description="Work with SQL, Python and dashboards for client reports.",
                location="Bengaluru / Hybrid",
                stipend="₹15,000 / month",
                deadline=(datetime.utcnow() + timedelta(days=21)).strftime("%Y-%m-%d"),
            )
            sde = Opportunity(
                company_id=acme.id,
                title="Junior Full-Stack Intern",
                type="internship",
                description="Build React + Flask features for internal tools.",
                location="Bengaluru",
                stipend="₹20,000 / month",
                deadline=(datetime.utcnow() + timedelta(days=14)).strftime("%Y-%m-%d"),
            )
            ml = Opportunity(
                company_id=nimbus.id,
                title="ML Project Collaborator",
                type="project",
                description="Prototype a recommendation module with explainable outputs.",
                location="Remote",
                stipend="Certificate + PPO track",
                deadline=(datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
            )
            cloud = Opportunity(
                company_id=nimbus.id,
                title="Cloud Support Intern",
                type="internship",
                description="Assist customers with AWS basics and documentation.",
                location="Pune",
                stipend="₹12,000 / month",
                deadline=(datetime.utcnow() + timedelta(days=18)).strftime("%Y-%m-%d"),
            )
            design = Opportunity(
                company_id=pixel.id,
                title="UI/UX Intern",
                type="internship",
                description="Wireframes and UI kits for education products.",
                location="Hyderabad",
                stipend="₹10,000 / month",
                deadline=(datetime.utcnow() + timedelta(days=10)).strftime("%Y-%m-%d"),
            )
            job = Opportunity(
                company_id=acme.id,
                title="Graduate SDE",
                type="job",
                description="Entry-level software engineer. JavaScript, React, Python, Git.",
                location="Bengaluru",
                stipend="₹6–8 LPA",
                deadline=(datetime.utcnow() + timedelta(days=45)).strftime("%Y-%m-%d"),
            )
            db.session.add_all([intern, sde, ml, cloud, design, job])
            db.session.flush()
            add_opp_skills(intern.id, ["Python", "SQL", "Excel", "Data Analysis"])
            add_opp_skills(sde.id, ["JavaScript", "React", "Python", "Flask", "Git"])
            add_opp_skills(ml.id, ["Python", "Machine Learning", "Data Analysis"])
            add_opp_skills(cloud.id, ["AWS", "Python", "Communication"])
            add_opp_skills(design.id, ["UI/UX", "JavaScript", "Communication"])
            add_opp_skills(job.id, ["JavaScript", "React", "Python", "Git", "SQL"])

            db.session.add_all(
                [
                    Application(student_id=student.id, opportunity_id=sde.id, status="shortlisted"),
                    Application(student_id=aisha.id, opportunity_id=ml.id, status="applied"),
                    Application(student_id=ravi.id, opportunity_id=design.id, status="applied"),
                    Application(student_id=meera.id, opportunity_id=intern.id, status="applied"),
                ]
            )

        db.session.commit()
        print("Seed complete.")
        print("Students: student@demo.com / student123")
        print("Company:  company@demo.com / company123")
        print("College:  college@demo.com / college123")


if __name__ == "__main__":
    seed()
