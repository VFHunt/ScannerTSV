import React, { useState } from "react";
import { uploadFile, processFiles } from "../utils/api"; // you handle upload and processing separately
import { Upload, message as antdMessage, Button, Spin } from "antd";
import { CloudUploadOutlined, DeleteOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";

const { Dragger } = Upload;

function FileUpload() {
  const [files, setFiles] = useState([]);
  const [statusMessage, setStatusMessage] = useState(""); // Message to display after processing
  const [loadingStep, setLoadingStep] = useState(null); // Track the current loading step
  const [isUploadComplete, setIsUploadComplete] = useState(false); // Track if the upload process is complete

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

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file.originFileObj); // Access raw file
    });

    try {
      // Step 1: Upload
      setLoadingStep("uploading");
      const uploadResponse = await uploadFile(formData);
      setStatusMessage(uploadResponse.message || "Files uploaded!");

      // Step 2: Process
      setLoadingStep("processing");
      const processResponse = await processFiles();
      setStatusMessage(processResponse.message || "Files processed!");

      // Mark upload as complete
      setIsUploadComplete(true);

      // Display the list of successfully uploaded files
      const fileNames = files.map((file) => file.name).join(", ");
      setStatusMessage(`The following files have been successfully uploaded and processed: ${fileNames}`);
    } catch (error) {
      console.error("Upload or processing error:", error);
      setStatusMessage("Something went wrong during upload or processing.");
    } finally {
      setLoadingStep(null); // Reset loading step
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
      {/* Conditionally render the Dragger */}
      {!isUploadComplete && !loadingStep && (
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
      )}

      {/* Conditionally render the buttons */}
      {files.length > 0 && !loadingStep && !isUploadComplete && (
        <div style={{ marginTop: "20px", textAlign: "center" }}>
          <Button type="primary" onClick={handleUpload} style={{ marginRight: "10px" }}>
            Upload & Process
          </Button>
          <Button danger icon={<DeleteOutlined />} onClick={() => setFiles([])}>
            Clear All
          </Button>
        </div>
      )}

      {/* Loader */}
      {loadingStep && (
        <div style={{ marginTop: "20px", textAlign: "center" }}>
          <Spin size="large" />
          <p style={{ marginTop: "10px", color: "#1890ff" }}>
            {loadingStep === "uploading" && "Uploading files..."}
            {loadingStep === "processing" && "Processing files..."}
          </p>
        </div>
      )}

      {/* Final Message */}
      {isUploadComplete && (
        <div style={{ marginTop: "20px", textAlign: "center", color: "#1890ff" }}>
          <p>{statusMessage}</p>
        </div>
      )}
    </div>
  );
}

export default FileUpload;
