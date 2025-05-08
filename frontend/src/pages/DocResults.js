import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { List, Tag, Button, message } from "antd";
import { fetchDocumentResults } from "../utils/api"; // Import the API function

function DocResults() {
  const { filename } = useParams(); // Get the filename from the URL
  const [content, setContent] = useState([]); // State to store text splits and keywords
  const [loading, setLoading] = useState(false); // State for loading indicator

  // Function to fetch text splits and keywords from the backend
  const fetchDocumentResultsHandler = async () => {
    setLoading(true);
    try {
      const data = await fetchDocumentResults(filename); // Call the imported function
      setContent(data.results || []); // Set the content from the backend response
    } catch (error) {
      message.error("Failed to fetch document results");
      console.error("Error fetching document results:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocumentResultsHandler(); // Fetch data when the component loads
  }, [filename]);

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Document Results</h1>
      <p>Viewing results for: <strong>{filename}</strong></p>
      <List
        dataSource={content}
        renderItem={(item) => (
          <List.Item style={{ padding: "1rem 0", borderBottom: "1px solid #f0f0f0" }}>
            <div>
              <p>{item.text}</p> {/* Display the text split */}
              <div style={{ marginBottom: "0.5rem" }}>
                {item.keywords.map((keyword, index) => (
                  <Tag color="geekblue" key={index}>
                    {keyword}
                  </Tag>
                ))}
              </div>
              <Tag color="gray">Page {item.page}</Tag> {/* Display the page number */}
            </div>
          </List.Item>
        )}
        loading={loading}
      />
    </div>
  );
}

export default DocResults;