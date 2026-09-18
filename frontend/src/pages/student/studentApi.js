import { api } from "../../api";
import { loadStudent, saveStudent, withMatches } from "./mockData";

function delay(value) {
  return new Promise((resolve) => setTimeout(() => resolve(value), 120));
}

function readStore() {
  const data = loadStudent();
  return {
    profile: {
      name: data.profile.name || "",
      email: data.profile.email || "",
      university: data.profile.university || data.profile.college || "",
      degree: data.profile.degree || "",
      branch: data.profile.branch || "",
      year: data.profile.year || "",
      cgpa: data.profile.cgpa || "",
      location: data.profile.location || "",
      bio: data.profile.bio || "",
      careerGoal: data.profile.careerGoal || "",
    },
    certifications: data.certifications || [],
  };
}

function writeProfile(profile) {
  const data = loadStudent();
  data.profile = {
    ...data.profile,
    ...profile,
    college: profile.university,
  };
  saveStudent(data);
  return readStore();
}

export async function getStudentProfile() {
  try {
    const data = await api("/api/students/profile");
    return {
      profile: {
        name: data.name || "",
        email: data.email || "",
        university: data.college_name || data.university || "",
        degree: data.degree || "B.Tech",
        branch: data.branch || "",
        year: data.year_of_study || data.year || "",
        cgpa: String(data.cgpa || ""),
        location: data.location || "",
        bio: data.bio || "",
        careerGoal: data.career_goals || data.career_goal || data.goal || "",
      },
      certifications: (data.certifications || []).map((c, idx) =>
        typeof c === "string"
          ? { id: idx + 1, title: c, issuer: "Certified", year: "2026" }
          : { id: c.id ?? idx + 1, title: c.title || "", issuer: c.issuer || "Issuer", year: String(c.year || "2026") }
      ),
    };
  } catch (err) {
    console.warn("GET /api/students/profile unavailable, using mock data:", err.message);
    return delay(readStore());
  }
}

export async function saveStudentProfile(profile) {
  try {
    const saved = await api("/api/students/profile", {
      method: "PUT",
      body: JSON.stringify({
        name: profile.name,
        college_name: profile.university,
        university: profile.university,
        degree: profile.degree,
        branch: profile.branch,
        year: profile.year,
        year_of_study: profile.year,
        cgpa: profile.cgpa,
        bio: profile.bio,
        location: profile.location,
        career_goals: profile.careerGoal,
        career_goal: profile.careerGoal,
        goal: profile.careerGoal,
      }),
    });
    return getStudentProfile().then((current) => ({
      ...current,
      profile: { ...current.profile, name: saved.name || current.profile.name },
    }));
  } catch (err) {
    console.warn("PUT /api/students/profile unavailable, saving to local store:", err.message);
    return delay(writeProfile(profile));
  }
}

export async function addStudentCertification(cert) {
  try {
    await api("/api/student/certifications", {
      method: "POST",
      body: JSON.stringify(cert),
    });
    return getStudentProfile();
  } catch (err) {
    console.warn("POST /api/student/certifications unavailable, saving to mock data:", err.message);
    const data = loadStudent();
    data.certifications = [
      ...data.certifications,
      {
        id: Date.now(),
        title: cert.title.trim(),
        issuer: cert.issuer.trim() || "Issuer",
        year: cert.year.trim() || String(new Date().getFullYear()),
      },
    ];
    saveStudent(data);
    return delay(readStore());
  }
}

export async function removeStudentCertification(id) {
  try {
    await api(`/api/student/certifications/${id}`, { method: "DELETE" });
    return getStudentProfile();
  } catch (err) {
    console.warn("DELETE /api/student/certifications unavailable, updating mock data:", err.message);
    const data = loadStudent();
    data.certifications = data.certifications.filter((item) => item.id !== id);
    saveStudent(data);
    return delay(readStore());
  }
}

function readSkills() {
  const data = loadStudent();
  return (data.skills || []).map((skill) =>
    typeof skill === "string" ? { name: skill, level: 3 } : skill
  );
}

export async function getStudentSkills() {
  try {
    const data = await api("/api/students/skills");
    const list = Array.isArray(data) ? data : (data.skills || []);
    return list.map((item) => {
      const name = typeof item === "string" ? item : item.name;
      return { name, level: 3 };
    });
  } catch (err) {
    console.warn("GET /api/students/skills unavailable, using mock data:", err.message);
    return delay(readSkills());
  }
}

export async function addStudentSkill(name) {
  const clean = (name || "").trim();
  if (!clean) throw new Error("Enter a skill name");
  try {
    const data = await api("/api/students/skills", {
      method: "POST",
      body: JSON.stringify({ skill: clean }),
    });
    const list = Array.isArray(data) ? data : (data.skills || []);
    return list.map((item) => {
      const sname = typeof item === "string" ? item : item.name;
      return { name: sname, level: 3 };
    });
  } catch (err) {
    console.warn("POST /api/students/skills unavailable, adding to mock data:", err.message);
    const data = loadStudent();
    const skills = readSkills();
    if (skills.some((skill) => skill.name.toLowerCase() === clean.toLowerCase())) {
      return delay(skills);
    }
    data.skills = [...skills, { name: clean, level: 3 }];
    saveStudent(data);
    return delay(readSkills());
  }
}

