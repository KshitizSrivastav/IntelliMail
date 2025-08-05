import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const AuthCallback = ({ onLogin }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const token = searchParams.get('token');
        const accessToken = searchParams.get('access_token');
        const error = searchParams.get('error');

        console.log('AuthCallback - Received params:', { 
          token: token ? 'present' : 'missing', 
          accessToken: accessToken ? 'present' : 'missing',
          error 
        });

        if (error) {
          toast.error(`Authentication error: ${error}`);
          navigate('/');
          return;
        }

        if (token && accessToken) {
          // Store tokens in localStorage (using consistent key names)
          localStorage.setItem('access_token', accessToken);
          localStorage.setItem('auth_token', token);

          // Decode JWT to get user info
          try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const user = {
              email: payload.email,
              name: payload.name,
              token: token,
              accessToken: accessToken
            };

            console.log('AuthCallback - User decoded:', user);
            toast.success('Login successful!');
            onLogin(user, accessToken); // Pass both user and token
            navigate('/dashboard');
          } catch (decodeError) {
            console.error('Error decoding token:', decodeError);
            toast.error('Authentication failed');
            navigate('/');
          }
        } else {
          toast.error('Missing authentication tokens');
          navigate('/');
        }
      } catch (error) {
        console.error('Auth callback error:', error);
        toast.error('Authentication failed');
        navigate('/');
      }
    };

    handleCallback();
  }, [searchParams, navigate, onLogin]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner />
        <p className="mt-4 text-gray-600">Completing authentication...</p>
      </div>
    </div>
  );
};

export default AuthCallback;
