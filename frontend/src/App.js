qqqimport React from "react";
import KeywordSearch from "./components/KeywordSearch";
import FileUpload from "./components/FileUpload";

function App() {
  return (
    <div>
      <h1>Pinecone Search & File Upload</h1>
      <FileUpload />
      <KeywordSearch />
    </div>
  );
}

export default App;
