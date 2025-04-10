import React, { useEffect, useState } from "react";
import { Table, Button, Tag, Space, message, Row, Col } from "antd";
import {
  DeleteOutlined,
  EyeOutlined,
  PlusOutlined,
  ReloadOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import {
  fetchFiles,
  deleteFile,
  downloadZip,
} from "../utils/api"; // Adjust if needed
import { useNavigate } from "react-router-dom";

function Results() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const loadFiles = async () => {
    setLoading(true);
    try {
      const data = await fetchFiles();
      setFiles(data.files || []);
    } catch (error) {
      message.error("Error fetching files");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  const handleDelete = async (filename) => {
    try {
      const result = await deleteFile(filename);
      message.success(result.message);
      await loadFiles();
    } catch (error) {
      message.error("Error deleting file: " + error.message);
    }
  };

  const handleZipDownload = async () => {
    try {
      await downloadZip();
    } catch (error) {
      alert(error.message);
    }
  };

  const handleNewProject = async () => {
    try {
      await resetProject(); // clears Pinecone + local .json
      navigate("/new-scan");
    } catch (error) {
      message.error("Failed to reset project: " + error.message);
    }
  };

  const columns = [
    {
      title: "Bestandsnaam",
      dataIndex: "filename",
      key: "filename",
    },
    {
      title: "Matchende termen",
      dataIndex: "keywords",
      key: "keywords",
      render: (keywords) =>
        keywords?.split(",").map((word, index) => (
          <Tag color="geekblue" key={index}>
            {word.trim()}
          </Tag>
        )),
    },
    {
      title: "Status",
      dataIndex: "scanned",
      key: "scanned",
      render: (scanned) =>
        scanned ? (
          <Tag color="green">Scan gereed</Tag>
        ) : (
          <Tag color="orange">In wachtrij</Tag>
        ),
    },
    {
      title: "Laatste scan",
      dataIndex: "uploaded_at",
      key: "uploaded_at",
    },
    {
      title: "Actie",
      key: "actions",
      render: (_, record) => (
        <Space>
          <Button
            icon={<EyeOutlined />}
            type="link"
            onClick={() => window.open(`/view/${record.filename}`, "_blank")}
          >
            View
          </Button>
          <Button
            icon={<DeleteOutlined />}
            danger
            onClick={() => handleDelete(record.filename)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: "2rem" }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: "2rem" }}>
        <Col>
          <h2 style={{ margin: 0 }}>AI SmartScanner</h2>
        </Col>
        <Col>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={handleNewProject}>
              Nieuwe Scan
            </Button>
            <Button icon={<PlusOutlined />} type="primary" onClick={() => navigate("/upload")}>
              Upload nieuwe bestanden
            </Button>
            <Button icon={<DownloadOutlined />} onClick={handleZipDownload}>
              Bestanden Downloaden
            </Button>
          </Space>
        </Col>
      </Row>

      <Table
        columns={columns}
        dataSource={files}
        loading={loading}
        rowKey="filename"
        pagination={{
          pageSize: 10,
          showSizeChanger: false,
        }}
      />
    </div>
  );
}

export default Results;
