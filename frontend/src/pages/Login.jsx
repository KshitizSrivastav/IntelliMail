import React, { useState, useEffect, useCallback } from 'react';
import { Mail, Sparkles, LogIn, Shield, Zap, Users } from 'lucide-react';
import toast from 'react-hot-toast';
import { authService } from '../services/authService';
import DebugAuth from '../components/DebugAuth';

const Login = ({ onLogin }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleGoogleCallback = useCallback(async (code) => {
    setIsLoading(true);
    try {
      const result = await authService.authenticateWithGoogle(code);
      toast.success('Successfully authenticated!');
      onLogin(result.user_info, result.access_token);
      
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } catch (error) {
      console.error('Authentication error:', error);
      toast.error('Authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [onLogin]);

  useEffect(() => {
    // Check if we're returning from Google OAuth
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const error = urlParams.get('error');

    if (error) {
      toast.error('Authentication was cancelled or failed');
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
      return;
    }

    if (code) {
      handleGoogleCallback(code);
    }
  }, [handleGoogleCallback]);

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    try {
      const { authorization_url } = await authService.getGoogleAuthUrl();
      // Redirect to Google OAuth
      window.location.href = authorization_url;
    } catch (error) {
      console.error('Failed to get auth URL:', error);
      toast.error('Failed to initiate authentication');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="flex min-h-screen">
        {/* Left Panel - Branding */}
        <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-indigo-700 relative overflow-hidden">
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative z-10 flex flex-col justify-center px-12 text-white">
            <div className="mb-8">
              <div className="flex items-center mb-6">
                <div className="bg-white/20 p-3 rounded-xl mr-4">
                  <Mail className="h-8 w-8" />
                </div>
                <h1 className="text-3xl font-bold">IntelliMail</h1>
              </div>
              <p className="text-xl text-blue-100 mb-8">
                Transform your email experience with AI-powered summarization and intelligent reply generation
              </p>
            </div>

            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="bg-white/20 p-2 rounded-lg mt-1">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">AI-Powered Summaries</h3>
                  <p className="text-blue-100">Get instant, intelligent summaries of long email threads</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="bg-white/20 p-2 rounded-lg mt-1">
                  <Zap className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">Smart Replies</h3>
                  <p className="text-blue-100">Generate context-aware replies with customizable tone</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="bg-white/20 p-2 rounded-lg mt-1">
                  <Shield className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">Secure Integration</h3>
                  <p className="text-blue-100">Direct Gmail integration with OAuth2 security</p>
                </div>
              </div>
            </div>

            <div className="mt-12 p-6 bg-white/10 rounded-xl backdrop-blur-sm">
              <div className="flex items-center space-x-4 mb-4">
                <Users className="h-6 w-6" />
                <span className="text-lg font-semibold">Trusted by professionals</span>
              </div>
              <p className="text-blue-100">
                "IntelliMail has revolutionized how I handle email. I save hours every day with smart summaries and AI replies."
              </p>
              <p className="text-blue-200 text-sm mt-2">- Sarah Chen, Product Manager</p>
            </div>
          </div>

          {/* Decorative elements */}
          <div className="absolute top-20 right-20 w-32 h-32 bg-white/10 rounded-full blur-xl"></div>
          <div className="absolute bottom-32 left-16 w-24 h-24 bg-white/10 rounded-full blur-xl"></div>
        </div>

        {/* Right Panel - Login Form */}
        <div className="flex-1 flex flex-col justify-center px-8 sm:px-12 lg:px-16">
          <div className="w-full max-w-md mx-auto">
            {/* Mobile Logo */}
            <div className="lg:hidden text-center mb-8">
              <div className="flex items-center justify-center mb-4">
                <div className="bg-blue-600 p-3 rounded-xl mr-3">
                  <Mail className="h-8 w-8 text-white" />
                </div>
                <h1 className="text-3xl font-bold text-gray-900">IntelliMail</h1>
              </div>
              <p className="text-gray-600">AI-powered email assistant</p>
            </div>

            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Welcome back</h2>
              <p className="text-gray-600">Sign in to your Gmail account to get started</p>
            </div>

            <div className="space-y-6">
              <button
                onClick={handleGoogleLogin}
                disabled={isLoading}
                className="w-full flex items-center justify-center px-6 py-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-700 font-medium hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
                    Connecting...
                  </div>
                ) : (
                  <div className="flex items-center">
                    <LogIn className="h-5 w-5 mr-3" />
                    Continue with Google
                  </div>
                )}
              </button>

              <div className="text-center">
                <p className="text-sm text-gray-500">
                  By signing in, you agree to our{' '}
                  <button 
                    onClick={() => window.open('/terms', '_blank')}
                    className="text-blue-600 hover:text-blue-700 underline bg-transparent border-none cursor-pointer"
                  >
                    Terms of Service
                  </button>{' '}
                  and{' '}
                  <button 
                    onClick={() => window.open('/privacy', '_blank')}
                    className="text-blue-600 hover:text-blue-700 underline bg-transparent border-none cursor-pointer"
                  >
                    Privacy Policy
                  </button>
                </p>
              </div>
            </div>

            <div className="mt-8 p-4 bg-blue-50 rounded-lg">
              <h3 className="text-sm font-semibold text-blue-900 mb-2">🔒 Your privacy is protected</h3>
              <p className="text-sm text-blue-700">
                We use Google's secure OAuth2 system. We never store your Gmail password and only access emails you explicitly choose to summarize or reply to.
              </p>
            </div>

            {/* Demo Note */}
            <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <h3 className="text-sm font-semibold text-amber-800 mb-1">📝 Demo Version</h3>
              <p className="text-sm text-amber-700">
                This is a demo application. Make sure you have configured your Google OAuth credentials and OpenAI API key in the backend configuration.
              </p>
            </div>

            {/* Debug Component (temporary) */}
            <div className="mt-4">
              <DebugAuth />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
