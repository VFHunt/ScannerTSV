import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/ProjectView.css";

function ProjectView() {
  const navigate = useNavigate();

  const handleNewProject = () => {
    navigate("/newscan"); // Navigate to the NewScan page
  };

  return (
    <div className="projectViewContainer">
      <h1 className="header">AI SmartScanner</h1>

      {/* Search Bar */}
      <div className="searchRow">
        <label className="label">Projectnaam:</label>
        <input
          type="text"
          placeholder="Please enter"
          className="searchInput"
        />
        <button className="resetButton">Reset</button>
        <button className="searchButton">Search</button>
      </div>

      {/* Projects Table */}
      <div className="projectsTable">
        <div className="tableHeader">
          <span>Projecten</span>
          <button className="newProjectButton" onClick={handleNewProject}>
            + Nieuw Project
          </button>
        </div>
        <table>
          <thead>
            <tr>
              <th></th>
              <th>Projectnaam</th>
              <th>Status</th>
              <th>Datum aangemaakt</th>
              <th>Actie</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><input type="checkbox" /></td>
              <td>Project 1</td>
              <td>Scan gereed</td>
              <td>2021-02-05 08:28:36</td>
              <td>
                <button className="viewButton">View</button>
                <button className="deleteButton">Delete</button>
              </td>
            </tr>
            <tr>
              <td><input type="checkbox" /></td>
              <td>Project 2</td>
              <td>Scanning</td>
              <td>2021-02-03 19:49:33</td>
              <td>
                <button className="viewButton">View</button>
                <button className="deleteButton">Delete</button>
              </td>
            </tr>
            <tr>
              <td><input type="checkbox" /></td>
              <td>Project 3</td>
              <td>Scan gereed</td>
              <td>2021-02-02 19:17:15</td>
              <td>
                <button className="viewButton">View</button>
                <button className="deleteButton">Delete</button>
              </td>
            </tr>
            <tr>
              <td><input type="checkbox" /></td>
              <td>Project 4</td>
              <td>Scan gereed</td>
              <td>2021-02-02 09:46:33</td>
              <td>
                <button className="viewButton">View</button>
                <button className="deleteButton">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="pagination">
        <span>1-10 of 100 items</span>
        <div className="paginationControls">
          <button>{"<"}</button>
          <button>1</button>
          <button>...</button>
          <button>5</button>
          <button className="activePage">6</button>
          <button>7</button>
          <button>...</button>
          <button>50</button>
          <button>{">"}</button>
        </div>
      </div>
    </div>
  );
}

export default ProjectView;