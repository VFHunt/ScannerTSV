import React, { useEffect, useState } from "react";

function Results() {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/uploaded_files");
        const data = await response.json();
        setFiles(data.files);
      } catch (error) {
        console.error("Error fetching uploaded files:", error);
      }
    };

    fetchFiles();
  }, []);

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Results</h2>
      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Uploaded At</th>
            <th>Scanned</th>
            <th>Keywords</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file, index) => (
            <tr key={index}>
              <td>{file.filename}</td>
              <td>{file.uploaded_at}</td>
              <td>{file.scanned ? "✅" : "❌"}</td>
              <td>{file.keywords}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Results;
