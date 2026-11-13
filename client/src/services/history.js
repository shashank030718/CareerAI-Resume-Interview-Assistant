const STORAGE_KEY = "careerai_history";
const MAX_HISTORY_ITEMS = 30;

export function getHistory() {
  try {
    const saved = sessionStorage.getItem(STORAGE_KEY);
    const parsed = saved ? JSON.parse(saved) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.error("Unable to read CareerAI history:", error);
    return [];
  }
}

export function saveHistoryEntry({ feature, title, filename, result }) {
  try {
    const current = getHistory();
    const entry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      feature,
      title: title || feature,
      filename: filename || "Resume",
      createdAt: new Date().toISOString(),
      result,
    };

    const updated = [entry, ...current].slice(0, MAX_HISTORY_ITEMS);
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    return true;
  } catch (error) {
    console.error("Unable to save CareerAI history:", error);
    return false;
  }
}

export function deleteHistoryEntry(id) {
  const updated = getHistory().filter((entry) => entry.id !== id);
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (error) {
    console.error("Unable to update CareerAI history:", error);
  }
  return updated;
}

export function clearHistory() {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error("Unable to clear CareerAI history:", error);
  }
}
