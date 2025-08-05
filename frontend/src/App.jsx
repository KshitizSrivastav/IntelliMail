import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// Components
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import EmailView from './pages/EmailView';
import AuthCallback from './pages/AuthCallback';
import Layout from './components/Layout';
import LoadingSpinner from './components/LoadingSpinner';

// Services
import { authService } from './services/authService';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Check for stored access token
        const storedToken = localStorage.getItem('access_token');
        const authToken = localStorage.getItem('auth_token');
        
        console.log('App initialization - Tokens found:', { 
          accessToken: storedToken ? 'present' : 'missing',
          authToken: authToken ? 'present' : 'missing'
        });
        
        if (storedToken && authToken) {
          // Try to decode the JWT to get user info
          try {
            const payload = JSON.parse(atob(authToken.split('.')[1]));
            const user = {
              email: payload.email,
              name: payload.name,
              token: authToken,
              accessToken: storedToken
            };
            console.log('App initialization - User restored:', user);
            setUser(user);
          } catch (decodeError) {
            console.error('Error decoding stored token:', decodeError);
            // Clear invalid tokens
            localStorage.removeItem('access_token');
            localStorage.removeItem('auth_token');
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('auth_token');
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const handleLogin = (userData, token) => {
    setUser(userData);
    localStorage.setItem('access_token', token);
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('auth_token');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              theme: {
                primary: '#4ade80',
                secondary: '#000',
              },
            },
            error: {
              duration: 5000,
              theme: {
                primary: '#ef4444',
                secondary: '#000',
              },
            },
          }}
        />
        
        <Routes>
          <Route 
            path="/login" 
            element={
              user ? <Navigate to="/dashboard" replace /> : 
              <Login onLogin={handleLogin} />
            } 
          />
          
          <Route 
            path="/auth/callback" 
            element={<AuthCallback onLogin={handleLogin} />} 
          />
          
          <Route 
            path="/" 
            element={
              user ? <Navigate to="/dashboard" replace /> : 
              <Navigate to="/login" replace />
            } 
          />
          
          <Route 
            path="/dashboard" 
            element={
              user ? (
                <Layout user={user} onLogout={handleLogout}>
                  <Dashboard user={user} />
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          
          <Route 
            path="/email/:emailId" 
            element={
              user ? (
                <Layout user={user} onLogout={handleLogout}>
                  <EmailView user={user} />
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          
          {/* Catch all route */}
          <Route 
            path="*" 
            element={<Navigate to="/" replace />} 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
