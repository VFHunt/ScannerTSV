import React, { useState, useEffect } from "react";
import { Table, Button, Input, Space, Layout, message, Modal, Form } from "antd";
import { PlusOutlined, ReloadOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import "../styles/ProjectView.css";
import { get_projects, setProjectName, reset_db, deleteProject } from "../utils/api"; // Import setProjectName

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
  const handleReset = async () => {
    Modal.confirm({
      title: 'Weet je het zeker?',
      content: 'Dit verwijdert alle projecten. Deze actie kan niet ongedaan worden gemaakt.',
      okText: 'Ja, verwijderen',
      okType: 'danger',
      cancelText: 'Annuleren',
      onOk: async () => {
        try {
          await reset_db();  // Call backend to reset
          setSearchTerm("");

          // Re-fetch projects after reset
          const data = await get_projects();
          setProjects(data || []);
          setFilteredProjects(data || []);

          message.success("Projecten zijn succesvol gereset.");
        } catch (error) {
          console.error("Failed to reset projects:", error);
          message.error("Failed to reset projects.");
        }
      },
    });
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

  const handleDeleteProject = async (projectName) => {
    Modal.confirm({
      title: `Project "${projectName}" verwijderen?`,
      content: "Deze actie kan niet ongedaan worden gemaakt.",
      okText: "Verwijderen",
      okType: "danger",
      cancelText: "Annuleren",
      onOk: async () => {
        try {
          await deleteProject(projectName);
          message.success(`Project '${projectName}' is succesvol verwijderd.`);
          // Vernieuw de projectlijst na verwijderen
          const data = await get_projects();
          setProjects(data || []);
          setFilteredProjects(data || []);
        } catch (error) {
          message.error("Verwijderen van het project is mislukt.");
          console.error(error);
        }
      },
    });
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


  // Update the columns definition
    const columns = [
    {
        title: "Projectnaam",
        dataIndex: "projectName",
        key: "projectName",
    },
    {
        title: "Status",
        dataIndex: "scanned",
        key: "scanned",
        render: (scanned) => (scanned ? "Geslaagd" : "Niet gescand"),
    },
    {
        title: "Datum Aangemaakt",
        dataIndex: "uploadDate",
        key: "uploadDate",
        render: (uploadDate) => {
          const date = new Date(uploadDate);
          return isNaN(date)
            ? "Onbekend"
            : date.toLocaleString("nl-NL", {
                day: "2-digit",
                month: "long",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              });
        },
    },
    {
        title: "Actie",
        key: "action",
        render: (_, record) => (
          <Space size="middle">
            <Button type="link" onClick={() => navigate(`/results/${record.projectName}`)}>
              Bekijk
            </Button>
            <Button type="link" danger onClick={() => handleDeleteProject(record.projectName)}>
              Verwijderen
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
          <Button onClick={handleReset}>Alle projecten verwijderen</Button>
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
          okText="Creëren"
          cancelText="Annuleren"
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
                placeholder="Voer projectnaam in"
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