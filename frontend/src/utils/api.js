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

export const getSynonyms = async (keywordsList) => {
  const response = await fetch(`${API_BASE_URL}/get_synonyms`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body:  JSON.stringify({ keywords: keywordsList }), // Send the keyword as an array
  });

  if (!response.ok) {
    throw new Error(await response.json());
  }

  return response.json();
};

export const get_projects = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/projects`); // Adjust endpoint as needed
    return response.data; // Return the list of projects
  } catch (error) {
    console.error("Error fetching projects:", error);
    throw new Error("Failed to fetch projects.");
  }
};