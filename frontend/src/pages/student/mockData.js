import { useCallback, useState } from "react";

const STORAGE_KEY = "skillbridge_student_v1";

export const LEARNING_CATALOG = {
  flask: {
    title: "Flask web APIs",
    provider: "Flask documentation",
    hours: 10,
    link: "https://flask.palletsprojects.com/",
  },
  aws: {
    title: "AWS Cloud Practitioner essentials",
    provider: "AWS Skill Builder",
    hours: 12,
    link: "https://skillbuilder.aws/",
  },
  excel: {
    title: "Excel for analysts",
    provider: "Microsoft Learn",
    hours: 6,
    link: "https://learn.microsoft.com/excel/",
  },
  "machine learning": {
    title: "Intro to machine learning",
    provider: "Kaggle",
    hours: 16,
    link: "https://www.kaggle.com/learn/intro-to-machine-learning",
  },
  "data analysis": {
    title: "Pandas data analysis",
    provider: "Kaggle",
    hours: 8,
    link: "https://www.kaggle.com/learn/pandas",
  },
  "ui/ux": {
    title: "UI design foundations",
    provider: "Figma Learn",
    hours: 8,
    link: "https://www.figma.com/resource-library/",
  },
  communication: {
    title: "Workplace communication",
    provider: "NPTEL / Coursera audit",
    hours: 6,
    link: "https://www.coursera.org/",
  },
};

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export function normalizeSkill(name) {
  return (name || "").trim().toLowerCase();
}

export function matchSkills(studentSkillNames, requiredSkills) {
  const student = new Set((studentSkillNames || []).map(normalizeSkill).filter(Boolean));
  const required = [...new Set((requiredSkills || []).map(normalizeSkill).filter(Boolean))];

  if (!required.length) {
    return {
      matchPercent: 100,
      matched: [],
      missing: [],
      explanation: "This opportunity lists no required skills, so match is 100%.",
    };
  }

  const matched = required.filter((skill) => student.has(skill));
  const missing = required.filter((skill) => !student.has(skill));
  const matchPercent = Math.round((matched.length / required.length) * 1000) / 10;
  const parts = [`Matched ${matched.length} of ${required.length} required skills (${matchPercent}%).`];
  parts.push(matched.length ? `Matched: ${matched.join(", ")}.` : "No overlapping skills yet.");
  parts.push(missing.length ? `Skill gaps: ${missing.join(", ")}.` : "No skill gaps.");

  return { matchPercent, matched, missing, explanation: parts.join(" ") };
}

export function recommendLearning(missingSkills) {
  return (missingSkills || []).map((skill) => {
    const key = normalizeSkill(skill);
    const course = LEARNING_CATALOG[key];
    if (course) return { skill: key, ...course };
    return {
      skill: key,
      title: `Learn ${skill}`,
      provider: "NPTEL / YouTube search",
      hours: 8,
      link: `https://www.google.com/search?q=${encodeURIComponent(skill + " nptel course")}`,
    };
  });
}

