import React from 'react';

const DebugAuth = () => {
  const checkTokens = () => {
    const accessToken = localStorage.getItem('access_token');
    const authToken = localStorage.getItem('auth_token');
    
    console.log('=== TOKEN DEBUG ===');
    console.log('Access Token:', accessToken ? 'Present' : 'Missing');
    console.log('Auth Token:', authToken ? 'Present' : 'Missing');
    
    if (authToken) {
      try {
        const payload = JSON.parse(atob(authToken.split('.')[1]));
        console.log('JWT Payload:', payload);
      } catch (e) {
        console.error('JWT Decode Error:', e);
      }
    }
    
    console.log('Current URL:', window.location.href);
    console.log('URL Params:', window.location.search);
    console.log('===================');
  };

  const clearTokens = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('auth_token');
    console.log('Tokens cleared');
    window.location.reload();
  };

  return (
    <div className="p-4 bg-yellow-100 border border-yellow-400 rounded">
      <h3 className="font-bold text-yellow-800">Authentication Debug</h3>
      <div className="mt-2 space-x-2">
        <button 
          onClick={checkTokens}
          className="px-3 py-1 bg-blue-500 text-white rounded text-sm"
        >
          Check Tokens
        </button>
        <button 
          onClick={clearTokens}
          className="px-3 py-1 bg-red-500 text-white rounded text-sm"
        >
          Clear Tokens
        </button>
      </div>
    </div>
  );
};

export default DebugAuth;
