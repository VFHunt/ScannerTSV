import React from "react";
import { Layout, Button } from "antd";
import { Outlet, useNavigate } from "react-router-dom";
import { ArrowLeftOutlined } from "@ant-design/icons"; // Import the back arrow icon
import Sidebar from "./Sidebar"; // Assuming Sidebar is your sidebar component

const { Sider, Content } = Layout;

function MainLayout() {
  const navigate = useNavigate();

  const handleBack = () => {
    if (window.history.length > 1) {
      navigate("/projectview"); // Navigate to the previous page if history exists
    } 
  };

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
      </Sider>

      {/* Main Content */}
      <Layout>
        <Content
          style={{
            margin: "40px",
            padding: "20px",
            backgroundColor: "#fff",
            borderRadius: "16px",
            boxShadow: "0 4px 20px rgba(0, 0, 0, 0.1)",
          }}
        >
          {/* Back Button */}
          <Button
            type="link"
            icon={<ArrowLeftOutlined />}
            onClick={handleBack}
            style={{ marginBottom: "20px" }}
          >
            Back
          </Button>

          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}

export default MainLayout;