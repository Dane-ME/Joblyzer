import React from 'react';
import { useTheme } from './BackgroundComponent';
import './ThemeToggle.css';

const ThemeToggle: React.FC = () => {
    const { theme, toggleTheme } = useTheme();

    return (
        <label className="theme-toggle">
            <input
                type="checkbox"
                checked={theme === 'light'}
                onChange={toggleTheme}
                aria-label="Toggle theme"
            />
            <span className="slider">
                <span className="icon moon"></span>
                <span className="icon sun"></span>
            </span>
        </label>
    );
};

export default ThemeToggle;
