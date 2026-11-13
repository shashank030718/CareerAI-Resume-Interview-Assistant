
import { useState } from "react";
import {
  Upload,
  FileText,
  Sparkles,
  CheckCircle,
  AlertCircle,
  LoaderCircle,
  X
} from "lucide-react";

import { analyzeResume } from "../services/api";
import { saveHistoryEntry } from "../services/history";
import "./ResumeAnalyzer.css";

function ResumeAnalyzer() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) return;

    if (selectedFile.type !== "application/pdf") {
      setError("Please upload a PDF file.");
      return;
    }

    setFile(selectedFile);
    setResult(null);
    setError("");
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please upload your resume first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await analyzeResume(file);
      setResult(data);
      const analysisData = data?.analysis || data;
      saveHistoryEntry({
        feature: "Resume Analysis",
        title: analysisData?.candidate_name || file.name,
        filename: file.name,
        result: data,
      });
    } catch (err) {
      const message = err.response?.data?.detail;

      if (err.response?.status === 503) {
        setError("Gemini AI is temporarily unavailable. Please try again later.");
      } else if (err.response?.status === 429) {
        setError("API rate limit reached. Please try again later.");
      } else {
        setError(
          typeof message === "string"
            ? message
            : "Unable to analyze your resume. Please check your backend."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const analysis = result?.analysis || result;

  const renderList = (items) => {
    if (!Array.isArray(items) || items.length === 0) {
      return <p className="empty-text">No information available.</p>;
    }

    return (
      <ul className="analysis-list">
        {items.map((item, index) => (
          <li key={index}>
            {typeof item === "object"
              ? JSON.stringify(item)
              : String(item)}
          </li>
        ))}
      </ul>
    );
  };

  const renderSkills = (items) => {
    if (!Array.isArray(items) || items.length === 0) {
      return <p className="empty-text">No skills found.</p>;
    }

    return (
      <div className="skill-tags">
        {items.map((skill, index) => (
          <span key={index}>{String(skill)}</span>
        ))}
      </div>
    );
  };

  return (
    <div className="resume-page">

      <div className="resume-heading">
        <div>
          <span className="resume-eyebrow">
            <Sparkles size={15} /> GEMINI AI POWERED
          </span>
          <h1>Resume Analyzer</h1>
          <p>
            Upload your resume and get personalized AI-powered
            insights about your professional profile.
          </p>
        </div>
      </div>

      <div className="resume-upload-card">

        <div className="upload-heading">
          <div className="resume-upload-icon">
            <Upload size={25} />
          </div>
          <div>
            <h2>Upload Your Resume</h2>
            <p>Upload your resume in PDF format.</p>
          </div>
        </div>

        <label className="resume-dropzone">
          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
            hidden
          />

          <div className="dropzone-icon">
            <FileText size={30} />
          </div>

          <h3>Choose your resume</h3>
          <p>Click here to browse PDF files</p>
          <span>PDF files only</span>
        </label>

        {file && (
          <div className="selected-file">
            <FileText size={20} />
            <div>
              <strong>{file.name}</strong>
              <span>{(file.size / 1024).toFixed(1)} KB</span>
            </div>

            <button
              onClick={() => {
                setFile(null);
                setResult(null);
                setError("");
              }}
              aria-label="Remove file"
            >
              <X size={18} />
            </button>
          </div>
        )}

        {error && (
          <div className="resume-error">
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        <button
          className="analyze-button"
          onClick={handleAnalyze}
          disabled={!file || loading}
        >
          {loading ? (
            <>
              <LoaderCircle className="spin" size={19} />
              Analyzing Resume...
            </>
          ) : (
            <>
              <Sparkles size={19} />
              Analyze My Resume
            </>
          )}
        </button>

        <p className="privacy-note">
          Your resume is processed by the AI backend for analysis.
        </p>
      </div>

      {result && analysis && (
        <div className="analysis-results">

          <div className="result-success">
            <CheckCircle size={20} />
            Resume analysis completed successfully!
          </div>

          <div className="candidate-card">
            <span className="result-label">CANDIDATE OVERVIEW</span>
            <h2>{analysis.candidate_name || "Candidate"}</h2>
            <p>
              {analysis.professional_summary ||
                "No professional summary available."}
            </p>
          </div>

          <div className="result-section">
            <h2>Technical Skills</h2>

            <div className="result-grid">
              <div className="result-card">
                <h3>Technical Skills</h3>
                {renderSkills(analysis.technical_skills)}
              </div>

              <div className="result-card">
                <h3>Programming Languages</h3>
                {renderSkills(analysis.programming_languages)}
              </div>

              <div className="result-card">
                <h3>Tools and Frameworks</h3>
                {renderSkills(analysis.tools_and_frameworks)}
              </div>
            </div>
          </div>

          <div className="result-section">
            <h2>Education</h2>

            {Array.isArray(analysis.education) &&
              analysis.education.length > 0 ? (
                analysis.education.map((item, index) => (
                  <div className="result-card" key={index}>
                    <h3>{item.degree || "Degree"}</h3>
                    <p>{item.institution || "Institution not specified"}</p>
                    <p>{item.location || ""} {item.duration || ""}</p>
                    {item.gpa && <p>CGPA: {item.gpa}</p>}
                  </div>
                ))
              ) : (
                <p className="empty-text">No education details found.</p>
              )}
          </div>

          <div className="result-section">
            <h2>Projects</h2>

            {Array.isArray(analysis.projects) &&
              analysis.projects.length > 0 ? (
                analysis.projects.map((project, index) => (
                  <div className="result-card" key={index}>
                    <h3>{project.title || "Project"}</h3>
                    <p>
                      {project.objective_and_achievements ||
                        "No project description available."}
                    </p>
                    <h4>Technologies</h4>
                    {renderSkills(project.technologies)}
                  </div>
                ))
              ) : (
                <p className="empty-text">No projects found.</p>
              )}
          </div>

          <div className="result-section">
            <h2>Professional Experience</h2>
            {renderList(analysis.experience)}
          </div>

          <div className="result-section">
            <h2>Certifications</h2>
            {renderList(analysis.certifications)}
          </div>

          <div className="result-grid">
            <div className="result-card">
              <h3>Strengths</h3>
              {renderList(analysis.strengths)}
            </div>

            <div className="result-card">
              <h3>Areas to Improve</h3>
              {renderList(analysis.areas_to_improve)}
            </div>
          </div>

        </div>
      )}
    </div>
  );
}

export default ResumeAnalyzer;
