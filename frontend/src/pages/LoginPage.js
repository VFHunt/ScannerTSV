import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/LoginPage.css";

function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = () => {
    // For simplicity, no authentication logic is implemented
    navigate("/projectview", {replace: true}); // Navigate to the ProjectView page
  };

  return (
    <div className="loginContainer">
      <h1 className="header">AI SmartScanner</h1>
      <p className="subHeader">Het interne platform voor AI tools</p>

      <div className="loginForm">
        <h2 className="formHeader">Login</h2>
        <div className="inputGroup">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="inputField"
          />
        </div>
        <div className="inputGroup">
          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="inputField"
          />
        </div>
        <div className="rememberMe">
          <input type="checkbox" id="rememberMe" />
          <label htmlFor="rememberMe">Remember me</label>
        </div>
        <button onClick={handleLogin} className="loginButton">
          Login
        </button>
      </div>
    </div>
  );
}

export default LoginPage;