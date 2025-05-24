import React, { useEffect, useState } from "react";
import { Table, Button, Tag, Space, message, Row, Col } from "antd";
import {
  DeleteOutlined,
  EyeOutlined,
  PlusOutlined,
  ReloadOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import { fetchSearchResults, downloadZip, setProjectName } from "../utils/api"; // Import setProjectName
import { useNavigate, useParams } from "react-router-dom"; // Import useParams

function Results() {
  const [searchResults, setSearchResults] = useState([]); // State for search results
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { projectName } = useParams(); // Extract projectName from the URL

  const loadSearchResults = async () => {
    setLoading(true);
    try {
      const data = await fetchSearchResults(projectName); // Pass projectName to the API
      console.log("Fetched projects:", data);
      const processedResults = processResults(data.results || []); // Process the results
      setSearchResults(processedResults);
    } catch (error) {
      message.error("Error fetching search results");
    } finally {
      setLoading(false);
    }
  };

  const processResults = (results) => {
    // Map the pandas DataFrame-like structure to the required format
    return results.map((row) => ({
      filename: row["Document Name"], // Map "Document Name" to "filename"
      keywords: row["Keywords"], // Map "Keywords" to "keywords"
    }));
  };

  useEffect(() => {
    const updateProjectName = async () => {
      try {
        await setProjectName(projectName); // Call setProjectName to update the backend
        console.log(`Project name "${projectName}" set successfully.`);
      } catch (error) {
        console.error("Error setting project name:", error);
        message.error("Failed to set the project name.");
      }
    };

    updateProjectName(); // Update the project name when the component loads
    loadSearchResults(); // Fetch search results when the component loads
  }, [projectName]); // Re-run when projectName changes

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
          onClick={() => navigate(`/docresults/${record.filename}`)} // Pass the filename as a route parameter
        >
          View
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: "2rem" }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: "2rem" }}>
        <Col>
          <h2 style={{ margin: 0 }}>AI SmartScanner - {projectName}</h2> {/* Display project name */}
        </Col>
        <Col>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={() => loadSearchResults()}>
              Refresh
            </Button>
            <Button icon={<PlusOutlined />} type="primary" onClick={() => navigate("/upload")}>
              Upload nieuwe bestanden
            </Button>
            <Button icon={<DownloadOutlined />} onClick={() => message.info("Download not implemented")}>
              Bestanden Downloaden
            </Button>
          </Space>
        </Col>
      </Row>

      <Table
        columns={columns}
        dataSource={searchResults} // Use search results as the data source
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