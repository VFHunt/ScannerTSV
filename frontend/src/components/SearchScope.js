import React from "react";

const SearchScope = ({ scope, setScope }) => {
  return (
    <div
      className="searchScopeRow"
      style={{
        marginBottom: "1rem",
        display: "flex",
        alignItems: "center",
      }}
    >
      <label
        className="label"
        style={{
          marginRight: "10px",
          fontWeight: "bold",
        }}
      >
        Zoekbereik:
      </label>
      <div style={{ display: "flex", gap: "20px" }}>
        <div>
          <input
            type="radio"
            id="focused"
            name="searchScope"
            value="focused"
            checked={scope === "focused"}
            onChange={(e) => setScope(e.target.value)}
          />
          <label htmlFor="focused" style={{ marginLeft: "5px" }}>
            Focus
          </label>
        </div>

        <div>
          <input
            type="radio"
            id="balanced"
            name="searchScope"
            value="balanced"
            checked={scope === "balanced"}
            onChange={(e) => setScope(e.target.value)}
          />
          <label htmlFor="balanced" style={{ marginLeft: "5px" }}>
            Gebalanceerd
          </label>
        </div>

        <div>
          <input
            type="radio"
            id="broad"
            name="searchScope"
            value="broad"
            checked={scope === "broad"}
            onChange={(e) => setScope(e.target.value)}
          />
          <label htmlFor="broad" style={{ marginLeft: "5px" }}>
            Breed
          </label>
        </div>
      </div>
    </div>
  );
};

export default SearchScope;