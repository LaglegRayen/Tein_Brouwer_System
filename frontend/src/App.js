import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from './components/Navbar';
import SignupEmail from './components/SignupEmail';
import SignupPassword from './components/SignupPassword';
import PricingPage from './components/PricingPage';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import LocalRankingGrid from './components/LocalRankingGrid';

// Configure axios defaults
axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [logoutInProgress, setLogoutInProgress] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, [logoutInProgress]);

  const checkAuthStatus = async () => {
    console.log('🔍 checkAuthStatus called, logoutInProgress:', logoutInProgress);
    // Don't check auth if logout is in progress
    if (logoutInProgress) {
      console.log('⏸️ Skipping auth check - logout in progress');
      setIsAuthenticated(false);
      setUser(null);
      setLoading(false);
      return;
    }
    
    try {
      console.log('📡 Calling auth check API...');
      const response = await axios.get('http://localhost:8000/api/accounts/check-auth/');
      console.log('🔍 Auth check response:', response.data);
      if (response.data.authenticated) {
        console.log('✅ User is authenticated');
        setIsAuthenticated(true);
        setUser(response.data.user);
      } else {
        console.log('❌ User is not authenticated');
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (error) {
      console.log('❌ Auth check error:', error.response?.data || error.message);
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setIsAuthenticated(true);
    setUser(userData);
  };

  const handleLogout = async () => {
    console.log('🔄 Logout started');
    // Set logout in progress immediately
    setLogoutInProgress(true);
    setIsAuthenticated(false);
    setUser(null);
    console.log('✅ State cleared immediately');
    
    try {
      // Call logout endpoint
      console.log('📡 Calling logout endpoint...');
      const response = await axios.post('http://localhost:8000/api/accounts/logout/');
      console.log('✅ Logout API success:', response.data);
    } catch (error) {
      console.error('❌ Logout API error:', error.response?.data || error.message);
      console.error('❌ Full error:', error);
    }
    
    // Clear stored data
    localStorage.clear();
    sessionStorage.clear();
    console.log('🗑️ Storage cleared');
    
    // Keep logout in progress to prevent re-authentication
    setTimeout(() => {
      console.log('⏰ Timeout complete, allowing auth check');
      setLogoutInProgress(false);
    }, 1000);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <Navbar isAuthenticated={isAuthenticated} user={user} onLogout={handleLogout} />
        <Routes>
          <Route 
            path="/" 
            element={
              (() => {
                console.log('🛤️ Root route: isAuthenticated =', isAuthenticated, ', logoutInProgress =', logoutInProgress);
                if (logoutInProgress) {
                  return <Navigate to="/login" />;
                }
                return isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/login" />;
              })()
            } 
          />
          <Route 
            path="/signup/email" 
            element={
              isAuthenticated ? <Navigate to="/dashboard" /> : <SignupEmail />
            } 
          />
          <Route 
            path="/signup/password" 
            element={
              isAuthenticated ? <Navigate to="/dashboard" /> : <SignupPassword />
            } 
          />
          <Route 
            path="/signup/pricing" 
            element={
              isAuthenticated ? <Navigate to="/dashboard" /> : <PricingPage onSignupComplete={handleLogin} />
            } 
          />
          <Route 
            path="/login" 
            element={
              isAuthenticated ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />
            } 
          />
          <Route 
            path="/dashboard" 
            element={
              (() => {
                console.log('🛤️ Dashboard route: isAuthenticated =', isAuthenticated, ', logoutInProgress =', logoutInProgress);
                if (logoutInProgress) {
                  return <Navigate to="/login" />;
                }
                return isAuthenticated ? <Dashboard user={user} /> : <Navigate to="/login" />;
              })()
            } 
          />
          <Route 
            path="/local-ranking-grid" 
            element={
              (() => {
                console.log('🛤️ Local Ranking Grid route: isAuthenticated =', isAuthenticated, ', logoutInProgress =', logoutInProgress);
                if (logoutInProgress) {
                  return <Navigate to="/login" />;
                }
                return isAuthenticated ? (
                  <LocalRankingGrid 
                    isAuthenticated={isAuthenticated} 
                    user={user}
                  />
                ) : (
                  <Navigate to="/login" />
                );
              })()
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 