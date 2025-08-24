import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SignupEmail = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!email) {
      setError('Email is required');
      return;
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }

    localStorage.setItem('signupEmail', email);
    navigate('/signup/password');
  };

  return (
    <div className="container">
      <div style={{ maxWidth: '400px', margin: '80px auto' }}>
        <div className="card">
          <h2 style={{ marginBottom: '24px', textAlign: 'center' }}>Create Your Account</h2>
          <p style={{ marginBottom: '32px', textAlign: 'center', color: '#6b7280' }}>
            Step 1 of 3: Enter your email address
          </p>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="email">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                className="form-input"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoFocus
              />
              {error && <div className="error">{error}</div>}
            </div>
            
            <button type="submit" className="btn" style={{ width: '100%' }}>
              Next
            </button>
          </form>
          
          <p style={{ marginTop: '24px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
            Already have an account?{' '}
            <a href="/login" style={{ color: '#3b82f6', textDecoration: 'none' }}>
              Sign in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignupEmail; 