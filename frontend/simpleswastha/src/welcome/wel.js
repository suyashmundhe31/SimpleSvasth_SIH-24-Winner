import React from 'react';
import { Link } from 'react-router-dom';
import './welcome.css';
import SimpleSwasthIcon from './Simple_swasth_icon.png';
import UserIcon from './User.png';
import AdminIcon from './admin.png';
import GovernmentIcon from './government.png';
import NextIcon from './Next_icon.png';

const Welcome = () => {
  return (
    <div className="wel-body">
          <div className="wel-wrapper">
      <div className="wel-main-logo">
        <img src={SimpleSwasthIcon} alt="Main Logo" className="wel-simple-swasth-logo" />
      </div>
      <div className="wel-welcome-message">
        <div className='header'>Welcome to Simple Swasth.</div>
        <p>A one-stop solution for all your health-related issues.</p>
      </div>
      <div className="wel-sub-container">
        <Link to="/user">
          <div className="wel-option-box" style={{ backgroundColor: '#c5dcff' }}>
            <div className="wel-icon-option" style={{ backgroundColor: '#d9ecfe' }}>
              <img src={UserIcon} alt="User Icon" />
            </div>
            <div className="wel-text-box" style={{ color: '#2f41dd' }}>
              <h3><b>User Login</b></h3>
              <p>Check the availability for the hospital you're looking for.</p>
            </div>
            <div className="wel-arrow-icon">
              <img src={NextIcon} alt="Next Icon" />
            </div>
          </div>
        </Link>
        <Link to="/admin">
          <div className="wel-option-box" style={{ backgroundColor: '#b5ebba' }}>
            <div className="wel-icon-option" style={{ backgroundColor: '#d9fee1' }}>
              <img src={AdminIcon} alt="Admin Icon" style={{ width: '90px' }} />
            </div>
            <div className="wel-text-box" style={{ color: '#0d3f1b' }}>
              <h3><b>Admin Login</b></h3>
              <p>Manage your hospital from here.</p>
            </div>
            <div className="wel-arrow-icon">
              <img src={NextIcon} alt="Next Icon" />
            </div>
          </div>
        </Link>
        <Link to="/government">
          <div className="wel-option-box" style={{ backgroundColor: '#d9a3e7' }}>
            <div className="wel-icon-option" style={{ backgroundColor: '#fbd9fe' }}>
              <img src={GovernmentIcon} alt="Government Icon" style={{ width: '100px' }} />
            </div>
            <div className="wel-text-box" style={{ color: '#3e0d3f' }}>
              <h3><b>Government Login</b></h3>
              <p>Government management interface.</p>
            </div>
            <div className="wel-arrow-icon">
              <img src={NextIcon} alt="Next Icon" />
            </div>
          </div>
        </Link>
      </div>
    </div>
    </div>
  );
};

export default Welcome;
