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
    <div>
      <h2>Upload a File</h2>
      <input type="file" multiple onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default FileUpload;
