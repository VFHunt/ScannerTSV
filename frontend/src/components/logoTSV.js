import React from 'react';
import logoImage from '../assets/logo.png'; // Adjust the path to your image file

const LogoViewer = () => {
    const handleLogoClick = () => {
        window.location.href = ''; // Replace with your desired link
    };

    return (
        <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <div style={{ marginTop: '20px' }}>
                <img
                    src={logoImage} // Use the imported image
                    alt=""
                    style={{ maxWidth: '200px', maxHeight: '200px', cursor: 'pointer' }}
                    onClick={handleLogoClick} // Redirect on click
                />
            </div>
        </div>
    );
};

export default LogoViewer;
// import React from 'react';
// import logoImage from '../assets/logo.png'; // Adjust the path to your image file

// const LogoViewer = () => {
//     const handleLogoClick = () => {
//         window.location.href = ''; // Replace with your desired link
//     };

//     return (
//         <div style={{ textAlign: 'center', marginTop: '20px' }}>
//             <div style={{ marginTop: '20px' }}>
//                 <img
//                     src={logoImage} // Use the imported image
//                     alt=""
//                     style={{ maxWidth: '200px', maxHeight: '200px', cursor: 'pointer' }}
//                     onClick={handleLogoClick} // Redirect on click
//                 />
//             </div>
//         </div>
//     );
// };

// export default LogoViewer;