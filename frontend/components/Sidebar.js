import React from "react";
import styles from "./styles/Sidebar.module.css";

export default function Sidebar({ isDocked, onToggleDock, onNavigate }) {
  return (
    <div className={`${styles.sidebar} ${isDocked ? styles.docked : ""}`}>
      <button className={styles["toggle-button"]} onClick={onToggleDock}>
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