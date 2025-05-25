import React, { useState, useEffect } from "react";
import { Modal, Button, Select, Input, Radio, Space, List, Tag } from "antd";
import { 
  getSynonyms, 
  searchKeywords,
  searchKeywordsUnscanned,
  get_keywords // Add this import
} from "../utils/api";

const { Option } = Select;

const ScanPopup = ({ visible, onCancel, onStartScan, onRefresh }) => {
  const [woordenlijst, setWoordenlijst] = useState("handmatig");
  const [keyword, setKeyword] = useState("");
  const [keywordsList, setKeywordsList] = useState([]);
  const [synonymsList, setSynonymsList] = useState([]);
  const [documentSelectie, setDocumentSelectie] = useState("alles");
  const [message, setMessage] = useState("");

  // Keyword handling functions
  const addKeyword = () => {
    if (keyword && !keywordsList.includes(keyword)) {
      setKeywordsList([...keywordsList, keyword]);
      setKeyword("");
    }
  };

  const removeKeyword = (kw) => {
    setKeywordsList(keywordsList.filter((k) => k !== kw));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      addKeyword();
    }
  };

  // Synonym handling functions
  const handleSynonymGeneration = async () => {
    try {
          if (keywordsList.length === 0) {
            setMessage("No keywords available to generate synonyms.");
            return;
          }
    
          setMessage(`Generating synonyms for: ${keywordsList.join(", ")}`);
          const data = await getSynonyms(keywordsList); // Fetch synonyms for all keywords in the list
          setSynonymsList(data.synonyms || []); // Assuming the API returns an array of synonyms
          setMessage("Synonyms generated successfully!");
        } catch (error) {
          setMessage(`Error in Synonym Generation: ${error.response?.data?.error || error.message}, please make sure you uploaded one or more files.`);
        }
  };

  const removeSynonym = (syn) => {
    setSynonymsList(synonymsList.filter((s) => s !== syn));
  };

  const handleScan = async () => {
    try {
      const terms = [...keywordsList, ...synonymsList];
      const scanFunction = documentSelectie === "alles" ? searchKeywords : searchKeywordsUnscanned;
      
      const result = await scanFunction(terms);
      onStartScan(woordenlijst, documentSelectie, terms);
      onCancel();
      if (onRefresh) await onRefresh(); // Refresh results without full page reload
    } catch (error) {
      setMessage(`Error starting scan: ${error.message}`);
    }
  };

  // Add useEffect to fetch keywords when woordenlijst changes
  useEffect(() => {
    const fetchKeywords = async () => {
      if (woordenlijst === "previously_searched") {
        try {
          const previousKeywords = await get_keywords();
          setKeywordsList(previousKeywords);
          setSynonymsList([]); // Clear synonyms when switching to previous keywords
        } catch (error) {
          setMessage("Error fetching previous keywords");
        }
      } else {
        // Reset lists when switching to manual mode
        setKeywordsList([]);
        setSynonymsList([]);
      }
    };

    fetchKeywords();
  }, [woordenlijst]);

  // Update the Select onChange handler
  const handleWoordenlijstChange = (value) => {
    setWoordenlijst(value);
    setMessage(""); // Clear any existing messages
  };

  return (
    <Modal
      title="Nieuwe Scan"
      open={visible}
      onCancel={onCancel}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Cancel
        </Button>,
        <Button
          key="start"
          type="primary"
          onClick={handleScan}  // Updated to use handleScan
        >
          Start Scan
        </Button>,
      ]}
    >
      <div style={{ marginBottom: "1rem" }}>
        <label>Woordenlijst:</label>
        <Select
          value={woordenlijst}
          onChange={handleWoordenlijstChange}
          style={{ width: "100%" }}
        >
          <Option value="handmatig">Handmatig</Option>
          <Option value="previously_searched">Eerder gezocht</Option>
        </Select>
      </div>

      {woordenlijst === "handmatig" ? (
        <div style={{ marginBottom: "1rem" }}>
          <div style={{ marginBottom: "1rem" }}>
            <Input
              placeholder="Enter a keyword"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onPressEnter={addKeyword}
              style={{ width: "calc(100% - 88px)", marginRight: "8px" }}
            />
            <Button 
              type="primary"
              onClick={addKeyword}
            >
              Add
            </Button>
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <Space wrap>
              {keywordsList.map((kw, index) => (
                <Tag
                  key={index}
                  closable
                  onClose={() => removeKeyword(kw)}
                >
                  {kw}
                </Tag>
              ))}
            </Space>
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <Button 
              type="primary"
              onClick={handleSynonymGeneration}
            >
              Extra words
            </Button>
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <Space wrap>
              {synonymsList.map((syn, index) => (
                <Tag
                  key={index}
                  closable
                  onClose={() => removeSynonym(syn)}
                >
                  {syn}
                </Tag>
              ))}
            </Space>
          </div>

          {message && <div style={{ marginBottom: "1rem" }}>{message}</div>}
        </div>
      ) : (
        <div style={{ marginBottom: "1rem" }}>
          <List
            dataSource={keywordsList}
            renderItem={(term) => (
              <List.Item>
                <Tag closable onClose={() => removeKeyword(term)}>
                  {term}
                </Tag>
              </List.Item>
            )}
          />
        </div>
      )}

      <div>
        <label>Document Selectie:</label>
        <Radio.Group
          onChange={(e) => setDocumentSelectie(e.target.value)}
          value={documentSelectie}
        >
          <Space direction="vertical">
            <Radio value="alles">Alles</Radio>
            <Radio value="alleen_nieuwe_bestanden">Alleen nieuwe bestanden</Radio>
          </Space>
        </Radio.Group>
      </div>
    </Modal>
  );
};

export default ScanPopup;