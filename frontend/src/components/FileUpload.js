import React, { useState } from "react";
import { uploadFile } from "../utils/api";

function FileUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage("Please select a file.");
      return;
    }

    try {
      const data = await uploadFile(file);
      setMessage(data.message);
    } catch (error) {
      setMessage(`Error from FileUpload: ${error.response?.data?.error || error.message}`);
    }
  };

  return (
    <div>
      <h2>Upload a File</h2>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default FileUpload;
