import { api } from "../api";

export const collegeApi = {
  students: (params = {}) => {
    const cleanParams = Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
    );
    const qs = new URLSearchParams(cleanParams).toString();
    return api(`/api/college/students${qs ? `?${qs}` : ""}`);
  },
  analytics: () => api("/api/college/analytics"),
  skillGaps: () => api("/api/college/skill-gaps"),
};

export const studentApi = {
  recommendations: () => api("/api/students/recommendations"),
  skillGap: () => api("/api/students/skill-gap"),
};
