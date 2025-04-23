import React, { useState } from "react";
import { uploadFile, processFiles } from "../utils/api"; // you handle upload and processing separately
import { Upload, message as antdMessage, Button } from "antd";
import { CloudUploadOutlined, DeleteOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";

const { Dragger } = Upload;

function FileUpload() {
  const [files, setFiles] = useState([]);
  const [statusMessage, setStatusMessage] = useState(""); // Renamed to avoid conflict with AntD's message
  const navigate = useNavigate();

  const handleChange = (info) => {
    setFiles(info.fileList);
  };

  const handleRemove = (file) => {
    setFiles((prevFiles) => prevFiles.filter((item) => item.uid !== file.uid));
    antdMessage.info(`${file.name} removed.`);
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setStatusMessage("Please select at least one file.");
      return;
    }

    antdMessage.loading("Uploading files...", 2);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file.originFileObj); // Access raw file
    });

    try {
      // Step 1: Upload
      const uploadResponse = await uploadFile(formData);
      setStatusMessage(uploadResponse.message || "Files uploaded!");

      // Step 2: Process
      const processResponse = await processFiles();
      setStatusMessage(processResponse.message || "Files processed!");

      // Step 3: Go to results
      navigate("/results");

    } catch (error) {
      console.error("Upload or processing error:", error);
      setStatusMessage("Something went wrong during upload or processing.");
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
      <Dragger
        multiple
        fileList={files}
        onChange={handleChange}
        onRemove={handleRemove}
        beforeUpload={() => false} // Prevent auto-upload
        style={{
          padding: "40px",
          border: "2px dashed #d9d9d9",
          borderRadius: "50%",
          backgroundColor: "#eaf4ff",
          textAlign: "center",
          width: "300px",
          height: "300px",
          margin: "0 auto",
        }}
      >
        <p className="ant-upload-drag-icon">
          <CloudUploadOutlined style={{ fontSize: "64px", color: "#1890ff" }} />
        </p>
        <p className="ant-upload-text">Click or drag files here to upload</p>
        <p className="ant-upload-hint">Supports single or multiple files</p>
      </Dragger>

      {files.length > 0 && (
        <div style={{ marginTop: "20px", textAlign: "center" }}>
          <Button type="primary" onClick={handleUpload} style={{ marginRight: "10px" }}>
            Upload & Process
          </Button>
          <Button danger icon={<DeleteOutlined />} onClick={() => setFiles([])}>
            Clear All
          </Button>
        </div>
      )}

      {statusMessage && (
        <div style={{ marginTop: "20px", textAlign: "center", color: "#1890ff" }}>
          {statusMessage}
        </div>
      )}
    </div>
  );
}

export default FileUpload;
