import React, { useState, useEffect } from "react";
import { Table, Button, Input, Space, Layout, message, Modal, Form } from "antd";
import { PlusOutlined, ReloadOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import "../styles/ProjectView.css";
import { get_projects, setProjectName } from "../utils/api"; // Import setProjectName

const { Content } = Layout;

function ProjectView() {
  const [projects, setProjects] = useState([]); // State for project data
  const [filteredProjects, setFilteredProjects] = useState([]); // State for filtered projects
  const [searchTerm, setSearchTerm] = useState(""); // State for search input
  const [isModalVisible, setIsModalVisible] = useState(false); // State for modal visibility
  const [newProjectName, setNewProjectName] = useState(""); // State for new project name
  const navigate = useNavigate();


  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await get_projects(); // Call the backend function
        console.log("Fetched projects:", data); // Debugging output
        setProjects(data || []); // Ensure data is an array
        setFilteredProjects(data || []); // Initialize filtered projects
      } catch (error) {
        console.error("Error fetching projects:", error);
        message.error("No projects have beeen created yet");
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
      setIsModalVisible(true); // Show the modal
    } catch (error) {
      console.error("Error preparing for new project:", error);
      message.error("Failed to prepare for a new project.");
    }
  };

  // Handle modal submission
  const handleModalOk = async () => {
    if (!newProjectName.trim()) {
      message.error("Project name cannot be empty.");
      return;
    }

    // Check if the project name already exists
    const isDuplicate = projects.some(
      (project) => project.projectName.toLowerCase() === newProjectName.toLowerCase()
    );

    if (isDuplicate) {
      message.error("A project with this name already exists. Please choose a different name.");
      return;
    }

    try {
      await setProjectName(newProjectName); // Call the API to set the project name
      message.success("Project created successfully!");
      setIsModalVisible(false); // Close the modal
      setNewProjectName(""); // Reset the input field
      navigate("/newscan"); // Navigate to the new scan page
    } catch (error) {
      console.error("Error creating project:", error);
      message.error("Failed to create the project.");
    }
  };

  // Handle modal cancellation
  const handleModalCancel = () => {
    setIsModalVisible(false); // Close the modal
    setNewProjectName(""); // Reset the input field
  };

  // Define table columns
  const columns = [
    {
      title: "Projectnaam",
      dataIndex: "projectName",
      key: "projectName",
    },
    {
      title: "Actie",
      key: "action",
      render: (_, record) => (
        <Space size="middle">
          <Button type="link" onClick={() => navigate(`/results/${record.projectName}`)}> {/* Pass the project name */}
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
            onChange={(e) => {
              const value = e.target.value;
              setSearchTerm(value);
              const filtered = projects.filter((project) =>
                project.projectName.toLowerCase().includes(value.toLowerCase())
              );
              setFilteredProjects(filtered);
            }}
            style={{ width: "300px" }}
          />
          <Button onClick={handleReset}>Reset</Button>
          <Button type="primary" onClick={handleSearch}>
            Search
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleNewProject} // Show modal for new project
            style={{ marginLeft: "auto" }}
          >
            Nieuw Project
          </Button>
          <Button icon={<ReloadOutlined />} onClick={() => window.location.reload()} />
        </Space>

        {/* Projects Table */}
        <Table
          columns={columns}
          dataSource={filteredProjects || []} // Fallback to an empty array
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
        />

        {/* Modal for New Project */}
        <Modal
          title="Nieuw Project"
          visible={isModalVisible}
          onOk={handleModalOk}
          onCancel={handleModalCancel}
          okText="Create"
          cancelText="Cancel"
        >
          <Form>
            <Form.Item label="Projectnaam" required>
              <Input
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    handleModalOk(); // Trigger modal submission on Enter key press
                  }
                }}
                placeholder="Enter project name"
                autoFocus // Automatically focus the input field when the modal opens
              />
            </Form.Item>
          </Form>
        </Modal>
      </Content>
    </Layout>
  );
}

export default ProjectView;