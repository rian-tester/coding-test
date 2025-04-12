import React from "react";

export default function Sidebar({ onNavigate }) {
  return (
    <div className="sidebar">
      <ul>
        <li onClick={() => onNavigate("dummy-data")}>Dummy Data</li>
        <li onClick={() => onNavigate("ai-section")}>AI Section</li>
      </ul>
    </div>
  );
}