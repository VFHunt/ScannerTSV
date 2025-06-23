import React, { useState } from "react";
import { getSynonyms, searchKeywords, getProjectName } from "../utils/api";
import { useNavigate } from "react-router-dom";
import SearchScope from "./SearchScope"; // Import the new component
import "../styles/KeywordSearch.css";

function KeywordSearch() {
  const [keyword, setKeyword] = useState("");
  const [keywordsList, setKeywordsList] = useState([]);
  const [synonymsList, setSynonymsList] = useState([]);
  const [message, setMessage] = useState("");
  const [searchScope, setSearchScope] = useState("balanced"); // Default to "balanced"
  const navigate = useNavigate();

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
        setMessage("Geen trefwoorden beschikbaar om synoniemen te genereren.");
        return;
      }

      setMessage(`Synoniemen genereren voor: ${keywordsList.join(", ")}`);
      const data = await getSynonyms(keywordsList);
      setSynonymsList(data.synonyms || []);
      setMessage("Synoniemen succesvol gegenereerd!");
    } catch (error) {
      setMessage(
        `Fout bij het genereren van synoniemen: ${
          error.response?.data?.error || error.message
        }, zorg ervoor dat je één of meer bestanden hebt geüpload.`
      );
    }
  };

  const handleSearch = async () => {
    try {
      if (keywordsList.length === 0 && synonymsList.length === 0) {
        setMessage("Geen trefwoorden of synoniemen beschikbaar om te zoeken.");
        return;
      }

      setMessage("Zoeken...");
      const data = await searchKeywords([...keywordsList, ...synonymsList], searchScope); // Pass searchScope
      setMessage(data.message || "Zoekopdracht voltooid!");

      const projectName = await getProjectName();
      if (projectName) {
        navigate(`/results/${projectName}`);
      } else {
        setMessage("Fout: projectnaam niet gevonden.");
      }
    } catch (error) {
      setMessage(`Fout bij zoeken: ${error.response?.data?.error || error.message}`);
    }
  };

  return (
    <div className="keywordSearchContainer">
      {/* Input Row */}
      <div className="inputRow">
        <label className="label">Woordenlijst:</label>
        <input
          type="text"
          placeholder="Voer een trefwoord in"
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
          Toevoegen
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

      {/* Search Scope Toggle */}
      <SearchScope scope={searchScope} setScope={setSearchScope} />

      {/* Extra Words Button */}
      <div className="extraWordsRow">
        <button onClick={handleSynonymGeneration} className="extraWordsButton">
          Extra woorden
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
          Start scan
        </button>
      </div>

      {/* Message */}
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default KeywordSearch;