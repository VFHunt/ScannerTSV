import React, { useEffect, useState } from "react";
import {
  Table,
  Button,
  Tag,
  Space,
  message,
  Row,
  Col,
  Input,
  Modal,
  Checkbox,
} from "antd";
import {
  DeleteOutlined,
  EyeOutlined,
  PlusOutlined,
  DownloadOutlined,
  SearchOutlined,
} from "@ant-design/icons";
import {
  fetchSearchResults,
  downloadZip,
  setProjectName,
  deleteFile,
  statusData,
} from "../utils/api";
import { useNavigate, useParams } from "react-router-dom";
import FileUpload from "../components/FileUpload";
import ScanPopup from "./ScanPopup";

function Results() {

  const [searchResults, setSearchResults] = useState([]); // Original data
  const [filteredResults, setFilteredResults] = useState([]); // Filtered data
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState(""); // Search term
  const [isUploadModalVisible, setIsUploadModalVisible] = useState(false);
  const [isScanPopupVisible, setIsScanPopupVisible] = useState(false);
  const navigate = useNavigate();
  const { projectName } = useParams();
  const [fileStatuses, setFileStatuses] = useState({});

  const loadSearchResultsAndStatuses = async () => {
    setLoading(true);
    try {
      // Fetch search results
      const searchData = await fetchSearchResults(projectName);
      console.log("Fetched projects:", searchData);
      const processedResults = processResults(searchData.results || []);
      setSearchResults(processedResults);
      setFilteredResults(processedResults); // Initialize filtered results
    } catch (error) {
      console.error("Error fetching search results:", error);
      message.error("Error fetching search results.");
      setLoading(false);
      return;
    }

    try {
      // Fetch status data
      const statusDataResult = await statusData(projectName);
      console.log("Status data received:", statusDataResult);

      if (Array.isArray(statusDataResult)) {
        const statuses = {};
        statusDataResult.forEach((item) => {
          statuses[item.file_name] = item;
        });
        setFileStatuses(statuses);
      } else {
        console.error("Invalid format for status data:", statusDataResult);
        message.error("Invalid status data format from server.");
      }
    } catch (error) {
      console.error("Error fetching status data:", error);
      message.error("Error fetching status data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSearchResultsAndStatuses();
  }, [projectName]);

  // Filter logic
  useEffect(() => {
    if (searchTerm.trim() === "") {
      setFilteredResults(searchResults); // Reset to all results if search term is empty
    } else {
      const lowercasedSearchTerm = searchTerm.toLowerCase();
      const filtered = searchResults.filter((result) =>
        result.keywords.some((keyword) =>
          keyword.toLowerCase().includes(lowercasedSearchTerm)
        )
      );
      setFilteredResults(filtered);
    }
  }, [searchTerm, searchResults]);

  const handleDeleteFile = async (fileName) => {
    try {
      await deleteFile(projectName, fileName);
      message.success(`Bestand '${fileName}' succesvol verwijderd.`);
      loadSearchResultsAndStatuses();
    } catch (error) {
      console.error("Delete failed:", error);
      message.error("Bestand verwijderen is mislukt.");
    }
  };

  const processResults = (results) => {
    return results.map((row) => {
      const filename = row["Document Name"] || row["file_name"];
      return {
        filename,
        keywords: row["Keywords"],
        key: filename,
      };
    });
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
  }, [projectName]);

  const columns = [
    {
      title: (
        <>
          <Checkbox /> Bestandsnaam
        </>
      ),
      dataIndex: "filename",
      key: "filename",
      render: (filename) => (
        <>
          <Checkbox /> {filename}
        </>
      ),
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
      title: "Status",
      dataIndex: "filename",
      key: "status",
      render: (filename) => {
        const status = fileStatuses[filename];
        return status ? (
          status.scanned ? (
            <Tag color="green">Scanned</Tag>
          ) : (
            <Tag color="orange">Not Scanned</Tag>
          )
        ) : (
          "Loading..."
        );
      },
    },
    {
      title: "Laatste scan",
      dataIndex: "filename",
      key: "scanned_time",
      render: (filename) => {
        const status = fileStatuses[filename];
        return status?.scanned_time
          ? new Date(status.scanned_time).toLocaleString("nl-NL", {
              dateStyle: "short",
              timeStyle: "short",
            })
          : "N/A";
      },
    },
    {
      title: "Actie",
      key: "action",
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/docresults/${record.filename}`)}
          >
            View
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteFile(record.filename)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  const handleStartScan = (woordenlijst, documentSelectie, terms) => {
    console.log("Starting scan with:", woordenlijst, documentSelectie, terms);
    setIsScanPopupVisible(false);
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
              onClick={() => setIsScanPopupVisible(true)}
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
        dataSource={filteredResults} // Use filtered results here
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
            loadSearchResultsAndStatuses();
          }}
        />
      </Modal>

      <ScanPopup
        visible={isScanPopupVisible}
        onCancel={() => {
          setIsScanPopupVisible(false);
          loadSearchResultsAndStatuses(); // Refresh the page data
        }}
        onStartScan={handleStartScan}
      />
    </div>
  );
}

export default Results;
