import React, { useState } from "react";
import { uploadFile } from "../utils/api";

function FileUpload() {
  const [files, setFiles] = useState([]); // multiple files store bc of array storage
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    setFiles([...e.target.files]);
  };

  const handleUpload = async () => { // now loops through all files
    if (files.length === 0) {
      setMessage("Please select at least one file.");
      return;
    }

    const  formData = new FormData();
      files.forEach((file) => {
        formData.append("files", file); // append each file
      });

    try {
      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      console.log("Server response:", result)
      setMessage(result.message);
    } catch (error) {
      console.error("Upload Error:", error);
      setMessage(`Error: ${error.message}`);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>Upload a File</h2>
      <div style={styles.dropZone}>
        <input
          type="file" multiple
          onChange={handleFileChange}
          style={styles.fileInput}
        />
        <div style={styles.iconContainer}>
          <span style={styles.cloudIcon}>☁</span>
          <p style={styles.text}>
            Drag and drop a file here, or click to select a file
          </p>
        </div>
      </div>
      <button onClick={handleUpload} style={styles.uploadButton}>
        Upload
      </button>
      {message && <p style={styles.message}>{message}</p>}
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "20px",
    border: "1px solid #ccc",
    borderRadius: "10px",
    backgroundColor: "#f9f9f9",
    width: "100%",
    maxWidth: "500px",
    boxSizing: "border-box",
  },
  header: {
    marginBottom: "20px",
    fontSize: "1.5rem",
    fontWeight: "bold",
  },
  dropZone: {
    position: "relative",
    width: "100%",
    height: "200px",
    border: "2px dashed #007BFF",
    borderRadius: "10px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#eaf4ff",
    cursor: "pointer",
    marginBottom: "20px",
  },
  fileInput: {
    position: "absolute",
    width: "100%",
    height: "100%",
    opacity: 0,
    cursor: "pointer",
  },
  iconContainer: {
    textAlign: "center",
  },
  cloudIcon: {
    fontSize: "3rem",
    color: "#007BFF",
    marginBottom: "10px",
  },
  text: {
    fontSize: "1rem",
    color: "#555",
  },
  uploadButton: {
    backgroundColor: "#007BFF",
    color: "white",
    border: "none",
    borderRadius: "5px",
    padding: "10px 15px",
    cursor: "pointer",
    fontSize: "16px",
  },
  message: {
    marginTop: "10px",
    fontSize: "14px",
    color: "#333",
  },
};

export default FileUpload;
