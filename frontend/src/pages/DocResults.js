import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { List, Tag, Spin, Tooltip, Card, Typography, Row, Col, Select } from "antd";
import { fetchDocumentResults } from "../utils/api";

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

// Component for displaying individual document result items
const DocumentResultItem = ({ item }) => (
  <Card
    style={{
      marginBottom: "1.5rem",
      borderRadius: "16px",
      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.05)",
    }}
    bodyStyle={{ padding: "1.5rem" }}
    hoverable
  >
    <Row gutter={[16, 16]}>
      <Col span={18}>
        {/* Semantic Chunk */}
        <Paragraph ellipsis={{ rows: 4, expandable: true, symbol: "more" }} style={{ fontSize: "15px" }}>
          {item.text}
        </Paragraph>
      </Col>

      <Col span={6}>
        {/* Keywords and Page Number */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.25rem" }}>
            <Text strong style={{ fontSize: "14px" }}>
              Match:
            </Text>
            {(item.keywords || []).map((kw, i) => (
              <Tag color="geekblue" key={i} style={{ marginBottom: "0.25rem" }}>
                {kw}
              </Tag>
            ))}
          </div>
          <Tooltip title={`Page number`}>
            <Tag
              color="gold"
              style={{
                display: "inline-flex",
                alignItems: "center",
                padding: "0 6px", // Adjust padding to fit the text
                height: "auto", // Remove fixed height
                lineHeight: "1.5", // Adjust line height for better alignment
                fontSize: "14px", // Ensure font size matches the text
              }}
            >
              Page {item.page}
            </Tag>
          </Tooltip>
        </div>
      </Col>
    </Row>
  </Card>
);

// Main component for displaying document results
function DocResults() {
  const { filename } = useParams();
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedKeywords, setSelectedKeywords] = useState([]);
  const encodedFilename = encodeURIComponent(filename);

  const fetchDocumentResultsHandler = async () => {
    setLoading(true);
    try {
      const data = await fetchDocumentResults(encodedFilename);
      setContent(data.results || []);
    } catch (error) {
      console.error("Error fetching document results:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocumentResultsHandler();
  }, [filename]);

  // Extract unique keywords for filtering
  const allKeywords = [...new Set(content.flatMap(item => item.keywords || []))];

  // Filter content based on selected keywords
  const filteredContent = selectedKeywords.length > 0
    ? content.filter(item => item.keywords && item.keywords.some(kw => selectedKeywords.includes(kw)))
    : content;

  return (
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Title level={2} style={{ marginBottom: "1rem" }}>
            Semantic Search Results
          </Title>
          <Paragraph>
            Viewing results for: <Text code>{filename}</Text>
          </Paragraph>
        </Col>

        <Col span={24}>
          <div style={{ marginBottom: "1rem" }}>
            <Text strong>Filter by Keywords:</Text>
            <Select
              mode="multiple"
              allowClear
              style={{ width: "100%" }}
              placeholder="Select keywords to filter"
              onChange={setSelectedKeywords}
            >
              {allKeywords.map((keyword, index) => (
                <Option key={index} value={keyword}>
                  {keyword}
                </Option>
              ))}
            </Select>
          </div>
        </Col>

        <Col span={24}>
          {loading ? (
            <Spin size="large" style={{ marginTop: "2rem", display: "flex", justifyContent: "center" }} />
          ) : (
            <List
              itemLayout="vertical"
              dataSource={filteredContent}
              renderItem={(item) => (
                <List.Item>
                  <DocumentResultItem item={item} />
                </List.Item>
              )}
            />
          )}
        </Col>
      </Row>
    </div>
  );
}

export default DocResults;
