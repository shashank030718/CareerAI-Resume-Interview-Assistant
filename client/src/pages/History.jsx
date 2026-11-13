import { useEffect, useState } from "react";
import {
  History as HistoryIcon,
  FileText,
  Target,
  MessageSquare,
  Trash2,
  Eye,
  Clock3,
  ArrowLeft,
  ClipboardList
} from "lucide-react";
import { clearHistory, deleteHistoryEntry, getHistory } from "../services/history";
import "./History.css";

const featureIcons = {
  "Resume Analysis": FileText,
  "Job Matching": Target,
  "Interview Preparation": MessageSquare,
};

function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Date unavailable" : date.toLocaleString();
}

function History() {
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    setItems(getHistory());
  }, []);

  const handleDelete = (id) => {
    const updated = deleteHistoryEntry(id);
    setItems(updated);
    if (selected?.id === id) setSelected(null);
  };

  const handleClear = () => {
    clearHistory();
    setItems([]);
    setSelected(null);
  };

  if (selected) {
    const result = selected.result?.analysis || selected.result;

    return (
      <div className="history-page">
        <button className="history-back" onClick={() => setSelected(null)}>
          <ArrowLeft size={17} /> Back to history
        </button>
        <div className="history-header">
          <div className="history-heading-icon"><ClipboardList size={24} /></div>
          <div>
            <span className="history-eyebrow">{selected.feature}</span>
            <h1>{selected.title}</h1>
            <p>{selected.filename} · {formatDate(selected.createdAt)}</p>
          </div>
        </div>
        <section className="history-detail-card">
          <h2>Saved result</h2>
          <pre className="history-result-json">
            {JSON.stringify(result, null, 2)}
          </pre>
        </section>
      </div>
    );
  }

  return (
    <div className="history-page">
      <div className="history-header">
        <div className="history-heading-icon"><HistoryIcon size={24} /></div>
        <div>
          <span className="history-eyebrow">YOUR WORKSPACE</span>
          <h1>CareerAI History</h1>
          <p>Revisit results from your resume and interview tools.</p>
        </div>
      </div>

      <div className="history-toolbar">
        <div>
          <strong>{items.length}</strong> saved {items.length === 1 ? "result" : "results"}
          <span> · Stored for this browser session</span>
        </div>
        {items.length > 0 && (
          <button className="history-clear-button" onClick={handleClear}>
            <Trash2 size={16} /> Clear history
          </button>
        )}
      </div>

      {items.length === 0 ? (
        <div className="history-empty">
          <div className="history-empty-icon"><HistoryIcon size={30} /></div>
          <h2>No history yet</h2>
          <p>Your successful resume analyses, job matches and interview question sets will appear here.</p>
        </div>
      ) : (
        <div className="history-list">
          {items.map((item) => {
            const Icon = featureIcons[item.feature] || FileText;
            return (
              <article className="history-item" key={item.id}>
                <div className="history-item-icon"><Icon size={21} /></div>
                <div className="history-item-main">
                  <span className="history-item-type">{item.feature}</span>
                  <h3>{item.title}</h3>
                  <p><FileText size={14} /> {item.filename}</p>
                  <p><Clock3 size={14} /> {formatDate(item.createdAt)}</p>
                </div>
                <div className="history-item-actions">
                  <button className="history-view-button" onClick={() => setSelected(item)}>
                    <Eye size={16} /> View result
                  </button>
                  <button
                    className="history-delete-button"
                    onClick={() => handleDelete(item.id)}
                    aria-label={`Delete ${item.title}`}
                    title="Delete result"
                  >
                    <Trash2 size={17} />
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default History;