const INITIAL = {
  profile: {
    name: "Teja Varma",
    email: "student@demo.com",
    university: "National Institute of Technology Demo",
    college: "National Institute of Technology Demo",
    degree: "B.Tech",
    branch: "Computer Science and Engineering",
    year: "3rd Year",
    cgpa: "8.6",
    location: "Hyderabad",
    phone: "+91 90000 12345",
    careerGoal: "Full-stack intern this semester, then a graduate SDE role.",
    bio: "CSE student building web products. Comfortable with React and Python; currently closing backend and cloud gaps.",
  },
  skills: [
    { name: "Python", level: 4 },
    { name: "JavaScript", level: 4 },
    { name: "React", level: 4 },
    { name: "SQL", level: 3 },
    { name: "Git", level: 4 },
  ],
  certifications: [
    { id: 1, title: "Responsive Web Design", issuer: "freeCodeCamp", year: "2025" },
    { id: 2, title: "SQL Basics", issuer: "HackerRank", year: "2025" },
  ],
  opportunities: [
    {
      id: 1,
      title: "Junior Full-Stack Intern",
      company: "Acme Analytics",
      type: "internship",
      location: "Bengaluru",
      stipend: "₹20,000 / month",
      deadline: "2026-10-02",
      description: "Build React + Flask features for internal analytics tools used by client teams.",
      requiredSkills: ["JavaScript", "React", "Python", "Flask", "Git"],
      matchPercent: 80,
      matchedSkills: ["javascript", "react", "python", "git"],
      missingSkills: ["flask"],
      explanation: "Matched 4 of 5 required skills (80%).",
    },
    {
      id: 2,
      title: "Graduate SDE",
      company: "Acme Analytics",
      type: "job",
      location: "Bengaluru",
      stipend: "₹6–8 LPA",
      deadline: "2026-11-02",
      description: "Entry-level software engineer working across the web stack and data APIs.",
      requiredSkills: ["JavaScript", "React", "Python", "Git", "SQL"],
      matchPercent: 100,
      matchedSkills: ["javascript", "react", "python", "git", "sql"],
      missingSkills: [],
      explanation: "Matched 5 of 5 required skills (100%).",
    },
    {
      id: 3,
      title: "Data Analyst Intern",
      company: "Acme Analytics",
      type: "internship",
      location: "Bengaluru / Hybrid",
      stipend: "₹15,000 / month",
      deadline: "2026-10-09",
      description: "Write SQL, shape Python notebooks, and publish weekly client dashboards.",
      requiredSkills: ["Python", "SQL", "Excel", "Data Analysis"],
      matchPercent: 50,
      matchedSkills: ["python", "sql"],
      missingSkills: ["excel", "data analysis"],
      explanation: "Matched 2 of 4 required skills (50%).",
    },
    {
      id: 4,
      title: "ML Project Collaborator",
      company: "Nimbus Cloud",
      type: "project",
      location: "Remote",
      stipend: "Certificate + PPO track",
      deadline: "2026-10-18",
      description: "Prototype an explainable recommendation module with clear skill-overlap scoring.",
      requiredSkills: ["Python", "Machine Learning", "Data Analysis"],
      matchPercent: 33.3,
      matchedSkills: ["python"],
      missingSkills: ["machine learning", "data analysis"],
      explanation: "Matched 1 of 3 required skills (33.3%).",
    },
    {
      id: 5,
      title: "Cloud Support Intern",
      company: "Nimbus Cloud",
      type: "internship",
      location: "Pune",
      stipend: "₹12,000 / month",
      deadline: "2026-10-06",
      description: "Help customers with AWS basics, runbooks, and incident notes.",
      requiredSkills: ["AWS", "Python", "Communication"],
      matchPercent: 33.3,
      matchedSkills: ["python"],
      missingSkills: ["aws", "communication"],
      explanation: "Matched 1 of 3 required skills (33.3%).",
    },
    {
      id: 6,
      title: "UI/UX Intern",
      company: "Pixel Labs",
      type: "internship",
      location: "Hyderabad",
      stipend: "₹10,000 / month",
      deadline: "2026-09-28",
      description: "Wireframes and UI kits for education products used by colleges.",
      requiredSkills: ["UI/UX", "JavaScript", "Communication"],
      matchPercent: 33.3,
      matchedSkills: ["javascript"],
      missingSkills: ["ui/ux", "communication"],
      explanation: "Matched 1 of 3 required skills (33.3%).",
    },
  ],
  applications: [
    {
      id: 101,
      opportunityId: 1,
      status: "shortlisted",
      appliedAt: "2026-09-10",
    },
    {
      id: 102,
      opportunityId: 4,
      status: "under_review",
      appliedAt: "2026-09-12",
    },
    {
      id: 103,
      opportunityId: 2,
      status: "applied",
      appliedAt: "2026-09-15",
    },
  ],
};

export function skillNames(data) {
  return (data.skills || []).map((s) => s.name);
}

export function withMatches(data) {
  const names = skillNames(data);
  return (data.opportunities || []).map((opp) => ({
    ...opp,
    ...matchSkills(names, opp.requiredSkills),
  }));
}

export function loadStudent() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        ...clone(INITIAL),
        ...parsed,
        profile: { ...INITIAL.profile, ...(parsed.profile || {}) },
        skills: parsed.skills || INITIAL.skills,
        certifications: parsed.certifications || INITIAL.certifications,
        applications: parsed.applications || INITIAL.applications,
        opportunities: INITIAL.opportunities,
      };
    }
  } catch {
    /* keep defaults */
  }
  return clone(INITIAL);
}

export function saveStudent(data) {
  const persist = {
    profile: data.profile,
    skills: data.skills,
    certifications: data.certifications,
    applications: data.applications,
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(persist));
}

export function useStudentStore() {
  const [data, setData] = useState(loadStudent);

  const update = useCallback((patch) => {
    setData((current) => {
      const next = typeof patch === "function" ? patch(current) : { ...current, ...patch };
      saveStudent(next);
      return next;
    });
  }, []);

  return [data, update];
}
