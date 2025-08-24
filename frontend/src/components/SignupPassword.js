import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const SignupPassword = () => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const storedEmail = localStorage.getItem('signupEmail');
    if (!storedEmail) {
      navigate('/signup/email');
      return;
    }
    setEmail(storedEmail);
  }, [navigate]);

  const validatePassword = (password) => {
    return password.length >= 6;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!password) {
      setError('Password is required');
      return;
    }

    if (!validatePassword(password)) {
      setError('Password must be at least 6 characters long');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    localStorage.setItem('signupPassword', password);
    navigate('/signup/pricing');
  };

  const handleBack = () => {
    navigate('/signup/email');
  };

  return (
    <div className="container">
      <div style={{ maxWidth: '400px', margin: '80px auto' }}>
        <div className="card">
          <h2 style={{ marginBottom: '24px', textAlign: 'center' }}>Set Your Password</h2>
          <p style={{ marginBottom: '32px', textAlign: 'center', color: '#6b7280' }}>
            Step 2 of 3: Create a secure password for {email}
          </p>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="password">
                Password
              </label>
              <input
                type="password"
                id="password"
                className="form-input"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoFocus
              />
              <small style={{ fontSize: '12px', color: '#6b7280' }}>
                Minimum 6 characters
              </small>
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="confirmPassword">
                Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                className="form-input"
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
              {error && <div className="error">{error}</div>}
            </div>
            
            <div style={{ display: 'flex', gap: '12px' }}>
              <button 
                type="button" 
                onClick={handleBack}
                className="btn btn-secondary" 
                style={{ flex: 1 }}
              >
                Back
              </button>
              <button type="submit" className="btn" style={{ flex: 1 }}>
                Next
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SignupPassword; 