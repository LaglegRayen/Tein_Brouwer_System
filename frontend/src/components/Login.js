import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const Login = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8000/api/accounts/login/', {
        email: email,
        password: password
      });

      onLogin(response.data.user);
      navigate('/dashboard');
    } catch (error) {
      if (error.response?.data?.email || error.response?.data?.password) {
        setError('Invalid email or password');
      } else {
        setError(error.response?.data?.non_field_errors?.[0] || 'Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div style={{ maxWidth: '400px', margin: '80px auto' }}>
        <div className="card">
          <h2 style={{ marginBottom: '24px', textAlign: 'center' }}>Welcome Back</h2>
          <p style={{ marginBottom: '32px', textAlign: 'center', color: '#6b7280' }}>
            Sign in to your account
          </p>
          
          {error && (
            <div style={{ 
              background: '#fef2f2', 
              border: '1px solid #fecaca', 
              color: '#dc2626', 
              padding: '12px', 
              borderRadius: '8px', 
              marginBottom: '24px' 
            }}>
              {error}
            </div>
          )}
          
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
                required
                autoFocus
              />
            </div>
            
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
                required
              />
            </div>
            
            <button 
              type="submit" 
              className="btn" 
              style={{ width: '100%' }}
              disabled={loading}
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>
          
          <p style={{ marginTop: '24px', textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
            Don't have an account?{' '}
            <Link to="/signup/email" style={{ color: '#3b82f6', textDecoration: 'none' }}>
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
