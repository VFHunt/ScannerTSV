import React, { useState } from "react";
import { searchKeywords } from "../utils/api";

function KeywordSearch() {
  const [keyword, setKeyword] = useState("");
  const [message, setMessage] = useState("");

  const handleSearch = async () => {
    try {
      const data = await searchKeywords(keyword);
      setMessage(data.message);
    } catch (error) {
      setMessage(`Error in KeywordSearch: ${error.response?.data?.error || error.message}`);
    }
  };

  return (
    <div>
      <h2>Search in Pinecone</h2>
      <input
        type="text"
        placeholder="Enter a keyword"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
      />
      <button onClick={handleSearch}>Search</button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default KeywordSearch;