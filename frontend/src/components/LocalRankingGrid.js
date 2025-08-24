import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const LocalRankingGrid = ({ isAuthenticated, user }) => {
  const navigate = useNavigate();
  const [csrfToken, setCsrfToken] = useState(null);

  useEffect(() => {
    // Get CSRF token on component mount
    const getCsrfToken = async () => {
      try {
        console.log('🔄 Fetching CSRF token...');
        
        // Make a GET request to get the CSRF token
        const response = await axios.get('http://localhost:8000/api/get-csrf-token/', {
          withCredentials: true
        });
        
        // Get token from response
        const token = response.data.csrfToken;
        
        if (token) {
          console.log('✅ Got CSRF token from response');
          setCsrfToken(token);
          // Set it as a default header
          axios.defaults.headers.common['X-CSRFToken'] = token;
        } else {
          console.error('❌ No CSRF token in response');
        }
      } catch (error) {
        console.error('❌ Failed to get CSRF token:', error.message);
        if (error.response) {
          console.error('Response:', error.response.data);
          console.error('Status:', error.response.status);
        }
      }
    };

    getCsrfToken();
  }, []);
  const [formData, setFormData] = useState({
    businessName: '',
    businessLat: '',
    businessLng: '',
    gridSize: 3,
    radiusKm: 5.0,
    languageCode: 'en',
    device: 'desktop',
    targetDomain: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('quick'); // 'quick', 'advanced', 'split'

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || '' : value
    }));
  };

  // Fetch latest saved rank grid when businessName changes
  useEffect(() => {
    const fetchHistory = async () => {
      if (!isAuthenticated) return;
      try {
        const res = await axios.get('http://localhost:8000/api/ranking/history/', {
          withCredentials: true,
          params: formData.businessName ? { business_name: formData.businessName } : {}
        });
        setHistory(res.data?.results || []);
      } catch (e) {
        console.error('Failed to fetch history', e);
      }
    };
    fetchHistory();
  }, [isAuthenticated]);

  // Also refresh history whenever business name changes
  useEffect(() => {
    const fetchHistoryByName = async () => {
      if (!isAuthenticated || !formData.businessName) return;
      try {
        const res = await axios.get('http://localhost:8000/api/ranking/history/', {
          withCredentials: true,
          params: { business_name: formData.businessName }
        });
        setHistory(res.data?.results || []);
      } catch (e) {
        console.error('Failed to fetch history by name', e);
      }
    };
    fetchHistoryByName();
  }, [isAuthenticated, formData.businessName]);

  const handleQuickCheck = async (e) => {
    e.preventDefault();
    
    if (!formData.businessName || !formData.businessLat || !formData.businessLng) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      console.log('🚀 Starting quick check with data:', {
        business_name: formData.businessName,
        business_lat: parseFloat(formData.businessLat),
        business_lng: parseFloat(formData.businessLng)
      });

      console.log('Starting quick check with auth state:', {
        isAuthenticated,
        user,
        formData
      });

      if (!isAuthenticated) {
        console.error('Not authenticated');
        setError('Please log in first');
        navigate('/login');
        return;
      }

      // Get current session cookie
      const sessionid = document.cookie.split('; ').find(row => row.startsWith('sessionid='));
      console.log('Session cookie:', sessionid);

      // If we don't have a CSRF token, try to get one first
      if (!csrfToken) {
        console.log('🔄 No CSRF token, fetching one first...');
        try {
          const response = await axios.get('http://localhost:8000/api/get-csrf-token/', {
            withCredentials: true
          });
          const token = response.data.csrfToken;
          if (token) {
            console.log('✅ Got CSRF token on demand');
            setCsrfToken(token);
            axios.defaults.headers.common['X-CSRFToken'] = token;
          } else {
            console.error('❌ No CSRF token in response');
            setError('Failed to get security token. Please try refreshing the page.');
            return;
          }
        } catch (error) {
          console.error('❌ Failed to get CSRF token:', error.message);
          setError('Failed to get security token. Please try refreshing the page.');
          return;
        }
      }

      const config = {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || axios.defaults.headers.common['X-CSRFToken'],
          'X-Requested-With': 'XMLHttpRequest'
        }
      };
      
      console.log('📝 Request config:', config);

      console.log('Request config:', config);

      const response = await axios.post(
        'http://localhost:8000/api/ranking/quick-check/', 
        {
          business_name: formData.businessName,
          business_lat: parseFloat(formData.businessLat),
          business_lng: parseFloat(formData.businessLng),
          target_domain: formData.targetDomain || undefined
        },
        config
      );

      console.log('✅ Quick check response:', response.data);
      setResults(response.data);
    } catch (err) {
      console.error('❌ Quick check error:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        statusText: err.response?.statusText,
        config: {
          url: err.config?.url,
          method: err.config?.method,
          data: err.config?.data
        }
      });
      
      const errorMessage = err.response?.data?.message || 
                          err.response?.data?.error || 
                          err.message || 
                          'Failed to perform quick check';
      setError(`Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAdvancedCheck = async (e) => {
    e.preventDefault();
    
    if (!formData.businessName || !formData.businessLat || !formData.businessLng) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      if (!isAuthenticated) {
        console.error('Not authenticated');
        setError('Please log in first');
        navigate('/login');
        return;
      }

      const response = await axios.post('http://localhost:8000/api/ranking/grid-check/',
        {
          business_name: formData.businessName,
          business_lat: parseFloat(formData.businessLat),
          business_lng: parseFloat(formData.businessLng),
          grid_size: parseInt(formData.gridSize),
          radius_km: parseFloat(formData.radiusKm),
          language_code: formData.languageCode,
          device: formData.device,
          target_domain: formData.targetDomain || undefined
        },
        {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to perform grid check');
      console.error('Grid check error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderResults = () => {
    if (!results) return null;

    const { business_name, center_coordinates, grid_parameters, results: taskResults, metadata, rank_map } = results;
    const { summary } = taskResults || {};

    return (
      <div className="results-section">
        <h3>📊 Results for "{business_name}"</h3>
        
        <div className="results-header">
          <div className="result-card">
            <h4>📍 Location</h4>
            <p>Lat: {center_coordinates?.lat}</p>
            <p>Lng: {center_coordinates?.lng}</p>
          </div>
          
          {grid_parameters && (
            <div className="result-card">
              <h4>🗂️ Grid</h4>
              <p>Size: {grid_parameters.size}x{grid_parameters.size}</p>
              <p>Radius: {grid_parameters.radius_km}km</p>
            </div>
          )}
          
          {summary && (
            <div className="result-card">
              <h4>📈 Summary</h4>
              <p>✅ Completed: {summary.completed_count}</p>
              <p>❌ Failed: {summary.failed_count}</p>
              <p>⏳ Pending: {summary.pending_count}</p>
            </div>
          )}
          
          {metadata && (
            <div className="result-card">
              <h4>⏱️ Timing</h4>
              <p>Duration: {Math.round(metadata.total_duration_seconds)}s</p>
              <p>Status: {metadata.success ? '✅ Success' : '❌ Failed'}</p>
            </div>
          )}
        </div>

        {/* Rank Map Grid */}
        {rank_map && rank_map.length > 0 && (
          <div className="detailed-results">
            <h4>🗺️ Rank Grid</h4>
            <div className="rank-grid" style={{
              display: 'grid',
              gridTemplateColumns: `repeat(${grid_parameters?.size || 3}, 1fr)`,
              gap: '8px',
              marginTop: '12px'
            }}>
              {rank_map.map((cell) => (
                <div key={cell.task_id} className="rank-cell" style={{
                  background: cell.rank ? '#eef2ff' : (cell.status === 'failed' ? '#fee2e2' : '#f9fafb'),
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  padding: '12px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.8rem', color: '#374151', fontWeight: 600 }}>{cell.rank ?? '—'}</div>
                  <div style={{ fontSize: '0.7rem', color: '#6b7280' }}>{cell.status}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Detailed Results */}
        {taskResults?.completed && Object.keys(taskResults.completed).length > 0 && (
          <div className="detailed-results">
            <h4>🎯 Completed Tasks</h4>
            <div className="tasks-grid">
              {Object.entries(taskResults.completed).map(([taskId, data]) => (
                <div key={taskId} className="task-card completed">
                  <h5>Task: {taskId.substring(0, 8)}...</h5>
                  <p>Status: ✅ Completed</p>
                  {data.tasks?.[0]?.result?.[0]?.items && (
                    <p>Results: {data.tasks[0].result[0].items.length} items found</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {taskResults?.failed && Object.keys(taskResults.failed).length > 0 && (
          <div className="detailed-results">
            <h4>❌ Failed Tasks</h4>
            <div className="tasks-grid">
              {Object.entries(taskResults.failed).map(([taskId, data]) => (
                <div key={taskId} className="task-card failed">
                  <h5>Task: {taskId.substring(0, 8)}...</h5>
                  <p>Status: ❌ Failed</p>
                  <p>Reason: {data.tasks?.[0]?.status_message || 'Unknown error'}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {taskResults?.pending && taskResults.pending.length > 0 && (
          <div className="detailed-results">
            <h4>⏳ Pending Tasks</h4>
            <div className="tasks-grid">
              {taskResults.pending.map((taskId) => (
                <div key={taskId} className="task-card pending">
                  <h5>Task: {taskId.substring(0, 8)}...</h5>
                  <p>Status: ⏳ Still processing</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="local-ranking-grid">
      <div className="container">
        <h1>🗺️ Local Ranking Grid</h1>
        <p className="subtitle">
          Analyze local search rankings across multiple grid points around your business location
        </p>

        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button 
            className={`tab ${activeTab === 'quick' ? 'active' : ''}`}
            onClick={() => setActiveTab('quick')}
          >
            ⚡ Quick Check
          </button>
          <button 
            className={`tab ${activeTab === 'advanced' ? 'active' : ''}`}
            onClick={() => setActiveTab('advanced')}
          >
            ⚙️ Advanced Check
          </button>
        </div>

        {/* Quick Check Tab */}
        {activeTab === 'quick' && (
          <div className="tab-content">
            <h2>⚡ Quick Check (3x3 grid, 5km radius)</h2>
            <form onSubmit={handleQuickCheck} className="ranking-form">
              <div className="form-group">
                <label htmlFor="businessName">
                  Business Name *
                </label>
                <input
                  type="text"
                  id="businessName"
                  name="businessName"
                  value={formData.businessName}
                  onChange={handleInputChange}
                  placeholder="e.g., Pizza Restaurant"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="targetDomain">
                    Target Domain (optional)
                  </label>
                  <input
                    type="text"
                    id="targetDomain"
                    name="targetDomain"
                    value={formData.targetDomain}
                    onChange={handleInputChange}
                    placeholder="e.g., example.com"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="businessLat">
                    Latitude *
                  </label>
                  <input
                    type="number"
                    id="businessLat"
                    name="businessLat"
                    value={formData.businessLat}
                    onChange={handleInputChange}
                    placeholder="e.g., 40.689199"
                    step="any"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="businessLng">
                    Longitude *
                  </label>
                  <input
                    type="number"
                    id="businessLng"
                    name="businessLng"
                    value={formData.businessLng}
                    onChange={handleInputChange}
                    placeholder="e.g., -73.975035"
                    step="any"
                    required
                  />
                </div>
              </div>

              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? '🔄 Running Quick Check...' : '⚡ Run Quick Check'}
              </button>
            </form>
          </div>
        )}

        {/* Advanced Check Tab */}
        {activeTab === 'advanced' && (
          <div className="tab-content">
            <h2>⚙️ Advanced Grid Check</h2>
            <form onSubmit={handleAdvancedCheck} className="ranking-form">
              <div className="form-group">
                <label htmlFor="businessName">
                  Business Name *
                </label>
                <input
                  type="text"
                  id="businessName"
                  name="businessName"
                  value={formData.businessName}
                  onChange={handleInputChange}
                  placeholder="e.g., Pizza Restaurant"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="targetDomain">
                    Target Domain (optional)
                  </label>
                  <input
                    type="text"
                    id="targetDomain"
                    name="targetDomain"
                    value={formData.targetDomain}
                    onChange={handleInputChange}
                    placeholder="e.g., example.com"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="businessLat">
                    Latitude *
                  </label>
                  <input
                    type="number"
                    id="businessLat"
                    name="businessLat"
                    value={formData.businessLat}
                    onChange={handleInputChange}
                    placeholder="e.g., 40.689199"
                    step="any"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="businessLng">
                    Longitude *
                  </label>
                  <input
                    type="number"
                    id="businessLng"
                    name="businessLng"
                    value={formData.businessLng}
                    onChange={handleInputChange}
                    placeholder="e.g., -73.975035"
                    step="any"
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="gridSize">
                    Grid Size
                  </label>
                  <select
                    id="gridSize"
                    name="gridSize"
                    value={formData.gridSize}
                    onChange={handleInputChange}
                  >
                    <option value={2}>2x2 (4 points)</option>
                    <option value={3}>3x3 (9 points)</option>
                    <option value={4}>4x4 (16 points)</option>
                    <option value={5}>5x5 (25 points)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="radiusKm">
                    Radius (km)
                  </label>
                  <input
                    type="number"
                    id="radiusKm"
                    name="radiusKm"
                    value={formData.radiusKm}
                    onChange={handleInputChange}
                    min="0.1"
                    max="50"
                    step="0.1"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="languageCode">
                    Language
                  </label>
                  <select
                    id="languageCode"
                    name="languageCode"
                    value={formData.languageCode}
                    onChange={handleInputChange}
                  >
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                    <option value="it">Italian</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="device">
                    Device Type
                  </label>
                  <select
                    id="device"
                    name="device"
                    value={formData.device}
                    onChange={handleInputChange}
                  >
                    <option value="desktop">Desktop</option>
                    <option value="mobile">Mobile</option>
                    <option value="tablet">Tablet</option>
                  </select>
                </div>
              </div>

              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? '🔄 Running Advanced Check...' : '⚙️ Run Advanced Check'}
              </button>
            </form>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {/* Loading Spinner */}
        {loading && (
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>🔄 Processing your request... This may take 2-30 minutes depending on DataForSEO processing time.</p>
          </div>
        )}

        {/* Results */}
        {renderResults()}

        {/* Latest saved grid from history */}
        {history.length > 0 && (
          <div className="results-section">
            <h3>🕘 Latest Saved Grid</h3>
            <div className="detailed-results">
              <div className="rank-grid" style={{
                display: 'grid',
                gridTemplateColumns: `repeat(${history[0]?.grid_parameters?.size || 3}, 1fr)`,
                gap: '8px',
                marginTop: '12px'
              }}>
                {history[0]?.rank_map?.map((cell) => (
                  <div key={cell.task_id} className="rank-cell" style={{
                    background: cell.rank ? '#eef2ff' : (cell.status === 'failed' ? '#fee2e2' : '#f9fafb'),
                    border: '1px solid #e5e7eb',
                    borderRadius: '6px',
                    padding: '12px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.8rem', color: '#374151', fontWeight: 600 }}>{cell.rank ?? '—'}</div>
                    <div style={{ fontSize: '0.7rem', color: '#6b7280' }}>{cell.status}</div>
                  </div>
                ))}
              </div>
              <p style={{ marginTop: '8px', color: '#6b7280' }}>Saved at: {new Date(history[0]?.created_at).toLocaleString()}</p>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .local-ranking-grid {
          min-height: 100vh;
          background-color: #f8fafc;
          padding: 2rem 0;
        }

        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 1rem;
        }

        h1 {
          text-align: center;
          color: #1f2937;
          margin-bottom: 0.5rem;
          font-size: 2.5rem;
        }

        .subtitle {
          text-align: center;
          color: #6b7280;
          margin-bottom: 2rem;
          font-size: 1.1rem;
        }

        .tab-navigation {
          display: flex;
          justify-content: center;
          margin-bottom: 2rem;
          border-bottom: 1px solid #e5e7eb;
        }

        .tab {
          background: none;
          border: none;
          padding: 1rem 2rem;
          cursor: pointer;
          font-size: 1rem;
          color: #6b7280;
          border-bottom: 2px solid transparent;
          transition: all 0.3s ease;
        }

        .tab:hover {
          color: #3b82f6;
        }

        .tab.active {
          color: #3b82f6;
          border-bottom-color: #3b82f6;
          font-weight: 600;
        }

        .tab-content {
          background: white;
          border-radius: 12px;
          padding: 2rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          margin-bottom: 2rem;
        }

        .ranking-form {
          max-width: 600px;
          margin: 0 auto;
        }

        .form-group {
          margin-bottom: 1.5rem;
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 600;
          color: #374151;
        }

        input, select {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #d1d5db;
          border-radius: 8px;
          font-size: 1rem;
          transition: border-color 0.3s ease;
        }

        input:focus, select:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .btn {
          background-color: #3b82f6;
          color: white;
          border: none;
          padding: 1rem 2rem;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: background-color 0.3s ease;
          width: 100%;
          margin-top: 1rem;
        }

        .btn:hover:not(:disabled) {
          background-color: #2563eb;
        }

        .btn:disabled {
          background-color: #9ca3af;
          cursor: not-allowed;
        }

        .error-message {
          background-color: #fef2f2;
          color: #dc2626;
          padding: 1rem;
          border-radius: 8px;
          margin: 1rem 0;
          border: 1px solid #fecaca;
        }

        .loading-spinner {
          text-align: center;
          padding: 2rem;
          background: white;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          margin: 2rem 0;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f4f6;
          border-top: 4px solid #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .results-section {
          background: white;
          border-radius: 12px;
          padding: 2rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          margin: 2rem 0;
        }

        .results-header {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .result-card {
          background: #f8fafc;
          padding: 1rem;
          border-radius: 8px;
          border: 1px solid #e5e7eb;
        }

        .result-card h4 {
          margin: 0 0 0.5rem 0;
          color: #374151;
          font-size: 0.9rem;
        }

        .result-card p {
          margin: 0.25rem 0;
          color: #6b7280;
          font-size: 0.9rem;
        }

        .detailed-results {
          margin-top: 2rem;
        }

        .tasks-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 1rem;
          margin-top: 1rem;
        }

        .task-card {
          padding: 1rem;
          border-radius: 8px;
          border: 1px solid #e5e7eb;
        }

        .task-card.completed {
          background-color: #f0fdf4;
          border-color: #22c55e;
        }

        .task-card.failed {
          background-color: #fef2f2;
          border-color: #ef4444;
        }

        .task-card.pending {
          background-color: #fffbeb;
          border-color: #f59e0b;
        }

        .task-card h5 {
          margin: 0 0 0.5rem 0;
          font-size: 0.9rem;
          color: #374151;
        }

        .task-card p {
          margin: 0.25rem 0;
          font-size: 0.8rem;
          color: #6b7280;
        }

        @media (max-width: 768px) {
          .form-row {
            grid-template-columns: 1fr;
          }
          
          .results-header {
            grid-template-columns: 1fr;
          }
          
          .tasks-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default LocalRankingGrid;
