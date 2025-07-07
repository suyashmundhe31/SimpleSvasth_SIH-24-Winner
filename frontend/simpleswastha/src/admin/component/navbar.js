import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../css/navbar.css';
import logo from '../img/nav_logo.png';
import bellIcon from '../img/notification.png';

export default function NavbarAdmin() {
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
    <div className="nav-body" onClick={closeNotifications}>
      <nav className="nav">
        <div className="nav-logo">
          <img src={logo} alt="Simple Svastha" />
        </div>
        <Link to="/admin/home" className="nav-active">Home</Link>
        <Link to="/admin/addBed">Bed Booking</Link>
        <Link to="/admin/opdSc">OPD Appointment</Link>
        <Link to="/admin/inventory">Inventory</Link>
        <Link to="/admin/account">Account</Link>
        <button className="nav-helpButton" onClick={toggleNotifications}> <img src={bellIcon} alt="Bell Icon" />
          <samp>NOTIFICATION</samp>
        </button>
      </nav>

      {showNotifications && (
        <div className="notification-offcanvas">
          <div className="notification-header">
            <img src={bellIcon} alt="Bell Icon" />
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
