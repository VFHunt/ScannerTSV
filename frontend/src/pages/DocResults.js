import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { List, Tag, Spin, Tooltip, Card, Typography, Row, Col, Select } from "antd";
import { fetchDocumentResults } from "../utils/api";

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

const getColorFromDistance = (distance) => {
    if (distance >= 0.4 && distance < 0.5) return "#a8e6cf"; // greenish
    if (distance >= 0.5 && distance < 0.7) return "#ffd3b6"; // orangeish
    if (distance >= 0.7 && distance <= 1) return "#ff8b94"; // reddish
  };


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
        <Paragraph ellipsis={{ rows: 4, expandable: true, symbol: "meer" }} style={{ fontSize: "15px" }}>
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
            {(item.keywords || []).map(([ word, distance ], i) => (
              <Tag
                color={getColorFromDistance(distance)}
                key={i}
                style={{
                  marginBottom: "0.25rem",
                  whiteSpace: "normal",
                  wordBreak: "break-word",
                  border: "none",
                  color: "#000",
                }}
              >
                {word}
              </Tag>
            ))}
          </div>
          <Tooltip title="Paginanummer" placement="top" mouseEnterDelay={0.2}>
            <Tag
              color="gold"
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "0 0.6rem",
                height: "22px",
                fontSize: "12px",
                fontWeight: 500,
                borderRadius: "1px",
                lineHeight: 1,
                whiteSpace: "nowrap",
                cursor: "default",
              }}
              role="contentinfo"
              aria-label={`Pagina ${item.page}`}
            >
              Pagina {item.page}
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
      console.error("Fout bij het ophalen van documentresultaten:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocumentResultsHandler();
  }, [filename]);

  // Extract unique keywords for filtering
   const allKeywords = [...new Set(
    content.flatMap(item => (item.keywords || []).map(([word]) => word))
  )];


  // Filter content based on selected keywords
  const filteredContent = selectedKeywords.length > 0
    ? content.filter(item => {
        const kwList = (item.keywords || []).map(([word]) => word);
        return kwList.some(kw => selectedKeywords.includes(kw));
      })
    : content;

  return (
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Title level={2} style={{ marginBottom: "1rem" }}>
            Semantische zoekresultaten
          </Title>
          <Paragraph>
            Resultaten voor: <Text code>{filename}</Text>
          </Paragraph>
        </Col>

        <Col span={24}>
          <div style={{ marginBottom: "1rem" }}>
            <Text strong>Filter op trefwoorden:</Text>
            <Select
              mode="multiple"
              allowClear
              style={{ width: "100%" }}
              placeholder="Selecteer trefwoorden om te filteren"
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
          {/* Legend for distance colors */}
          <div style={{ margin: "16px 0" }}>
            <span style={{ marginRight: 16, display: "inline-flex", alignItems: "center" }}>
              <span style={{
                display: "inline-block",
                width: 18,
                height: 18,
                background: "#a8e6cf",
                borderRadius: 4,
                border: "1px solid #ccc",
                marginRight: 6,
                verticalAlign: "middle"
              }} />
              Breed
            </span>
            <span style={{ marginRight: 16, display: "inline-flex", alignItems: "center" }}>
              <span style={{
                display: "inline-block",
                width: 18,
                height: 18,
                background: "#ffd3b6",
                borderRadius: 4,
                border: "1px solid #ccc",
                marginRight: 6,
                verticalAlign: "middle"
              }} />
              Gebalanceerd
            </span>
            <span style={{ display: "inline-flex", alignItems: "center" }}>
              <span style={{
                display: "inline-block",
                width: 18,
                height: 18,
                background: "#ff8b94",
                borderRadius: 4,
                border: "1px solid #ccc",
                marginRight: 6,
                verticalAlign: "middle"
              }} />
              Focus
            </span>
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
