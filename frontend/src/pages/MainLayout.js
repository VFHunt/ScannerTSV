import React, { useEffect } from "react";
import { Layout, Button } from "antd";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { ArrowLeftOutlined } from "@ant-design/icons";
import Sidebar from "./Sidebar";

const { Sider, Content } = Layout;

function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const timer = setTimeout(() => {
      console.log("Timer running...");
    }, 1000);

    return () => {
      clearTimeout(timer);
    };
  }, []);

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
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(-1)}
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
