import React from "react";
import KeywordSearch from "./components/KeywordSearch";
import FileUpload from "./components/FileUpload";
import LogoViewer from "./components/logo"; // Import the LogoViewer component

function App() {
  return (
    <div style={styles.container}>
      <div style={styles.logo}>
        <LogoViewer />
      </div>
      <h1 style={styles.header}>Scanner TSV</h1>
      <div style={styles.content}>
        <div style={styles.keywordSearch}>
          <KeywordSearch />
        </div>
        <div style={styles.fileUpload}>
          <FileUpload />
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100vh", // Full viewport height
    textAlign: "center",
    padding: "20px",
    boxSizing: "border-box",
    position: "relative", // Allow absolute positioning for the logo
  },
  logo: {
    position: "absolute",
    top: "20px",
    left: "20px",
  },
  header: {
    marginBottom: "20px",
    fontSize: "2rem",
    fontWeight: "bold",
  },
  content: {
    display: "flex",
    flexDirection: "column", // Stack components vertically
    gap: "20px", // Space between components
    width: "100%",
    maxWidth: "800px", // Limit the width of the content
  },
  keywordSearch: {
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-start",
    padding: "20px",
    border: "1px solid #ccc",
    borderRadius: "10px",
    backgroundColor: "#f9f9f9",
  },
  fileUpload: {
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-start",
    padding: "20px",
    border: "1px solid #ccc",
    borderRadius: "10px",
    backgroundColor: "#f9f9f9",
  },
};

export default App;