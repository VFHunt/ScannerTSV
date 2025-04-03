import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:5000"; // Adjust based on backend

export const searchKeywords = async (keyword) => {
  const response = await axios.post(`${API_BASE_URL}/search`, { keyword });
  return response.data;
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
};