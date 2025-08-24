import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard = ({ user }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/dashboard/data/');
      setDashboardData(response.data);
    } catch (error) {
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="container">
        <div style={{ textAlign: 'center', marginTop: '80px' }}>
          <div>Loading dashboard...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div style={{ 
          background: '#fef2f2', 
          border: '1px solid #fecaca', 
          color: '#dc2626', 
          padding: '16px', 
          borderRadius: '8px', 
          marginTop: '40px' 
        }}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div style={{ marginBottom: '40px' }}>
        <h1 style={{ marginBottom: '8px' }}>Dashboard</h1>
        <p style={{ color: '#6b7280' }}>
          Welcome back, {user?.email || 'User'}! Here's your business overview.
        </p>
        {dashboardData?.user_profile?.subscription_status === 'trialing' && (
          <div style={{
            background: '#dbeafe',
            border: '1px solid #93c5fd',
            color: '#1e40af',
            padding: '12px 16px',
            borderRadius: '8px',
            marginTop: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div>
              <strong>🎉 Free Trial Active!</strong> You have {dashboardData?.user_profile?.trial_days_left || 7} days left on your {dashboardData?.user_profile?.plan_name || 'trial'}.
            </div>
            <button className="btn btn-primary" style={{ padding: '6px 12px', fontSize: '14px' }}>
              Upgrade Now
            </button>
          </div>
        )}
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-4" style={{ marginBottom: '40px' }}>
        <div className="card">
          <h3 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Total Users</h3>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#1f2937' }}>
            {dashboardData?.total_users?.toLocaleString() || '0'}
          </div>
          <div style={{ fontSize: '12px', color: '#10b981' }}>
            +{dashboardData?.growth_rate || 0}% this month
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Active Subscriptions</h3>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#1f2937' }}>
            {dashboardData?.active_subscriptions?.toLocaleString() || '0'}
          </div>
          <div style={{ fontSize: '12px', color: '#10b981' }}>
            {dashboardData?.trial_conversions || 0}% trial conversion
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Monthly Revenue</h3>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#1f2937' }}>
            {formatCurrency(dashboardData?.monthly_revenue || 0)}
          </div>
          <div style={{ fontSize: '12px', color: '#ef4444' }}>
            {dashboardData?.churn_rate || 0}% churn rate
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Avg. Rating</h3>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#1f2937' }}>
            {dashboardData?.review_metrics?.average_rating || '0'}⭐
          </div>
          <div style={{ fontSize: '12px', color: '#6b7280' }}>
            {dashboardData?.review_metrics?.total_reviews || 0} reviews
          </div>
        </div>
      </div>

      {/* Quick Stats Bar */}
      {dashboardData?.quick_stats && (
        <div style={{ 
          background: '#f8fafc', 
          padding: '20px', 
          borderRadius: '8px', 
          marginBottom: '40px',
          border: '1px solid #e2e8f0'
        }}>
          <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>Today's Quick Stats</h3>
          <div className="grid grid-cols-4">
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981', marginBottom: '4px' }}>
                {dashboardData.quick_stats.new_signups_today}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>New Signups</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b', marginBottom: '4px' }}>
                {dashboardData.quick_stats.trials_ending_soon}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Trials Ending Soon</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ef4444', marginBottom: '4px' }}>
                {dashboardData.quick_stats.support_tickets_open}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Open Tickets</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981', marginBottom: '4px' }}>
                {dashboardData.quick_stats.server_uptime}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Server Uptime</div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2">
        {/* Recent Activities */}
        <div className="card">
          <h3 style={{ marginBottom: '24px' }}>Recent Activities</h3>
          <div>
            {dashboardData?.recent_activities?.map((activity) => (
              <div key={activity.id} style={{ 
                padding: '16px 0', 
                borderBottom: '1px solid #f3f4f6',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start'
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: '500', marginBottom: '4px' }}>
                    {activity.action}
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>
                    {activity.description}
                  </div>
                  <div style={{ fontSize: '12px', color: '#9ca3af' }}>
                    {activity.user}
                  </div>
                </div>
                <div style={{ fontSize: '12px', color: '#6b7280', marginLeft: '16px' }}>
                  {formatDate(activity.timestamp)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Review Metrics */}
        <div className="card">
          <h3 style={{ marginBottom: '24px' }}>Customer Reviews</h3>
          
          {/* Star Rating Breakdown */}
          <div style={{ marginBottom: '24px' }}>
            {[5, 4, 3, 2, 1].map((stars) => {
              const count = dashboardData?.review_metrics?.[`${['five', 'four', 'three', 'two', 'one'][5-stars]}_star`] || 0;
              const total = dashboardData?.review_metrics?.total_reviews || 1;
              const percentage = (count / total) * 100;
              
              return (
                <div key={stars} style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  marginBottom: '8px',
                  fontSize: '14px'
                }}>
                  <span style={{ minWidth: '20px' }}>{stars}⭐</span>
                  <div style={{ 
                    flex: 1, 
                    background: '#f3f4f6', 
                    height: '8px', 
                    borderRadius: '4px',
                    margin: '0 12px',
                    overflow: 'hidden'
                  }}>
                    <div style={{ 
                      background: '#10b981', 
                      height: '100%', 
                      width: `${percentage}%`,
                      transition: 'width 0.3s ease'
                    }} />
                  </div>
                  <span style={{ minWidth: '30px', color: '#6b7280' }}>{count}</span>
                </div>
              );
            })}
          </div>

          {/* Recent Review */}
          {dashboardData?.review_metrics?.recent_review && (
            <div style={{ 
              background: '#f8fafc', 
              padding: '16px', 
              borderRadius: '8px',
              border: '1px solid #e2e8f0'
            }}>
              <div style={{ marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
                Latest Review
              </div>
              <div style={{ marginBottom: '8px' }}>
                {'⭐'.repeat(dashboardData.review_metrics.recent_review.rating)}
              </div>
              <div style={{ fontSize: '14px', color: '#4b5563', marginBottom: '8px' }}>
                "{dashboardData.review_metrics.recent_review.comment}"
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>
                — {dashboardData.review_metrics.recent_review.user}, {formatDate(dashboardData.review_metrics.recent_review.date)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 