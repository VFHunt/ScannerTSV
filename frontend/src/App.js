import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import NewScan from "./pages/NewScan";
import ProjectView from "./pages/ProjectView";
import Results from "./pages/Results";
import DocResults from "./pages/DocResults";
import MainLayout from "./pages/MainLayout";
import 'antd/dist/reset.css';
import "./styles/App.css";

function App() {
  return (
    <Router>      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        {/* Main Layout with nested routes */}
        <Route path="/" element={<MainLayout />}>
          <Route index element={<LoginPage />} />
          <Route path="newscan" element={<NewScan />} />
          <Route path="projectview" element={<ProjectView />} />
          <Route path="results/:projectName" element={<Results />} />
          <Route path="docresults/:filename" element={<DocResults />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
