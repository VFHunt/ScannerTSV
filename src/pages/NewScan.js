import React from "react";
import { Layout, Typography, Space } from "antd";
import KeywordSearch from "../components/KeywordSearch";
import FileUpload from "../components/FileUpload";

const { Content } = Layout;
const { Title } = Typography;

const NewScan = () => {
  return (
    <Layout style={{ minHeight: "100vh", padding: "40px", backgroundColor: "#f0f2f5" }}>
      <Content style={{ maxWidth: "800px", margin: "0 auto", width: "100%" }}>
        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          {/* SmartScan Section */}
          <div>
            <Title level={3} style={{ marginBottom: "20px" }}>
              SmartScan
            </Title>
            <KeywordSearch />
          </div>

          {/* File Upload Section */}
          <div>
            <Title level={3} style={{ marginBottom: "20px" }}>
              Bestanden
            </Title>
            <FileUpload />
          </div>
        </Space>
      </Content>
    </Layout>
  );
};

export default NewScan;