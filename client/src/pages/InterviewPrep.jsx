
import { useState } from "react";
import {
  MessageSquare,
  Upload,
  FileText,
  X,
  Loader2,
  Sparkles,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Code,
  Database,
  Briefcase,
  Users
} from "lucide-react";

import { generateQuestions } from "../services/api";
import { saveHistoryEntry } from "../services/history";
import "./CareerTools.css";

const categories = [
  { key: "python_questions", title: "Python Questions", icon: Code },
  { key: "sql_questions", title: "SQL Questions", icon: Database },
  { key: "project_questions", title: "Project Questions", icon: Briefcase },
  { key: "hr_questions", title: "HR Questions", icon: Users }
];

function InterviewPrep() {
  const [file, setFile] = useState(null);
  const [jobRole, setJobRole] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState({});

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

  const handleGenerate = async () => {
    if (!file) {
      setError("Please upload your resume.");
      return;
    }

    if (!jobRole.trim()) {
      setError("Please enter your target job role.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setExpanded({});

    try {
      const data = await generateQuestions(file, jobRole);
      setResult(data);
      saveHistoryEntry({
        feature: "Interview Preparation",
        title: `Interview prep - ${jobRole.trim()}`,
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
          "Unable to generate questions. Please try again."
        );
      }

      console.error("Interview question error:", err);
    } finally {
      setLoading(false);
    }
  };

  const toggleQuestion = (key) => {
    setExpanded((previous) => ({
      ...previous,
      [key]: !previous[key]
    }));
  };

  const totalQuestions = categories.reduce(
    (total, category) =>
      total + (Array.isArray(result?.[category.key]) ? result[category.key].length : 0),
    0
  );

  return (
    <div className="career-tool-page">
      <div className="tool-heading">
        <div className="tool-heading-icon orange">
          <MessageSquare size={25} />
        </div>
        <div>
          <h1>Interview Preparation</h1>
          <p>Practice personalized interview questions based on your resume.</p>
        </div>
      </div>

      <div className="tool-card">
        <h2>Prepare for Your Interview</h2>
        <p className="tool-description">
          Upload your resume and enter the role you're preparing for.
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

        <label className="field-label" htmlFor="job-role">
          Target Job Role
        </label>

        <input
          id="job-role"
          className="career-input"
          type="text"
          placeholder="e.g. Python Developer, Cloud Engineer, DevOps Engineer"
          value={jobRole}
          onChange={(e) => {
            setJobRole(e.target.value);
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
          onClick={handleGenerate}
          disabled={loading || !file || !jobRole.trim()}
        >
          {loading ? (
            <>
              <Loader2 className="spin" size={19} />
              Generating Questions...
            </>
          ) : (
            <>
              <Sparkles size={19} />
              Generate Interview Questions
            </>
          )}
        </button>
      </div>

      {result && (
        <div className="results-container">
          <div className="tool-card interview-summary">
            <div>
              <span className="result-label">YOUR INTERVIEW PRACTICE SET</span>
              <h2>{result.job_role || jobRole}</h2>
              <p>Personalized questions based on your uploaded resume.</p>
            </div>
            <div className="question-count">
              <strong>{totalQuestions}</strong>
              <span>Questions</span>
            </div>
          </div>

          {categories.map((category) => {
            const Icon = category.icon;
            const questions = Array.isArray(result[category.key])
              ? result[category.key]
              : [];

            return (
              <section className="question-category" key={category.key}>
                <div className="category-heading">
                  <Icon size={21} />
                  <h2>{category.title}</h2>
                  <span>{questions.length} Questions</span>
                </div>

                {questions.map((item, index) => {
                  const questionKey = `${category.key}-${index}`;
                  const isExpanded = Boolean(expanded[questionKey]);

                  return (
                    <div className="question-card" key={questionKey}>
                      <button
                        className="question-toggle"
                        onClick={() => toggleQuestion(questionKey)}
                        aria-expanded={isExpanded}
                      >
                        <span className="question-number">
                          {index + 1}
                        </span>
                        <strong>{item.question}</strong>
                        {isExpanded ? (
                          <ChevronUp size={20} />
                        ) : (
                          <ChevronDown size={20} />
                        )}
                      </button>

                      {isExpanded && (
                        <div className="question-answer">
                          <h4>Suggested Answer</h4>
                          <p>
                            {item.suggested_answer || "No suggested answer provided."}
                          </p>

                          <h4>Explanation</h4>
                          <p>
                            {item.explanation || "No explanation provided."}
                          </p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </section>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default InterviewPrep;
