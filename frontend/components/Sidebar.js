import React from "react";
import styles from "./styles/Sidebar.module.css";
import ThemeToggle from "./ThemeToggle";
import AudioPlayer from "./AudioPlayer";

export default function Sidebar({ isDocked, onToggleDock, onNavigate, soundEnabled, setSoundEnabled }) {
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

      <div className={styles.sidebarFooter}>
        <div className={styles.controlsSection}>
          {!isDocked && <div className={styles.settingsDivider}></div>}
          {!isDocked && <h5 className={styles.controlsTitle}>Settings</h5>}
          
          <div className={styles.controlItem}>
            <span className={styles.controlIcon}>🎨</span>
            {!isDocked && (
              <div className={styles.controlContent}>
                <ThemeToggle showNameOnly={true} />
              </div>
            )}
          </div>

          <div className={styles.controlItem}>
            <span className={styles.controlIcon}>🔊</span>
            {!isDocked && (
              <div className={styles.controlContent}>
                <span className={styles.controlLabel}>Sound</span>
                <AudioPlayer
                  soundEnabled={soundEnabled}
                  setSoundEnabled={setSoundEnabled}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
