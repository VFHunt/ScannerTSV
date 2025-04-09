import React, { useState } from "react";
import { getSynonyms, searchKeywords } from "../utils/api"; // Import the APIs
import "../styles/KeywordSearch.css";

function KeywordSearch() {
  const [keyword, setKeyword] = useState("");
  const [keywordsList, setKeywordsList] = useState([]);
  const [synonymsList, setSynonymsList] = useState([]);
  const [message, setMessage] = useState("");

  const addKeyword = () => {
    if (keyword && !keywordsList.includes(keyword)) {
      setKeywordsList([...keywordsList, keyword]);
      setKeyword("");
    }
  };

  const removeKeyword = (keywordToRemove) => {
    setKeywordsList(keywordsList.filter((kw) => kw !== keywordToRemove));
  };

  const removeSynonym = (synonymToRemove) => {
    setSynonymsList(synonymsList.filter((syn) => syn !== synonymToRemove));
  };

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
      setMessage(`Error in Synonym Generation: ${error.response?.data?.error || error.message}`);
    }
  };

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
    <div className="keywordSearchContainer">

      {/* Input Row */}
      <div className="inputRow">
        <label className="label">Woordenlijst:</label>
        <input
          type="text"
          placeholder="Enter a keyword"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              addKeyword();
            }
          }}
          className="input"
        />
        <button onClick={addKeyword} className="addButton">
          Add
        </button>
      </div>

      {/* Keywords List */}
      <div className="keywordsRow">
        {keywordsList.map((kw, index) => (
          <div key={index} className="keyword">
            {kw}
            <button onClick={() => removeKeyword(kw)} className="deleteButton">
              ✖
            </button>
          </div>
        ))}
      </div>

      {/* Extra Words Button */}
      <div className="extraWordsRow">
        <button onClick={handleSynonymGeneration} className="extraWordsButton">
          Extra words
        </button>
      </div>

      {/* Synonyms List */}
      <div className="synonymsRow">
        {synonymsList.map((syn, index) => (
          <div key={index} className="synonym">
            {syn}
            <button
              onClick={() => removeSynonym(syn)}
              className="deleteButton"
            >
              ✖
            </button>
          </div>
        ))}
      </div>

      {/* Start Scan Button */}
      <div className="startScanRow">
        <button onClick={handleSearch} className="startScanButton">
          Start Scan
        </button>
      </div>

      {/* Message */}
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default KeywordSearch;