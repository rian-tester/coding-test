import { useTheme } from '../contexts/ThemeContext';
import styles from './styles/ThemeToggle.module.css';

const ThemeToggle = () => {
  const { currentTheme, toggleTheme, theme } = useTheme();

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
