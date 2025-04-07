import React from "react";
import { Link } from "react-router-dom";
import LogoTSV from "../components/logoTSV"; // Import the logo component
import "../styles/SideBar.css"; // Import the CSS for styling

function Sidebar() {
  return (
    <div className="sidebarContainer">
      {/* Logo */}
      <div className="logoContainer">
        <LogoTSV />
      </div>

      {/* AI Smart Scanner Link */}
      <Link to="/projectview" className="sidebarLink aiSmartScanner">
        <span className="icon">💡</span> AI Smart Scanner
      </Link>

      {/* Settings Section */}
      <div className="settingsSection">
        <button className="settingsButton">Settings</button>
        <div className="settingsSubMenu">
          <button className="subMenuButton">User Management</button>
          <button className="subMenuButton">Cost Management</button>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;