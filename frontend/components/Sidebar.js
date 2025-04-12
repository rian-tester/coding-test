import React from "react";

export default function Sidebar({ isDocked, onToggleDock, onNavigate }) {
  return (
    <div className={`sidebar ${isDocked ? "docked" : ""}`}>
      <button className="toggle-button" onClick={onToggleDock}>
        {isDocked ? ">" : "<"}
      </button>
      {!isDocked && (
        <ul>
          <li onClick={() => onNavigate("dummy-data")}>Dummy Data</li>
          <li onClick={() => onNavigate("ai-section")}>AI Section</li>
        </ul>
      )}
    </div>
  );
}