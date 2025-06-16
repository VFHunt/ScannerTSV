import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/LoginPage.css";
import { loginUser } from "../utils/api";

function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

const handleLogin = async () => {
  const result = await loginUser(username, password);
  if (result.success) {
    navigate("/projectview", { replace: true });
  } else {
    alert(result.message);
  }
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