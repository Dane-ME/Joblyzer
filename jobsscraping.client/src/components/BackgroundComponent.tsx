import React, { useState, useEffect, createContext, useContext } from 'react';
import './Background.css';

type Theme = 'light' | 'dark';

interface ThemeContextType {
    theme: Theme;
    toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [theme, setTheme] = useState<Theme>('dark');
    const toggleTheme = () => {
        setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
    };
    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};

interface Star {
    id: number;
    x: number;
    y: number;
    size: number;
    opacity: number;
    speed: number;
}

interface Planet {
    id: number;
    x: number;
    y: number;
    size: number;
    color: string;
}

interface LightParticle {
    id: number;
    x: number;
    y: number;
    size: number;
}

const Background: React.FC = () => {
    const { theme } = useTheme();
    const [stars, setStars] = useState<Star[]>([]);
    const [planets, setPlanets] = useState<Planet[]>([]);
    const [lightParticles, setLightParticles] = useState<LightParticle[]>([]);
    const [mousePosition, setMousePosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

    useEffect(() => {
        const generateStars = (count: number): Star[] => {
            const newStars: Star[] = [];
            for (let i = 0; i < count; i++) {
                newStars.push({
                    id: i,
                    x: Math.random() * 100,
                    y: Math.random() * 100,
                    size: Math.random() * 2.5 + 0.5,
                    opacity: Math.random() * 0.5 + 0.4,
                    speed: Math.random() * 0.5 + 0.1,
                });
            }
            return newStars;
        };

        const generatePlanets = (count: number): Planet[] => {
            const colors = ['rgba(100, 100, 255, 0.3)', 'rgba(255, 100, 100, 0.3)', 'rgba(100, 255, 100, 0.2)'];
            const newPlanets: Planet[] = [];
            for (let i = 0; i < count; i++) {
                newPlanets.push({
                    id: i,
                    x: Math.random() * 100,
                    y: Math.random() * 100,
                    size: Math.random() * 50 + 20,
                    color: colors[Math.floor(Math.random() * colors.length)],
                });
            }
            return newPlanets;
        };

        const generateLightParticles = (count: number): LightParticle[] => {
            const newParticles: LightParticle[] = [];
            for (let i = 0; i < count; i++) {
                newParticles.push({
                    id: i,
                    x: Math.random() * 100,
                    y: Math.random() * 100,
                    size: Math.random() * 10 + 5,
                });
            }
            return newParticles;
        };

        setStars(generateStars(300));
        setPlanets(generatePlanets(5));
        setLightParticles(generateLightParticles(50));
    }, []);

    useEffect(() => {
        document.body.className = theme;
    }, [theme]);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setMousePosition({ x: e.clientX, y: e.clientY });
        };
        window.addEventListener('mousemove', handleMouseMove);
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
        };
    }, []);

    return (
        <div className={`background ${theme}`}>
            {planets.map((planet) => (
                <div
                    key={planet.id}
                    className="planet"
                    style={{
                        left: `${planet.x}%`,
                        top: `${planet.y}%`,
                        width: `${planet.size}px`,
                        height: `${planet.size}px`,
                        background: planet.color,
                    }}
                />
            ))}
            {stars.map((star) => (
                <div
                    key={star.id}
                    className="star"
                    style={{
                        left: `${star.x}%`,
                        top: `${star.y}%`,
                        width: `${star.size}px`,
                        height: `${star.size}px`,
                        opacity: star.opacity,
                        animationDuration: `${star.speed * 10}s`,
                    }}
                />
            ))}
            {lightParticles.map((particle) => (
                <div
                    key={particle.id}
                    className="light-particle"
                    style={{
                        left: `${particle.x}%`,
                        top: `${particle.y}%`,
                        width: `${particle.size}px`,
                        height: `${particle.size}px`,
                    }}
                />
            ))}
            <div className="nebula" />
            <div
                className="lens-effect"
                style={{
                    left: `${mousePosition.x}px`,
                    top: `${mousePosition.y}px`,
                }}
            />

            <div className="content-placeholder">
                <h1>Chào mừng đến với Website Chủ đề Không Gian</h1>
                <p>UI/UX hiện đại với hiệu ứng ngôi sao, hành tinh và kính lúp theo chuột</p>
            </div>
        </div>
    );
};

export default Background;