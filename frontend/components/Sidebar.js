import React from "react";
import styles from "./styles/Sidebar.module.css";

export default function Sidebar({ isDocked, onToggleDock, onNavigate }) {
  const menuItems = [
    { key: "dummy-data", icon: "📊", label: "Sales Dashboard", shortLabel: "Sales" },
    { key: "ai-section", icon: "🤖", label: "AI Assistant", shortLabel: "AI" }
  ];

  return (
    <div className={`${styles.sidebar} ${isDocked ? styles.docked : ""}`}>
      <div className={styles.sidebarHeader}>
        <button className={styles.toggleButton} onClick={onToggleDock}>
          {isDocked ? "📋" : "◀"}
        </button>
      </div>
      
      <nav className={styles.navigation}>
        {menuItems.map((item) => (
          <button
            key={item.key}
            className={styles.navItem}
            onClick={() => onNavigate(item.key)}
            title={item.label}
          >
            <span className={styles.navIcon}>{item.icon}</span>
            {!isDocked && (
              <span className={styles.navLabel}>{item.label}</span>
            )}
          </button>
        ))}
      </nav>
    </div>
  );
}
