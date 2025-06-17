import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';

const BackButton = () => {
  const navigate = useNavigate();
  const location = useLocation();  const handleBack = (e) => {
    e.preventDefault();

    // If we're in a document or results view and would go back to uploads, go to projectview instead
    if (location.pathname.includes('/results/')) {
      navigate('/projectview/');
    } else if (location.pathname.includes('/projectview/')) {
      navigate('/uploads/');
    } else if (location.key) { // If we have location history
      navigate(-1);
    } else {
      navigate('/');
    }
  };

  return (
    <div style={{ padding: '20px 0 0 40px' }}>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={handleBack}
        style={{
          borderRadius: '8px',
        }}
      >
        Go Back
      </Button>
    </div>
  );
};

export default BackButton;
