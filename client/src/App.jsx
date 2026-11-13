
import { useState } from "react";

import {
  LayoutDashboard,
  FileText,
  Target,
  MessageSquare,
  History as HistoryIcon,
  Settings,
  Sun,
  Moon,
  Bell,
  ArrowUpRight,
  Upload,
  Sparkles,
  Menu,
  X
} from "lucide-react";

import ResumeAnalyzer from "./pages/ResumeAnalyzer";
import JobMatcher from "./pages/JobMatcher";
import InterviewPrep from "./pages/InterviewPrep";
import History from "./pages/History";

import "./App.css";

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Sidebar navigation
  const navigation = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Resume Analyzer", icon: FileText },
    { name: "Job Matcher", icon: Target },
    { name: "Interview Prep", icon: MessageSquare },
    { name: "History", icon: HistoryIcon },
    { name: "Settings", icon: Settings }
  ];

  // Dashboard feature cards
  const features = [
    {
      title: "Resume Analyzer",
      description:
        "Analyze your resume and discover your strengths and improvement areas.",
      icon: FileText,
      color: "purple",
      action: "Analyze Resume",
      page: "Resume Analyzer"
    },
    {
      title: "Job Matcher",
      description:
        "Compare your resume with job descriptions and identify skill gaps.",
      icon: Target,
      color: "blue",
      action: "Match Job",
      page: "Job Matcher"
    },
    {
      title: "Interview Preparation",
      description:
        "Generate personalized technical, project and HR interview questions.",
      icon: MessageSquare,
      color: "orange",
      action: "Prepare Now",
      page: "Interview Prep"
    }
  ];

  // Navigation handler
  const navigate = (page) => {
    setActivePage(page);
    setSidebarOpen(false);
  };

  return (
    <div className={`app ${darkMode ? "dark" : ""}`}>

      {/* SIDEBAR */}
      <aside
        className={`sidebar ${
          sidebarOpen ? "sidebar-open" : ""
        }`}
      >

        {/* BRAND */}
        <div className="brand">
          <div className="brand-icon">
            <Sparkles size={23} />
          </div>

          <div>
            <h2>CareerAI</h2>
            <span>Career Assistant</span>
          </div>

          <button
            className="mobile-close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        <div className="nav-label">MENU</div>

        {/* NAVIGATION */}
        <nav>
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.name}
                className={`nav-item ${
                  activePage === item.name ? "active" : ""
                }`}
                onClick={() => navigate(item.name)}
              >
                <Icon size={19} />
                <span>{item.name}</span>
              </button>
            );
          })}
        </nav>

        {/* SIDEBAR BOTTOM */}
        <div className="sidebar-bottom">

          <div className="upgrade-card">
            <Sparkles size={22} />

            <h3>Career Growth</h3>

            <p>
              Build your skills and prepare for your next opportunity.
            </p>
          </div>

          <div className="profile">
            <div className="avatar">S</div>

            <div>
              <h4>Welcome User</h4>
              <span>Local account</span>
            </div>
          </div>

        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content">

        {/* TOP NAVIGATION */}
        <header className="topbar">

          <div className="topbar-left">

            <button
              className="mobile-menu"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open menu"
            >
              <Menu size={22} />
            </button>

            <div>
              <span className="breadcrumb">Workspace /</span>
              <strong>{activePage}</strong>
            </div>

          </div>

          <div className="topbar-actions">

            {/* DARK MODE TOGGLE */}
            <button
              className="icon-button"
              onClick={() => setDarkMode(!darkMode)}
              title="Toggle theme"
            >
              {darkMode ? (
                <Sun size={19} />
              ) : (
                <Moon size={19} />
              )}
            </button>

            {/* NOTIFICATIONS */}
            <button
              className="icon-button"
              title="Notifications"
              aria-label="Notifications"
            >
              <Bell size={19} />
            </button>

          </div>
        </header>

        {/* PAGE CONTENT */}
        <section className="page-content">

          {/* DASHBOARD */}
          {activePage === "Dashboard" && (
            <>

              <div className="welcome-section">

                <div>
                  <span className="eyebrow">
                    <Sparkles size={15} />
                    YOUR AI CAREER COMPANION
                  </span>

                  <h1>Welcome back! 👋</h1>

                  <p>
                    Take the next step in your career journey.
                    Analyze your resume, match jobs and prepare
                    for interviews.
                  </p>
                </div>

                <div className="welcome-decoration">
                  <Sparkles size={65} />
                </div>

              </div>

              {/* CAREER TOOLS */}
              <div className="section-heading">
                <div>
                  <h2>Your Career Tools</h2>
                  <p>Everything you need to move forward.</p>
                </div>
              </div>

              <div className="feature-grid">

                {features.map((feature) => {
                  const Icon = feature.icon;

                  return (
                    <div
                      className="feature-card"
                      key={feature.title}
                    >

                      <div
                        className={`feature-icon ${feature.color}`}
                      >
                        <Icon size={25} />
                      </div>

                      <h3>{feature.title}</h3>

                      <p>{feature.description}</p>

                      <button
                        className="feature-link"
                        onClick={() => navigate(feature.page)}
                      >
                        {feature.action}
                        <ArrowUpRight size={17} />
                      </button>

                    </div>
                  );
                })}

              </div>

              {/* GET STARTED */}
              <div className="section-heading recent-heading">
                <div>
                  <h2>Get Started</h2>
                  <p>Start by uploading your resume.</p>
                </div>
              </div>

              <div className="upload-card">

                <div className="upload-icon">
                  <Upload size={28} />
                </div>

                <div className="upload-text">
                  <h3>Ready to improve your resume?</h3>

                  <p>
                    Upload your PDF resume to get an AI-powered
                    analysis and personalized recommendations.
                  </p>
                </div>

                <button
                  className="primary-button"
                  onClick={() => navigate("Resume Analyzer")}
                >
                  Upload Resume
                </button>

              </div>

            </>
          )}

          {/* RESUME ANALYZER */}
          {activePage === "Resume Analyzer" && (
            <ResumeAnalyzer />
          )}

          {/* JOB MATCHER */}
          {activePage === "Job Matcher" && (
            <JobMatcher />
          )}

          {/* INTERVIEW PREPARATION */}
          {activePage === "Interview Prep" && (
            <InterviewPrep />
          )}

          {/* HISTORY */}
          {activePage === "History" && <History />}

          {/* SETTINGS */}
          {activePage === "Settings" && (
            <div className="placeholder-page">

              <div className="placeholder-icon">
                <Sparkles size={32} />
              </div>

              <h1>Settings</h1>

              <p>
                Settings functionality will be implemented next.
              </p>

              <button
                className="primary-button"
                onClick={() => navigate("Dashboard")}
              >
                Back to Dashboard
              </button>

            </div>
          )}

          {/* FOOTER */}
          <footer className="footer">
            Built with React, CSS, FastAPI and Gemini AI
          </footer>

        </section>
      </main>

      {/* MOBILE SIDEBAR OVERLAY */}
      {sidebarOpen && (
        <button
          className="sidebar-overlay"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}

    </div>
  );
}

export default App;
