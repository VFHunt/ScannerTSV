import React from 'react';
import KeywordSearch from "../components/KeywordSearch";
import FileUpload from "../components/FileUpload";
import '../styles/Main.css';

const MainPage = () => {
    return (
        <div className="container">
            <div className="content">
                <div className="KeywordSearch">
                    <KeywordSearch />
                </div>
                <div className="FileUpload">
                    <FileUpload />
                </div>
            </div>
        </div>
    );
};

export default MainPage;