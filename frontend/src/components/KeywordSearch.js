import React, { useState } from "react";
import { getSynonyms, searchKeywords } from "../utils/api"; // Import the APIs

function KeywordSearch() {
  const [keyword, setKeyword] = useState("");
  const [keywordsList, setKeywordsList] = useState([]); // To store multiple keywords
  const [synonymsList, setSynonymsList] = useState([]); // To store synonyms
  const [message, setMessage] = useState("");

  // Function to add a keyword to the list
  const addKeyword = () => {
    if (keyword && !keywordsList.includes(keyword)) {
      setKeywordsList([...keywordsList, keyword]);
      setKeyword("");
    }
  };

  // Function to remove a keyword from the list
  const removeKeyword = (keywordToRemove) => {
    setKeywordsList(keywordsList.filter((kw) => kw !== keywordToRemove));
  };

  // Function to remove a synonym from the list
  const removeSynonym = (synonymToRemove) => {
    setSynonymsList(synonymsList.filter((syn) => syn !== synonymToRemove));
  };

  // Handle the synonym generation functionality
  const handleSynonymGeneration = async () => {
    try {
      if (keywordsList.length === 0) {
        setMessage("No keywords available to generate synonyms.");
        return;
      }

      setMessage(`Generating synonyms for: ${keywordsList.join(", ")}`);
      const data = await getSynonyms(keywordsList); // Fetch synonyms for all keywords in the list
      setSynonymsList(data.synonyms); // Assuming the API returns an array of synonyms
      setMessage("Synonyms generated successfully!");
    } catch (error) {
      setMessage(`Error in Synonym Generation: ${error.response?.data?.error || error.message}`);
    }
  };

  // Handle the search functionality
  const handleSearch = async () => {
    try {
      if (keywordsList.length === 0 && synonymsList.length === 0) {
        setMessage("No keywords or synonyms available to search.");
        return;
      }

      setMessage("Searching...");
      const data = await searchKeywords([...keywordsList, ...synonymsList]); // Combine keywords and synonyms
      setMessage(data.message || "Search completed!");
    } catch (error) {
      setMessage(`Error in Search: ${error.response?.data?.error || error.message}`);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.leftContainer}>
        <div style={styles.inputContainer}>
          <input
            type="text"
            placeholder="Enter a keyword"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                addKeyword(); // Call addKeyword when Enter is pressed
              }
            }}
            style={styles.input}
          />
          <button onClick={addKeyword} style={styles.addButton}>
            Add
          </button>
        </div>

        <div style={styles.keywordsContainer}>
          {keywordsList.map((kw, index) => (
            <div key={index} style={styles.keyword}>
              {kw}
              <button onClick={() => removeKeyword(kw)} style={styles.deleteButton}>
                ✖
              </button>
            </div>
          ))}
        </div>

        <button onClick={handleSynonymGeneration} style={styles.generateButton}>
          Generate Synonyms
        </button>

        <button onClick={handleSearch} style={styles.searchButton}>
          Search
        </button>
      </div>

      <div style={styles.synonymsContainer}>
        <h3>Synonyms:</h3>
        <ul>
          {synonymsList.map((syn, index) => (
            <li key={index} style={styles.synonym}>
              {syn}
              <button onClick={() => removeSynonym(syn)} style={styles.deleteButton}>
                ✖
              </button>
            </li>
          ))}
        </ul>
      </div>

      {message && <p style={styles.message}>{message}</p>}
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    padding: "20px",
  },
  leftContainer: {
    display: "flex",
    flexDirection: "column",
    flex: "2",
  },
  inputContainer: {
    display: "flex",
    alignItems: "center",
    marginBottom: "20px",
  },
  input: {
    padding: "10px",
    fontSize: "16px",
    borderRadius: "5px",
    border: "1px solid #ccc",
    marginRight: "10px",
    flex: "1",
  },
  addButton: {
    backgroundColor: "#007BFF",
    color: "white",
    border: "none",
    borderRadius: "5px",
    padding: "10px 15px",
    cursor: "pointer",
    fontSize: "16px",
  },
  generateButton: {
    backgroundColor: "#28a745",
    color: "white",
    border: "none",
    borderRadius: "5px",
    padding: "10px 15px",
    cursor: "pointer",
    fontSize: "16px",
    marginTop: "20px",
  },
  searchButton: {
    backgroundColor: "#ffc107",
    color: "white",
    border: "none",
    borderRadius: "5px",
    padding: "10px 15px",
    cursor: "pointer",
    fontSize: "16px",
    marginTop: "10px",
  },
  keywordsContainer: {
    display: "flex",
    flexWrap: "wrap",
    gap: "10px",
    marginTop: "10px",
  },
  keyword: {
    backgroundColor: "#f0f0f0",
    padding: "10px",
    borderRadius: "5px",
    display: "flex",
    alignItems: "center",
    gap: "5px",
  },
  deleteButton: {
    backgroundColor: "red",
    color: "white",
    border: "none",
    borderRadius: "50%",
    width: "20px",
    height: "20px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
  },
  synonymsContainer: {
    marginLeft: "20px",
    flex: "1",
  },
  synonym: {
    marginBottom: "10px",
    display: "flex",
    alignItems: "center",
    gap: "5px",
  },
  message: {
    marginTop: "20px",
    fontSize: "14px",
    color: "#333",
  },
};

export default KeywordSearch;