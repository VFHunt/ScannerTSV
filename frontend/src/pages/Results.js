import React, { useEffect, useState } from "react";
import { Table, Button, Tag, Space, message, Row, Col, Input, Modal } from "antd";
import {
  DeleteOutlined,
  EyeOutlined,
  PlusOutlined,
  ReloadOutlined,
  DownloadOutlined,
  SearchOutlined,
} from "@ant-design/icons";
import { fetchSearchResults, downloadZip, setProjectName } from "../utils/api";
import { useNavigate, useParams } from "react-router-dom";
import FileUpload from "../components/FileUpload";
import ScanPopup from "./ScanPopup"; // Import ScanPopup

function Results() {
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [isUploadModalVisible, setIsUploadModalVisible] = useState(false);
  const [isScanPopupVisible, setIsScanPopupVisible] = useState(false); // State for ScanPopup visibility
  const navigate = useNavigate();
  const { projectName } = useParams();

  const loadSearchResults = async () => {
    setLoading(true);
    try {
      const data = await fetchSearchResults(projectName);
      console.log("Fetched projects:", data);
      const processedResults = processResults(data.results || []);
      setSearchResults(processedResults);
    } catch (error) {
      message.error("Error fetching search results");
    } finally {
      setLoading(false);
    }
  };

  const processResults = (results) => {
    return results.map((row) => ({
      filename: row["Document Name"],
      keywords: row["Keywords"],
    }));
  };

  useEffect(() => {
    const updateProjectName = async () => {
      try {
        await setProjectName(projectName);
        console.log(`Project name "${projectName}" set successfully.`);
      } catch (error) {
        console.error("Error setting project name:", error);
        message.error("Failed to set the project name.");
      }
    };

    updateProjectName();
    loadSearchResults();
  }, [projectName]);

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
        keywords?.map((word, index) => (
          <Tag color="geekblue" key={index}>
            {word.trim()}
          </Tag>
        )),
    },
    {
      title: "Actie",
      key: "view",
      render: (_, record) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => navigate(`/docresults/${record.filename}`)}
        >
          View
        </Button>
      ),
    },
  ];

  const handleStartScan = (woordenlijst, documentSelectie, terms) => {
    console.log("Starting scan with:");
    console.log("Woordenlijst:", woordenlijst);
    console.log("Document Selectie:", documentSelectie);
    console.log("Terms:", terms);
    setIsScanPopupVisible(false); // Close the ScanPopup after starting the scan
  };

  return (
    <div style={{ padding: "2rem" }}>
      <Row gutter={[16, 16]} align="middle">
        <Col flex="auto">
          <Input
            placeholder="Zoekterm"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: 200 }}
            suffix={<SearchOutlined />}
          />
        </Col>
        <Col>
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setIsScanPopupVisible(true)} // Open ScanPopup
            >
              Nieuwe Scan
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={() => message.info("Download not implemented")}
            >
              Bestanden Downloaden
            </Button>
            <Button
              icon={<PlusOutlined />}
              onClick={() => setIsUploadModalVisible(true)}
            >
              Bestand toevoegen
            </Button>
          </Space>
        </Col>
      </Row>

      <Table
        style={{ marginTop: "1rem" }}
        columns={columns}
        dataSource={searchResults}
        loading={loading}
        rowKey="filename"
        pagination={{
          pageSize: 10,
          showSizeChanger: false,
        }}
      />

      <Modal
        title="Bestand toevoegen"
        open={isUploadModalVisible}
        onCancel={() => setIsUploadModalVisible(false)}
        footer={null}
        width={800}
      >
        <FileUpload
          projectName={projectName}
          onUploadComplete={() => {
            setIsUploadModalVisible(false);
            loadSearchResults();
          }}
        />
      </Modal>

      <ScanPopup // Add ScanPopup component
        visible={isScanPopupVisible}
        onCancel={() => setIsScanPopupVisible(false)}
        onStartScan={handleStartScan}
      />
    </div>
  );
}

export default Results;