// src/components/MainLayout.js
import React from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar"; // Assuming NavBar is your sidebar

const layoutStyle = {
  display: "flex",
  width: "100vw",
  height: "100vh",
  backgroundColor: "#f4f4f4",
};

const contentWrapper = {
  flex: 1,
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  padding: "40px",
};

const contentBox = {
  width: "100%",
  maxWidth: "1000px",
  minHeight: "80vh",
  backgroundColor: "#fff",
  borderRadius: "16px",
  padding: "20px",
  boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
};

function MainLayout() {
  return (
    <div style={layoutStyle}>
      <Sidebar />
      <div style={contentWrapper}>
        <div style={contentBox}>
          <Outlet />
        </div>
      </div>
    </div>
  );
}

export default MainLayout;
