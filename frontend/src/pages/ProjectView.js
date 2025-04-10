import React, { useState, useEffect } from "react";
import { Table, Button, Input, Space, Layout, message } from "antd";
import { PlusOutlined, ReloadOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { get_projects } from "../utils/api"; // Import the function to fetch projects

const { Content } = Layout;

function ProjectView() {
  const [projects, setProjects] = useState([]); // State for project data
  const [filteredProjects, setFilteredProjects] = useState([]); // State for filtered projects
  const [searchTerm, setSearchTerm] = useState(""); // State for search input
  const navigate = useNavigate();

  // Fetch projects from the backend
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await get_projects(); // Call the backend function
        setProjects(data);
        setFilteredProjects(data); // Initialize filtered projects
      } catch (error) {
        console.error("Error fetching projects:", error);
        message.error("Failed to fetch projects.");
      }
    };

    fetchProjects();
  }, []);

  // Handle search functionality
  const handleSearch = () => {
    const filtered = projects.filter((project) =>
      project.projectName.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredProjects(filtered);
  };

  // Handle reset functionality
  const handleReset = () => {
    setSearchTerm("");
    setFilteredProjects(projects); // Reset to the original project list
  };

  // Handle creating a new project
  const handleNewProject = async () => {
    try {
      // const newProject = await create_new_project(); // Call the API to create a new project
      message.success("Creating new project!");
      navigate("/newscan"); // Navigate to the NewScan page
    } catch (error) {
      console.error("Error creating new project:", error);
      message.error("Failed to create a new project.");
    }
  };

  // Define table columns
  const columns = [
    {
      title: "Projectnaam",
      dataIndex: "projectName",
      key: "projectName",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
    },
    {
      title: "Datum aangemaakt",
      dataIndex: "createdDate",
      key: "createdDate",
    },
    {
      title: "Actie",
      key: "action",
      render: (_, record) => (
        <Space size="middle">
          <Button type="link" onClick={() => console.log("View", record)}>
            View
          </Button>
          <Button type="link" danger onClick={() => console.log("Delete", record)}>
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Layout style={{ minHeight: "100vh", padding: "20px", backgroundColor: "#f0f2f5" }}>
      <Content style={{ maxWidth: "1200px", margin: "0 auto", width: "100%" }}>
        <h1 style={{ marginBottom: "20px" }}>AI SmartScanner</h1>

        {/* Search Bar */}
        <Space style={{ marginBottom: "20px", width: "100%" }} align="center">
          <Input
            placeholder="Projectnaam"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: "300px" }}
          />
          <Button onClick={handleReset}>Reset</Button>
          <Button type="primary" onClick={handleSearch}>
            Search
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleNewProject} // Navigate to NewScan
            style={{ marginLeft: "auto" }}
          >
            Nieuw Project
          </Button>
          <Button icon={<ReloadOutlined />} onClick={() => window.location.reload()} />
        </Space>

        {/* Projects Table */}
        <Table
          columns={columns}
          dataSource={filteredProjects}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
        />
      </Content>
    </Layout>
  );
}

export default ProjectView;