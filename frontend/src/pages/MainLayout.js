import React from "react";
import { Layout } from "antd";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import BackButton from "../components/BackButton";

const { Sider, Content } = Layout;

// Wrapper component to handle route transitions
const RouteContent = ({ children }) => {
  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {children}
    </div>
  );
};

function MainLayout() {
  const location = useLocation();
  const showBackButton = location.pathname !== "/" && location.pathname !== "/login"; // Hide on home and login pages

  return (
    <Layout style={{ height: "100vh" }}>
      {/* Sidebar */}
      <Sider
        width={250}
        style={{
          backgroundColor: "#f0f2f5",
          boxShadow: "2px 0 5px rgba(0, 0, 0, 0.1)",
        }}
      >
        <Sidebar />
      </Sider>      {/* Main Content */}
      <Layout>
        <Content
          style={{
            display: 'flex',
            flexDirection: 'column',
            padding: '0',
            backgroundColor: 'transparent'
          }}
        >          <RouteContent>
            {showBackButton && <BackButton />}
            <div
              style={{
                margin: "40px",
                padding: "20px",
                backgroundColor: "#fff",
                borderRadius: "16px",
                boxShadow: "0 4px 20px rgba(0, 0, 0, 0.1)",
                overflow: "auto",
                flex: 1,
              }}
            >
              <Outlet />
            </div>
          </RouteContent>
        </Content>
      </Layout>
    </Layout>
  );
}

export default MainLayout;
