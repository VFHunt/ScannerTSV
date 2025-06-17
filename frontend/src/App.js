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
        {/* Login page as standalone full-screen route */}
        <Route path="/" element={<LoginPage />} />
        
        {/* All other pages under MainLayout */}
        <Route element={<MainLayout />}>
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
