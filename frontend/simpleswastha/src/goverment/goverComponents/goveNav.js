import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../css/goveNav.css';
import logo from '../img/nav_logo.png';
import noti from '../img/notification.png';

export default function GoveNav() {
  const [showNotifications, setShowNotifications] = useState(false);

  const toggleNotifications = () => {
    setShowNotifications(!showNotifications);
  };

  const closeNotifications = (e) => {
    if (e.target.className === 'notification-offcanvas' || e.target.className === 'close-notification') {
      setShowNotifications(false);
    }
  };

  return (
    <div className="goveNav-body" onClick={closeNotifications}>
      <nav className="goveNav">
        <div className="goveNav-logo">
          <img src={logo} alt="Simple Svastha" />
        </div>
        <Link to="/government" className="goveNav-active">Home</Link>
        <Link to="/government/map">DCMS</Link>
        <Link to="/government/schemes">Government Schemes</Link>
        <Link to="/government/centralPa">Centralized Patient History</Link>
        <button className="goveNav-helpButton" onClick={toggleNotifications}>
          <img src={noti} alt="Simple Svastha" /> <samp>NOTIFICATION</samp>
        </button>
      </nav>

      {showNotifications && (
        <div className="notification-offcanvas">
          <div className="notification-header">
            <img src={noti} alt="Bell Icon" />
            <h3>Notifications</h3>
            <button className="close-notification">×</button>
          </div>
          <div className="notification-body">
            <div className="notification-box">
              <h4>Notification Title 1</h4>
              <p>This is the body of notification 1.</p>
              <button className="mark-as-read">Mark as Read</button>
            </div>
            <div className="notification-box">
              <h4>Notification Title 2</h4>
              <p>This is the body of notification 2.</p>
              <button className="mark-as-read">Mark as Read</button>
            </div>
            <div className="notification-box">
              <h4>Notification Title 3</h4>
              <p>This is the body of notification 3.</p>
              <button className="mark-as-read">Mark as Read</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
