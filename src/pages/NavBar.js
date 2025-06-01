import React from 'react';
import LogoViewer from '../components/logoTSV'; // Import the LogoViewer component
import '../styles/Leftbar.css'; // Import the CSS file

const NavBar = () => {
    return (
        <div className="leftbarContainer">
            <div className="logo">
                <LogoViewer /> {/* Add the LogoViewer at the top */}
            </div>
        </div>
    );
};

export default LeftbarPage;