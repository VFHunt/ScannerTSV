import axios from "axios";

const API_BASE_URL = "https://scannertsv.onrender.com"; // Adjust based on backend

export const searchKeywords = async (keyword, scope) => {
  const response = await axios.post(`${API_BASE_URL}/search`, { keyword, scope });
  return response.data;
};

export const searchKeywordsUnscanned = async (keyword, scope) => {
  const response = await axios.post(`${API_BASE_URL}/search_unscanned`, { keyword, scope });
  return response.data;
};

export const uploadFile = async (files) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file); // Append each file
  });

  const response = await axios.post(`${API_BASE_URL}/upload-multiple`, formData, {
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
    const errorData = await response.json();
    throw new Error(errorData.error || "Failed to fetch synonyms");
  }

  return await response.json();
};

export const processFiles = async () => {
  const response = await axios.post(`${API_BASE_URL}/process-files`);
  return response.data;
};

export const fetchFiles = async () => {
  const response = await axios.get(`${API_BASE_URL}/uploaded_files`);
  return response.data; // Return the response data
};

export const get_projects = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/projects`); // Adjust endpoint as needed
    return response.data.projects; // Return the list of projects
  } catch (error) {
    console.error("Error fetching projects:", error);
    throw new Error("Failed to fetch projects.");
  }
};

export const create_new_project = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/projects`, {
      // Add any required payload here if needed
    });

    if (response.status !== 201) {
      throw new Error("Failed to create a new project.");
    }

    return response.data; // Return the created project data
  } catch (error) {
    console.error("Error creating new project:", error);
    throw error;
  }
}

export const downloadZip = async (projectName) => {
  try {
    const response = await fetch(`${API_BASE_URL}/download-multiple`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ project_name: projectName }), // Send projectName to the backend
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to download ZIP.");
    }

    // Convert response into a downloadable blob
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    // Create a temporary link to trigger the download
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${projectName}_results.zip`); // Use projectName in the filename
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    throw new Error(`Download failed: ${error.message}`);
  }
};

export const fetchSearchResults = async (projectName) => {
  const response = await axios.get(`${API_BASE_URL}/fetch_results/${projectName}`);
  return response.data;
};

export const fetchDocumentResults = async (filename) => {
  const response = await axios.get(`${API_BASE_URL}/fetch_docresults/${filename}`);
  return response.data;
};

export const setProjectName = async (projectName) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/set_project_name`, {
      projectName, // Send the project name in the request body
    });

    if (response.status !== 200) {
      throw new Error("Failed to set the project name.");
    }

    return response.data; // Return the response data
  } catch (error) {
    console.error("Error setting project name:", error);
    throw error;
  }
};


export const reset_db = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/reset_db`);
    if (response.status !== 200) {
      throw new Error("Failed to reset projects.");
    }
    return response.data;
  } catch (error) {
    console.error("Error resetting projects:", error);
    throw error;
  }
};

export const getProjectName = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/get_project_name`);
    return response.data.projectName; // Return the project name
  } catch (error) {
    console.error("Error fetching project name:", error);
    throw new Error("Failed to fetch project name.");
  }
};

export const getProjectDate = async (projectName) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/get_project_date`, {
      params: {
        projectName: projectName
      }
    });
    return response.data.creationDate; // Axios automatically parses JSON
  } catch (error) {
    console.error(`Error fetching creation date for project "${projectName}":`, error);
    throw error;
  }
};

// Add this new function to api.js: remember to get the name of the project with the handler
export const get_keywords = async () => { 
  try {
    const response = await axios.get(`${API_BASE_URL}/get_keywords`);
    return response.data.keywords;
  } catch (error) {
    console.error("Error fetching keywords:", error);
    throw error;
  }
};

export const deleteProject = async (projectName) => {
  const response = await axios.post(
    `${API_BASE_URL}/delete_project`,
    { projectName },               // <-- send projectName here
    { headers: { "Content-Type": "application/json" } }
  );

  if (response.status !== 200) {
    throw new Error("Failed to delete the project.");
  }

  return response.data;
};


export const deleteFile = async (projectName, fileName) => {
  const response = await axios.post(
    `${API_BASE_URL}/delete_file`,
    { project_name: projectName, file_name: fileName },  // Match backend field names
    { headers: { "Content-Type": "application/json" } }
  );

  if (response.status !== 200) {
    throw new Error("Failed to delete the file.");
  }

  return response.data.message; // Return the success message
};

export const statusData = async (projectName) => {
  const response = await axios.get(`${API_BASE_URL}/status_data`, {
    params: { project_name: projectName } // Pass the project
  });
  if (response.status !== 200) {
    throw new Error("Failed to fetch status data.");
  }
  
  return response.data.statuses; // Return the statuses array
};
export const getProjectStatus = async (projectName) => {
  const response = await axios.get(
    `${API_BASE_URL}/project/status`,
    {
      params: { project_name: projectName },
      headers: { "Content-Type": "application/json" }
    }
  );

  if (response.status !== 200) {
    throw new Error("Failed to fetch project status.");
  }

  return {
    uploadDate: response.data.upload_date,
    projectScanned: response.data.project_scanned,
  }
};

export const loginUser = async (username, password) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/loginUser`, // 1st argument: URL
      { username: username, password: password }, // 2nd argument: data (body)
      { headers: { "Content-Type": "application/json" } } // 3rd argument: config (headers)
    );

    return response.data; // { success: true/false, message: ... }
  } catch (error) {
    if (error.response) {
      return error.response.data; // backend returned error JSON
    }
    throw new Error("Login request failed");
  }
};






