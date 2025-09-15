import React, { useState } from "react";
import "./Taskbar.css"; // import file css
import ThemeToggle from "./ThemeToggle";

const Taskbar: React.FC = () => {
    const [language, setLanguage] = useState<"vi" | "en">("vi");
    const [showLangMenu, setShowLangMenu] = useState(false);

    return (
        <div className="taskbar">
            <div className="logo">Dane</div>

            <div className="actions">
                {/* Nút ngôn ngữ */}
                <div className="lang-wrapper">
                    <button
                        onClick={() => setShowLangMenu(!showLangMenu)}
                        className="btn-lang"
                    >
                        {language === "vi" ? "VI" : "EN"}
                    </button>

                    {showLangMenu && (
                        <div className="lang-menu">
                            <button
                                onClick={() => {
                                    setLanguage("vi");
                                    setShowLangMenu(false);
                                }}
                            >
                                VI
                            </button>
                            <button
                                onClick={() => {
                                    setLanguage("en");
                                    setShowLangMenu(false);
                                }}
                            >
                                EN
                            </button>
                        </div>
                    )}
                </div>

                {/* Nút đăng nhập */}
                <button className="btn-login">Đăng nhập</button>

                <ThemeToggle />
            </div>

            

        </div>
    );
};

export default Taskbar;
