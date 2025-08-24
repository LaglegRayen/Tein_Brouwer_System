import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = ({ isAuthenticated, user, onLogout }) => {
  return (
    <nav className="navbar">
      <div className="container">
        <div className="navbar-content">
          <Link to="/" className="navbar-brand">
            SaaS Platform
          </Link>
          <div className="navbar-nav">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="navbar-link">
                  Dashboard
                </Link>
                <Link to="/local-ranking-grid" className="navbar-link">
                  Local Ranking Grid
                </Link>
                <span className="navbar-link">
                  Profile
                </span>
                <button 
                  onClick={onLogout} 
                  className="btn btn-secondary"
                  style={{ padding: '8px 16px', fontSize: '14px' }}
                >
                  Logout
                </button>
                {user && (
                  <span style={{ fontSize: '14px', color: '#6b7280' }}>
                    {user.email}
                  </span>
                )}
              </>
            ) : (
              <>
                <Link to="/login" className="navbar-link">
                  Login
                </Link>
                <Link to="/signup/email" className="btn" style={{ padding: '8px 16px', fontSize: '14px' }}>
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 