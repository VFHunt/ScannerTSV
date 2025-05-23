import React, { useEffect } from "react";
import { Layout, Button } from "antd";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { ArrowLeftOutlined } from "@ant-design/icons"; // Import the back arrow icon
import Sidebar from "./Sidebar"; // Assuming Sidebar is your sidebar component

const { Sider, Content } = Layout;

function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation(); // Get the current location

  const handleBack = () => {
    if (window.history.state && window.history.state.idx > 0) {
      if (location.pathname === "/newscan" || location.pathname === "/projectview") {
        navigate("/projectview"); // Redirect to project view instead of navigating back to newscan
      } else {
        navigate(-1); // Navigate to the previous page
      }
    } else {
      navigate("/projectview"); // Default to project view if no history exists
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      console.log("Timer running...");
    }, 1000);

    return () => {
      clearTimeout(timer); // Cleanup the timer
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
            type="link"
            icon={<ArrowLeftOutlined />}
            onClick={handleBack}
            style={{ marginBottom: "20px" }}
          >
            Back
          </Button>

          <React.Fragment>
            <Outlet />
          </React.Fragment>
        </Content>
      </Layout>
    </Layout>
  );
}

export default MainLayout;