export async function removeStudentSkill(name) {
  try {
    const current = await getStudentSkills();
    const names = current.map((s) => s.name).filter((skill) => skill.toLowerCase() !== name.toLowerCase());
    const data = await api("/api/students/skills", {
      method: "PUT",
      body: JSON.stringify({ skills: names }),
    });
    const list = Array.isArray(data) ? data : (data.skills || []);
    return list.map((item) => {
      const sname = typeof item === "string" ? item : item.name;
      return { name: sname, level: 3 };
    });
  } catch (err) {
    console.warn("PUT /api/students/skills unavailable, removing from mock data:", err.message);
    const data = loadStudent();
    data.skills = readSkills().filter((skill) => skill.name.toLowerCase() !== name.toLowerCase());
    saveStudent(data);
    return delay(readSkills());
  }
}

function mapOpportunity(raw, applications = []) {
  const status =
    raw.application_status ||
    raw.applicationStatus ||
    raw.status ||
    applications.find((row) => row.opportunityId === raw.id || row.opportunity_id === raw.id)?.status ||
    null;
  return {
    id: raw.id,
    title: raw.title || raw.role || "",
    company: raw.company || raw.company_name || "",
    type: raw.type || "internship",
    location: raw.location || "—",
    description: raw.description || "",
    stipend: raw.stipend || "—",
    deadline: raw.deadline || "—",
    requiredSkills: raw.required_skills || raw.requiredSkills || [],
    matchPercent: typeof raw.match_percent === "number" ? Math.round(raw.match_percent) : (raw.matchPercent ?? 0),
    matchedSkills: raw.matched_skills || raw.matchedSkills || [],
    missingSkills: raw.missing_skills || raw.missingSkills || [],
    extraSkills: raw.extra_skills || raw.extraSkills || [],
    recommendedLearning: raw.recommended_learning || raw.recommendedLearning || [],
    explanation: raw.explanation || "",
    applicationStatus: status,
  };
}

function mockOpportunities() {
  const data = loadStudent();
  return (data.opportunities || []).map((opp) =>
    mapOpportunity(
      {
        ...opp,
        match_percent: opp.match_percent ?? opp.matchPercent,
        matched_skills: opp.matched_skills || opp.matchedSkills,
        missing_skills: opp.missing_skills || opp.missingSkills,
        required_skills: opp.requiredSkills,
        company_name: opp.company,
      },
      data.applications || []
    )
  );
}

export async function getStudentOpportunities() {
  try {
    const data = await api("/api/students/recommendations");
    const list = Array.isArray(data) ? data : (data.opportunities || []);
    return list.map((opp) => mapOpportunity(opp));
  } catch (err) {
    console.warn("GET /api/students/recommendations unavailable, using mock data:", err.message);
    return delay(mockOpportunities());
  }
}

export async function getStudentOpportunity(id) {
  try {
    const opp = await api(`/api/opportunities/${id}`);
    return mapOpportunity(opp);
  } catch (err) {
    console.warn(`GET /api/opportunities/${id} unavailable, looking up mock data:`, err.message);
    const found = mockOpportunities().find((opp) => String(opp.id) === String(id));
    if (!found) throw new Error("Opportunity not found");
    return delay(found);
  }
}

export async function applyToOpportunity(opportunityId) {
  try {
    await api("/api/applications", {
      method: "POST",
      body: JSON.stringify({ opportunity_id: opportunityId }),
    });
    return getStudentOpportunities();
  } catch (err) {
    // Rethrow to let the UI display backend error (e.g. Already applied for this opportunity)
    throw err;
  }
}

function readMockApplications() {
  const data = loadStudent();
  const opps = mockOpportunities();
  return (data.applications || []).map((app) => {
    const opp = opps.find((item) => item.id === app.opportunityId);
    return {
      id: app.id,
      opportunityId: app.opportunityId,
      opportunityTitle: opp?.title || `Opportunity #${app.opportunityId}`,
      companyName: opp?.company || "Company",
      type: opp?.type || "internship",
      location: opp?.location || "—",
      stipend: opp?.stipend || "—",
      deadline: opp?.deadline || "—",
      matchPercent: opp?.matchPercent ?? 0,
      status: app.status || "applied",
      appliedAt: app.appliedAt || new Date().toISOString().slice(0, 10),
    };
  });
}

