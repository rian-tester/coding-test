import { useTheme } from '../contexts/ThemeContext';
import styles from './styles/ThemeToggle.module.css';

const ThemeToggle = ({ showNameOnly = false }) => {
  const { currentTheme, toggleTheme, theme } = useTheme();

  if (showNameOnly) {
    return (
      <div className={styles.themeToggleInline}>
        <span className={styles.themeNameOnly}>{theme.name}</span>
        <button 
          onClick={toggleTheme}
          className={styles.toggleButtonInline}
          aria-label={`Switch to ${currentTheme === 'gaia' ? 'Shinra Executive' : 'Gaia Elegance'} theme`}
        >
          <div className={styles.toggleTrackInline}>
            <div className={`${styles.toggleThumbInline} ${currentTheme === 'shinra' ? styles.activeInline : ''}`}>
              <span className={styles.toggleIconInline}>
                {currentTheme === 'gaia' ? '🌸' : '⚡'}
              </span>
            </div>
          </div>
        </button>
      </div>
    );
  }

  return (
    <div className={styles.themeToggle}>
      <button 
        onClick={toggleTheme}
        className={styles.toggleButton}
        aria-label={`Switch to ${currentTheme === 'gaia' ? 'Shinra Executive' : 'Gaia Elegance'} theme`}
      >
        <div className={styles.toggleTrack}>
          <div className={`${styles.toggleThumb} ${currentTheme === 'shinra' ? styles.active : ''}`}>
            <span className={styles.toggleIcon}>
              {currentTheme === 'gaia' ? '🌸' : '⚡'}
            </span>
          </div>
        </div>
      </button>
      <span className={styles.themeLabel}>{theme.name}</span>
    </div>
  );
};

export default ThemeToggle;
