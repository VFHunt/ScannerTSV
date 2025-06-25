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
  getFocus,
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
      const searchData = await fetchSearchResults(projectName); // fetching results by project name from the database 
      console.log("Fetched projects:", searchData);
      const processedResults = processResults(searchData.results || []);
      setSearchResults(processedResults);
      setFilteredResults(processedResults); // Initialize filtered results
    } catch (error) {
      console.error("Fout bij het ophalen van zoekresultaten:", error);
      message.error("Fout bij het ophalen van zoekresultaten.");
      setLoading(false);
      return;
    }

    try {
      // Fetch status data
      const statusDataResult = await statusData(projectName);
      console.log("Statusgegevens ontvangen:", statusDataResult);

      // try {
      //   const focus = await getFocus(projectName);
      //   console.log("Laatste focus ontvangen:", focus);
      // } catch (error) {
      //   console.error("Fout bij het ophalen van de laatste focus:", error);
      // }

      if (Array.isArray(statusDataResult)) {
        const statuses = {};
        statusDataResult.forEach((item) => {
          statuses[item.file_name] = item;
        });
        setFileStatuses(statuses);
      } else {
        console.error("Ongeldig formaat voor statusgegevens:", statusDataResult);
        message.error("Ongeldig statusgegevensformaat van de server.");
      }
    } catch (error) {
      console.error("Fout bij het ophalen van statusgegevens:", error);
      message.error("Fout bij het ophalen van statusgegevens.");
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
      // Sort by the number of keywords (descending order)
      const sortedResults = [...searchResults].sort((a, b) => {
        const aKeywordCount = a.keywords ? a.keywords.length : 0;
        const bKeywordCount = b.keywords ? b.keywords.length : 0;
        return bKeywordCount - aKeywordCount; // More keywords come first
      });
      setFilteredResults(sortedResults); // Reset to all results if search term is empty
    } else {
      const lowercasedSearchTerm = searchTerm.toLowerCase();
      const filtered = searchResults.filter((result) =>
        result.keywords.some((word) =>
          word.toLowerCase().includes(lowercasedSearchTerm)
        )
      );
      // Sort filtered results by the number of keywords
      const sortedFiltered = [...filtered].sort((a, b) => {
        const aKeywordCount = a.keywords ? a.keywords.length : 0;
        const bKeywordCount = b.keywords ? b.keywords.length : 0;
        return bKeywordCount - aKeywordCount; // More keywords come first
      });
      setFilteredResults(sortedFiltered);
    }
  }, [searchTerm, searchResults]);

  const handleDeleteFile = async (fileName) => {
    try {
      await deleteFile(projectName, fileName);
      message.success(`Bestand '${fileName}' succesvol verwijderd.`);
      loadSearchResultsAndStatuses();
    } catch (error) {
      console.error("Verwijderen mislukt:", error);
      message.error("Verwijderen van bestand is mislukt.");
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

  const getColorFromDistance = (distance) => {
    if (distance >= 0.2 && distance < 0.49) return "#a8e6cf"; // greenish
    if (distance >= 0.5 && distance < 0.79) return "#ffd3b6"; // orangeish
    if (distance >= 0.8 && distance <= 0.99) return "#ff8b94"; // reddish
  };


  const cleanKeywords = (keywords) => {
    const flatList = [];
    keywords.forEach((item) => {
      const [wordList, distance] = item;
      if (Array.isArray(wordList)) {
        wordList.forEach((word) => {
          flatList.push({ word: word.trim(), distance });
        });
      } else if (typeof wordList === "string") {
        // Fallback in case data is just a single word
        flatList.push({ word: wordList.trim(), distance: distance || 1.0 });
      }
    });
    return flatList;
  };



  useEffect(() => {
    const updateProjectName = async () => {
      try {
        await setProjectName(projectName);
        console.log(`Projectnaam "${projectName}" succesvol ingesteld.`);
      } catch (error) {
        console.error("Fout bij het instellen van de projectnaam:", error);
        message.error("Projectnaam instellen is mislukt.");
      }
    };

    updateProjectName();
  }, [projectName]);

  const columns = [
    {
      title: "Bestandsnaam",
      dataIndex: "filename",
      key: "filename",
      render: (filename) => <>{filename}</>,
    },
    {
      title: "Matchende termen",
      dataIndex: "keywords",
      key: "keywords",
      render: (keywords) => {
        const flatKeywords = cleanKeywords(keywords);
        return flatKeywords.map(({ word, distance }, index) => {
          const color = getColorFromDistance(distance);
          return (
            <Tag
              key={index}
              style={{
                backgroundColor: color,
                border: "none",
                color: "#000", // or "#333" for better readability
                marginBottom: 4,
              }}
            >
              {word}
            </Tag>
          );
        });
      },


      sorter: (a, b) => {
        // Sort by whether keywords are empty or not
        const aHasKeywords = a.keywords && a.keywords.length > 0;
        const bHasKeywords = b.keywords && b.keywords.length > 0;
        return bHasKeywords - aHasKeywords; // Non-empty keywords come first
      },
    },
    {
      title: "Status",
      dataIndex: "filename",
      key: "status",
      render: (filename) => {
        const status = fileStatuses[filename];
        return status ? (
          status.scanned ? (
            <Tag color="green">Gescand</Tag>
          ) : (
            <Tag color="orange">Niet gescand</Tag>
          )
        ) : (
          "Laden..."
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
          : "N/B";
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
            Bekijken
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteFile(record.filename)}
          >
            Verwijderen
          </Button>
        </Space>
      ),
    },
  ];

  const handleStartScan = (woordenlijst, documentSelectie, terms) => {
    console.log("Scan starten met:", woordenlijst, documentSelectie, terms);
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
              Nieuwe scan
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={async () => {
                try {
                  await downloadZip(projectName);
                  message.success("Bestanden succesvol gedownload.");
                } catch (error) {
                  console.error("Fout bij het downloaden van bestanden:", error);
                  message.error("Fout bij het downloaden van bestanden.");
                }
              }}
            >
              Bestanden downloaden
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
            // window.location.reload();
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
