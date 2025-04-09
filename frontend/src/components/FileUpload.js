import React, { useState } from "react";
import { Upload, message, Button } from "antd";
import { CloudUploadOutlined, DeleteOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";

const { Dragger } = Upload;

function FileUpload() {
  const [files, setFiles] = useState([]);
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (files.length === 0) {
      message.warning("Please select at least one file.");
      return;
    }
  
    message.loading("Uploading the files...", 2); // Display a loading message
  
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file.originFileObj); // Append each file
    });
  
    try {
      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });
  
      const result = await response.json();
      message.success(result.message || "Files uploaded successfully!");
  
      if (result.message.includes("successfully")) {
        setFiles([]); // Clear all files after successful upload
        navigate("/results"); // Navigate to the results page
      }
    } catch (error) {
      console.error("Upload Error:", error);
      message.error(`Error: ${error.message}`);
    }
  };

  const handleChange = (info) => {
    const { fileList } = info;
    setFiles(fileList); // Update the file list
  };

  const handleRemove = (file) => {
    setFiles((prevFiles) => prevFiles.filter((item) => item.uid !== file.uid)); // Remove the selected file
    message.info(`${file.name} removed.`);
  };

  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
      <Dragger
        multiple
        fileList={files}
        onChange={handleChange}
        onRemove={handleRemove} // Enable file removal
        beforeUpload={() => false} // Prevent automatic upload
        style={{
          padding: "40px",
          border: "2px dashed #d9d9d9",
          borderRadius: "50%", // Make it circular like a cloud
          backgroundColor: "#eaf4ff", // Light blue background
          textAlign: "center",
          width: "300px", // Fixed width
          height: "300px", // Fixed height to make it square
          margin: "0 auto", // Center the cloud
        }}
      >
        <p className="ant-upload-drag-icon">
          <CloudUploadOutlined style={{ fontSize: "64px", color: "#1890ff" }} />
        </p>
        <p className="ant-upload-text">Click or drag file to this area to upload</p>
        <p className="ant-upload-hint">Support for a single or bulk upload.</p>
      </Dragger>
      {files.length > 0 && (
        <div style={{ marginTop: "20px", textAlign: "center" }}>
          <Button
            type="primary"
            onClick={handleUpload}
            style={{
              marginRight: "10px",
              padding: "10px 20px",
              backgroundColor: "#1890ff",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            Upload
          </Button>
          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={() => setFiles([])} // Clear all files
            style={{
              padding: "10px 20px",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            Clear All
          </Button>
        </div>
      )}
    </div>
  );
}

export default FileUpload;