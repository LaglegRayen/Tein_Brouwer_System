import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const PricingPage = ({ onSignupComplete }) => {
  const [plans, setPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const storedEmail = localStorage.getItem('signupEmail');
    const storedPassword = localStorage.getItem('signupPassword');
    
    if (!storedEmail || !storedPassword) {
      navigate('/signup/email');
      return;
    }
    
    setEmail(storedEmail);
    setPassword(storedPassword);
    fetchPricingPlans();
  }, [navigate]);

  const fetchPricingPlans = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/accounts/pricing/');
      setPlans(response.data.plans);
      if (response.data.plans.length > 0) {
        setSelectedPlan(response.data.plans[0].id);
      }
    } catch (error) {
      console.error('Error fetching pricing plans:', error);
      setError('Failed to load pricing plans');
    }
  };

  const handlePlanSelect = (planId) => {
    setSelectedPlan(planId);
  };

  const handleQuickSignup = async (planId) => {
    setSelectedPlan(planId);
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8000/api/accounts/signup/', {
        email: email,
        password: password,
        pricing_plan: planId
      });

      localStorage.removeItem('signupEmail');
      localStorage.removeItem('signupPassword');
      
      onSignupComplete(response.data.user);
      navigate('/dashboard');
    } catch (error) {
      setError(error.response?.data?.error || 'Signup failed. Please try again.');
      setLoading(false);
    }
  };

  const handleSignup = async () => {
    if (!selectedPlan) {
      setError('Please select a pricing plan');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8000/api/accounts/signup/', {
        email: email,
        password: password,
        pricing_plan: selectedPlan
      });

      localStorage.removeItem('signupEmail');
      localStorage.removeItem('signupPassword');
      
      onSignupComplete(response.data.user);
      navigate('/dashboard');
    } catch (error) {
      setError(error.response?.data?.error || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/signup/password');
  };

  return (
    <div className="container">
      <div style={{ maxWidth: '800px', margin: '40px auto' }}>
        <div className="card">
          <h2 style={{ marginBottom: '16px', textAlign: 'center' }}>Choose Your Plan</h2>
          <p style={{ marginBottom: '40px', textAlign: 'center', color: '#6b7280' }}>
            Step 3 of 3: Select the perfect plan for your needs
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
          
          <div className="grid grid-cols-3" style={{ marginBottom: '40px' }}>
            {plans.map((plan) => (
              <div 
                key={plan.id}
                className={`card ${selectedPlan === plan.id ? 'selected-plan' : ''}`}
                style={{ 
                  cursor: 'pointer',
                  border: selectedPlan === plan.id ? '2px solid #3b82f6' : '2px solid transparent',
                  transition: 'all 0.2s'
                }}
                onClick={() => handlePlanSelect(plan.id)}
              >
                <h3 style={{ marginBottom: '12px', color: '#1f2937' }}>{plan.name}</h3>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3b82f6', marginBottom: '16px' }}>
                  {plan.price}
                </div>
                <ul style={{ listStyle: 'none', padding: 0, marginBottom: '20px' }}>
                  {plan.features.map((feature, index) => (
                    <li key={index} style={{ 
                      marginBottom: '8px', 
                      padding: '4px 0',
                      borderBottom: index < plan.features.length - 1 ? '1px solid #f3f4f6' : 'none'
                    }}>
                      ✓ {feature}
                    </li>
                  ))}
                </ul>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    handleQuickSignup(plan.id);
                  }}
                  className="btn btn-success"
                  disabled={loading}
                  style={{ 
                    width: '100%', 
                    padding: '12px',
                    fontSize: '14px',
                    fontWeight: 'bold'
                  }}
                >
                  {loading ? 'Starting...' : 'Start Free Trial'}
                </button>
              </div>
            ))}
          </div>
          
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <h3 style={{ marginBottom: '16px', color: '#1f2937' }}>Or select a plan and proceed manually:</h3>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button 
                type="button" 
                onClick={handleBack}
                className="btn btn-secondary"
                disabled={loading}
              >
                Back
              </button>
              <button 
                onClick={handleSignup}
                className="btn btn-primary"
                disabled={loading || !selectedPlan}
                style={{ minWidth: '120px' }}
              >
                {loading ? 'Creating Account...' : 'Continue with Selected Plan'}
              </button>
            </div>
          </div>
          
          <div style={{ 
            background: '#f8fafc', 
            padding: '20px', 
            borderRadius: '8px',
            textAlign: 'center',
            border: '1px solid #e2e8f0'
          }}>
            <h4 style={{ marginBottom: '12px', color: '#1f2937' }}>✨ What's Included in Your Free Trial</h4>
            <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
              • 7-day free trial on any plan
            </p>
            <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
              • No credit card required
            </p>
            <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
              • Full access to all plan features
            </p>
            <p style={{ fontSize: '14px', color: '#6b7280' }}>
              • Cancel anytime with one click
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPage; 