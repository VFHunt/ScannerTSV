import React, { useState } from "react";
import { Upload, message } from "antd";
import { CloudUploadOutlined } from "@ant-design/icons"; // Use a cloud icon
import { useNavigate } from "react-router-dom";
import { uploadFile } from "../utils/api";
import { useNavigate } from "react-router-dom";


function FileUpload() {
  const [files, setFiles] = useState([]); // multiple files store bc of array storage
  const [message, setMessage] = useState("");
  const navigate = useNavigate()

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning("Please select at least one file.");
      return;
    }

    const formData = new FormData();
    fileList.forEach((file) => {
      formData.append("files", file.originFileObj); // Append each file
    });

    try {
      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      console.log("Server response:", result)
      setMessage(result.message);

      if (result.message.includes("successfully")) {
        navigate("/results");
      }

    } catch (error) {
      console.error("Upload Error:", error);
      message.error(`Error: ${error.message}`);
    }
  };

  const handleChange = (info) => {
    const { fileList } = info;
    setFileList(fileList); // Update the file list
  };

  return (
    <div className="fileUploadContainer">
      <Dragger
        multiple
        fileList={fileList}
        onChange={handleChange}
        beforeUpload={() => false} // Prevent automatic upload
        className="uploadArea"
      >
        <p className="ant-upload-drag-icon">
          <CloudUploadOutlined />
        </p>
        <p className="ant-upload-text">Click or drag file to this area to upload</p>
        <p className="ant-upload-hint">Support for a single or bulk upload.</p>
      </Dragger>
    </div>
  );
}

export default FileUpload;