export async function getStudentApplications() {
  try {
    const data = await api("/api/students/applications");
    const list = Array.isArray(data) ? data : (data.applications || []);
    return list.map((app) => ({
      id: app.application_id || app.id,
      opportunityId: app.opportunity_id || app.id,
      opportunityTitle: app.title || app.role || `Opportunity #${app.opportunity_id || app.id}`,
      companyName: app.company_name || app.company || "Company",
      type: app.type || "internship",
      location: app.location || "—",
      stipend: app.stipend || "—",
      deadline: app.deadline || "—",
      matchPercent: typeof app.match_percent === "number" ? Math.round(app.match_percent) : (app.matchPercent ?? 0),
      status: app.status || "applied",
      appliedAt: (app.created_at || app.applied_at || new Date().toISOString()).slice(0, 10),
    }));
  } catch (err) {
    console.warn("GET /api/students/applications unavailable, using local mock data:", err.message);
    return delay(readMockApplications());
  }
}

const MOCK_GAP_COURSES = [
  {
    skill: "Docker",
    title: "Docker Fundamentals",
    provider: "Docker Docs",
    hours: 8,
    link: "https://docs.docker.com/get-started/",
  },
  {
    skill: "AWS",
    title: "AWS Basics",
    provider: "AWS Skill Builder",
    hours: 12,
    link: "https://skillbuilder.aws/",
  },
  {
    skill: "Statistics",
    title: "Statistics for Data Science",
    provider: "Khan Academy",
    hours: 10,
    link: "https://www.khanacademy.org/math/statistics-probability",
  },
];

export async function getStudentSkillGap() {
  try {
    const data = await api("/api/students/skill-gap");
    const currentSkills = data.student_skills || data.current_skills || [];
    const missingSkills = data.missing_skills || [];
    let recommendedCourses = data.recommended_learning || [];
    if ((!recommendedCourses || recommendedCourses.length === 0) && data.top_skill_gaps) {
      recommendedCourses = data.top_skill_gaps.map((gap) => ({
        skill: gap.skill,
        title: gap.recommendation || `Learn ${gap.skill}`,
        provider: "SkillBridge Path",
        hours: 10,
        link: `https://www.google.com/search?q=${encodeURIComponent("learn " + gap.skill)}`,
      }));
    }
    return {
      totalOpportunities: data.total_opportunities || 0,
      currentSkills,
      missingSkills,
      topSkillGaps: data.top_skill_gaps || [],
      explanation: data.explanation || "",
      recommendedCourses,
    };
  } catch (err) {
    console.warn("GET /api/students/skill-gap unavailable, using mock data:", err.message);
    return delay({
      totalOpportunities: 4,
      currentSkills: readSkills().map((skill) => skill.name),
      missingSkills: MOCK_GAP_COURSES.map((course) => course.skill),
      topSkillGaps: [],
      explanation: "Skill gap analysis based on current opportunities.",
      recommendedCourses: MOCK_GAP_COURSES,
    });
  }
}

export async function getStudentDashboardData() {
  const [profileData, skillsData, oppsData, gapData, appsData] = await Promise.all([
    getStudentProfile(),
    getStudentSkills(),
    getStudentOpportunities(),
    getStudentSkillGap(),
    getStudentApplications(),
  ]);

  const profile = profileData.profile || {};
  const certifications = profileData.certifications || [];
  const skills = skillsData || [];
  const opportunities = oppsData || [];
  const applications = appsData || [];

  const checks = [
    profile.name,
    profile.email,
    profile.university,
    profile.branch,
    profile.year,
    profile.location,
    profile.careerGoal,
    profile.bio,
    skills.length >= 1,
    skills.length >= 3,
    certifications.length >= 1,
  ];
  const completion = Math.round((checks.filter(Boolean).length / checks.length) * 100);

  const ranked = [...opportunities].sort((a, b) => (b.matchPercent ?? 0) - (a.matchPercent ?? 0));
  const topMatch = ranked[0]?.matchPercent ?? 0;
  const recommended = ranked.slice(0, 3);

  const appCounts = {
    total: applications.length,
    applied: applications.filter((a) => a.status === "applied").length,
    under_review: applications.filter((a) => a.status === "under_review" || a.status === "review").length,
    shortlisted: applications.filter((a) => a.status === "shortlisted").length,
    selected: applications.filter((a) => a.status === "selected").length,
    rejected: applications.filter((a) => a.status === "rejected").length,
  };

  let topGaps = [];
  if (gapData.topSkillGaps && gapData.topSkillGaps.length > 0) {
    topGaps = gapData.topSkillGaps.slice(0, 4).map((g) => [g.skill, g.opportunities_requiring || 1]);
  } else if (gapData.missingSkills && gapData.missingSkills.length > 0) {
    topGaps = gapData.missingSkills.slice(0, 4).map((s) => [s, 1]);
  }

  return {
    profile,
    certifications,
    skills,
    completion,
    topMatch,
    recommended,
    appCounts,
    topGaps,
    applications,
  };
}

