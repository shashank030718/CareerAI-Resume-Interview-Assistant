
import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: 600000,
});

export const analyzeResume = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await API.post("/analyze-resume", formData);
  return response.data;
};

export const matchJob = async (file, jobDescription) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("job_description", jobDescription);

  const response = await API.post("/match-job", formData);
  return response.data;
};

export const generateQuestions = async (file, jobRole) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("job_role", jobRole);

  const response = await API.post("/generate-questions", formData);
  return response.data;
};

export default API;
