
import { useState } from "react";
import {
  Target,
  Upload,
  FileText,
  X,
  Loader2,
  CheckCircle,
  AlertCircle,
  Sparkles,
  TrendingUp,
  Lightbulb
} from "lucide-react";

import { matchJob } from "../services/api";
import { saveHistoryEntry } from "../services/history";
import "./CareerTools.css";

function JobMatcher() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setError("Please upload a PDF resume.");
      return;
    }

    setFile(selectedFile);
    setResult(null);
    setError("");
  };

  const handleMatch = async () => {
    if (!file) {
      setError("Please upload your resume.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please enter the job description.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await matchJob(file, jobDescription);
      setResult(data);
      saveHistoryEntry({
        feature: "Job Matching",
        title: `Job match - ${file.name}`,
        filename: file.name,
        result: data,
      });
    } catch (err) {
      const status = err.response?.status;

      if (status === 429) {
        setError("Gemini free-tier quota or rate limit reached. Please try again later.");
      } else if (status === 503) {
        setError("Gemini is temporarily unavailable. Please try again later.");
      } else {
        setError(
          err.response?.data?.detail ||
          "Unable to match your resume. Please try again."
        );
      }

      console.error("Job matching error:", err);
    } finally {
      setLoading(false);
    }
  };

  const score = Number(result?.match_score ?? 0);

  return (
    <div className="career-tool-page">
      <div className="tool-heading">
        <div className="tool-heading-icon blue">
          <Target size={25} />
        </div>
        <div>
          <h1>Job Matcher</h1>
          <p>Discover how well your resume matches your target job.</p>
        </div>
      </div>

      <div className="tool-card">
        <h2>Upload Your Resume</h2>
        <p className="tool-description">
          Upload your PDF resume and paste the job description below.
        </p>

        <label className="upload-area">
          <Upload size={28} />
          <strong>Choose your resume PDF</strong>
          <span>Click here to browse files</span>
          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
            hidden
          />
        </label>

        {file && (
          <div className="selected-file">
            <FileText size={20} />
            <span>{file.name}</span>
            <button
              type="button"
              onClick={() => {
                setFile(null);
                setResult(null);
              }}
              aria-label="Remove resume"
            >
              <X size={18} />
            </button>
          </div>
        )}

        <label className="field-label" htmlFor="job-description">
          Job Description
        </label>

        <textarea
          id="job-description"
          className="career-textarea"
          rows={9}
          placeholder="Paste the complete job description here..."
          value={jobDescription}
          onChange={(e) => {
            setJobDescription(e.target.value);
            setResult(null);
          }}
        />

        {error && (
          <div className="tool-error">
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        <button
          className="tool-primary-button"
          onClick={handleMatch}
          disabled={loading || !file || !jobDescription.trim()}
        >
          {loading ? (
            <>
              <Loader2 className="spin" size={19} />
              Matching Resume...
            </>
          ) : (
            <>
              <Sparkles size={19} />
              Analyze Job Match
            </>
          )}
        </button>
      </div>

      {result && (
        <div className="results-container">
          <div className="tool-card">
            <div className="result-heading">
              <TrendingUp size={23} />
              <h2>Job Match Results</h2>
            </div>

            <div className="score-section">
              <div className="score-circle">
                <strong>{score}%</strong>
                <span>Match Score</span>
              </div>
              <div className="score-summary">
                <h3>Overall Assessment</h3>
                <p>{result.overall_assessment || "No assessment provided."}</p>
              </div>
            </div>
          </div>

          <div className="result-grid">
            <ResultList
              title="Matching Skills"
              items={result.matching_skills}
              type="success"
            />
            <ResultList
              title="Missing Skills"
              items={result.missing_skills}
              type="danger"
            />
            <ResultList
              title="Partially Matching Skills"
              items={result.partially_matching_skills}
              type="warning"
            />
            <ResultList
              title="Relevant Projects"
              items={result.relevant_projects}
              type="normal"
            />
            <ResultList
              title="Strengths"
              items={result.strengths}
              type="success"
            />
            <ResultList
              title="Recommendations"
              items={result.recommendations}
              type="normal"
            />
            <ResultList
              title="Learning Suggestions"
              items={result.learning_suggestions}
              type="normal"
            />
          </div>
        </div>
      )}
    </div>
  );
}

function ResultList({ title, items, type }) {
  const list = Array.isArray(items) ? items : [];

  return (
    <div className="tool-card result-list-card">
      <div className="result-heading">
        <CheckCircle size={20} />
        <h3>{title}</h3>
      </div>

      {list.length > 0 ? (
        <ul className={`result-list ${type}`}>
          {list.map((item, index) => (
            <li key={index}>{typeof item === "string" ? item : JSON.stringify(item)}</li>
          ))}
        </ul>
      ) : (
        <p className="empty-result">No information returned.</p>
      )}
    </div>
  );
}

export default JobMatcher;
