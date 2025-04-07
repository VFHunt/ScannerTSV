import React from "react";
import KeywordSearch from "./components/KeywordSearch";
import FileUpload from "./components/FileUpload";
import LogoViewer from "./components/logoTSV"; // Import the LogoViewer component
import Main from "./pages/MainPage"; // Import the MainPage component

function App() {
  return (
    <div style={styles.container}>
      <div style={styles.logo}>
        <LogoViewer />
      </div>
      <h1 style={styles.header}>Scanner TSV</h1>
      <div style={styles.content}>
      </div>
      <div style={styles.main}>
        <Main />
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
    maxWidth: "100vw", // Full viewport width
    textAlign: "center",
    padding: "20px",
    boxSizing: "border-box",
    position: "relative", // Allow absolute positioning for the logo
    overflow: "hidden", // Prevent overflow of content
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
    maxWidth: "100", // Limit the width of the content
  },

  main: {
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-start",
    maxWidth: "100%",
    backgroundColor: "#f9f9f9",
  },
};

export default App;

// import React from "react";
// import MainPage from "./pages/MainPage"; // Import the MainPage component
// import LeftBarPage from "./pages/LeftbarPage"; // Import the LeftBarPage component
// import "./styles/App.css"; // Import the CSS file

// function App() {
//   return (
//     <div className="container">
//       <div className="content">
//         <div className="leftBar">
//           <LeftBarPage />
//         </div>
//         <div className="mainPage">
//           <MainPage />
//         </div>
//       </div>
//     </div>
//   );
// }

// export default App;a