import { Navigate, Route, Routes } from "react-router-dom";
import { getUser } from "./api";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import StudentLayout from "./pages/student/StudentLayout.jsx";
import StudentDashboard from "./pages/student/StudentDashboard.jsx";
import StudentProfile from "./pages/student/StudentProfile.jsx";
import OpportunityDetail from "./pages/student/OpportunityDetail.jsx";
import StudentApplications from "./pages/student/StudentApplications.jsx";
import StudentSkills from "./pages/student/StudentSkills.jsx";
import StudentOpportunities from "./pages/student/StudentOpportunities.jsx";
import StudentSkillGap from "./pages/student/StudentSkillGap.jsx";
import CompanyLayout from "./pages/company/CompanyLayout.jsx";
import CompanyDashboard from "./pages/company/CompanyDashboard.jsx";
import PostOpportunity from "./pages/company/PostOpportunity.jsx";
import Applicants from "./pages/company/Applicants.jsx";
import CollegeLayout from "./pages/college/CollegeLayout.jsx";
import CollegeDashboard from "./pages/college/CollegeDashboard.jsx";

function Guard({ role, children }) {
  const user = getUser();
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to="/" replace />;
  return children;
}

function HomeRedirect() {
  const user = getUser();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role === "company") return <Navigate to="/company" replace />;
  if (user.role === "college") return <Navigate to="/college" replace />;
  return <Navigate to="/student" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/student"
        element={
          <Guard role="student">
            <StudentLayout />
          </Guard>
        }
      >
        <Route index element={<StudentDashboard />} />
        <Route path="profile" element={<StudentProfile />} />
        <Route path="skills" element={<StudentSkills />} />
        <Route path="opportunities" element={<StudentOpportunities />} />
        <Route path="opportunities/:id" element={<OpportunityDetail />} />
        <Route path="skill-gap" element={<StudentSkillGap />} />
        <Route path="applications" element={<StudentApplications />} />
      </Route>

      <Route
        path="/company"
        element={
          <Guard role="company">
            <CompanyLayout />
          </Guard>
        }
      >
        <Route index element={<CompanyDashboard />} />
        <Route path="post" element={<PostOpportunity />} />
        <Route path="opportunities/:id" element={<Applicants />} />
      </Route>

      <Route
        path="/college"
        element={
          <Guard role="college">
            <CollegeLayout />
          </Guard>
        }
      >
        <Route index element={<CollegeDashboard />} />
      </Route>
    </Routes>
  );
}
