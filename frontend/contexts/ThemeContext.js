import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

const themes = {
  gaia: {
    name: 'Gaia Elegance',
    background: '#F4F4F9',
    primaryAccent: '#506680',
    secondaryAccent: '#8FA8C8',
    highlight: '#DAA49A',
    textMain: '#2E2E2E',
    textMuted: '#6E6E6E'
  },
  shinra: {
    name: 'Shinra Executive',
    background: '#F2F5F7',
    primaryAccent: '#1F2A44',
    secondaryAccent: '#6C7A89',
    highlight: '#B1A7F2',
    textMain: '#1C1C1C',
    textMuted: '#5E5E5E'
  }
};

export const ThemeProvider = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState('gaia');

  useEffect(() => {
    const savedTheme = localStorage.getItem('selectedTheme');
    if (savedTheme && themes[savedTheme]) {
      setCurrentTheme(savedTheme);
    }
  }, []);

  useEffect(() => {
    const theme = themes[currentTheme];
    const root = document.documentElement;
    
    root.style.setProperty('--bg-color', theme.background);
    root.style.setProperty('--primary-accent', theme.primaryAccent);
    root.style.setProperty('--secondary-accent', theme.secondaryAccent);
    root.style.setProperty('--highlight-color', theme.highlight);
    root.style.setProperty('--text-main', theme.textMain);
    root.style.setProperty('--text-muted', theme.textMuted);
    
    localStorage.setItem('selectedTheme', currentTheme);
  }, [currentTheme]);

  const toggleTheme = () => {
    setCurrentTheme(prev => prev === 'gaia' ? 'shinra' : 'gaia');
  };

  const value = {
    currentTheme,
    theme: themes[currentTheme],
    toggleTheme,
    themes
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};
