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
    console.log("Current Path:", location.pathname); // Debugging: Log the current path

    if (location.pathname === "/newscan") {
      console.log("Navigating from newscan to project view."); // Debugging: Log navigation action
      navigate("/projectview"); // From newscan, go to project view
      return;
    }

    if (location.pathname === "/projectview") {
      console.log("Already on project view. No further navigation."); // Debugging: Stay on project view
      return;
    }

    if (location.pathname === "/docresults") {
      console.log("Navigating from docresults to results."); // Debugging: Log navigation action
      navigate("/results"); // From docresults, go to results
      return;
    }

    if (location.pathname === "/results") {
      console.log("Navigating from results to project view."); // Debugging: Log navigation action
      navigate("/projectview"); // From results, go to project view
      return;
    }

    console.log("Unhandled path. Redirecting to project view."); // Debugging: Default case
    navigate("/projectview"); // Default to project view for any other case
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