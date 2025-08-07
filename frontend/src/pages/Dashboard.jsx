import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, Search, Filter, Sparkles, Mail, Clock } from 'lucide-react';
import toast from 'react-hot-toast';

import EmailCard from '../components/EmailCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { emailService, aiService } from '../services/authService';

const Dashboard = ({ user }) => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [summaryLoading, setSummaryLoading] = useState({});

  const loadEmails = useCallback(async (showToast = false) => {
    try {
      if (showToast) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      const params = {};
      if (searchQuery) params.query = searchQuery;
      if (filterType !== 'all') {
        if (filterType === 'unread') params.query = 'is:unread';
        if (filterType === 'important') params.query = 'is:important';
      }

      const emailData = await emailService.getEmails(params);
      setEmails(emailData);

      if (showToast) {
        toast.success('Emails refreshed');
      }
    } catch (error) {
      console.error('Failed to load emails:', error);
      toast.error('Failed to load emails');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [searchQuery, filterType]);

  useEffect(() => {
    loadEmails();
  }, [loadEmails]);

  const handleSearch = () => {
    loadEmails();
  };

  const handleFilterChange = (newFilter) => {
    setFilterType(newFilter);
    setTimeout(() => loadEmails(), 100);
  };

  const handleSummarizeEmail = async (emailId) => {
    try {
      setSummaryLoading(prev => ({ ...prev, [emailId]: true }));
      
      const summary = await aiService.summarizeEmail({
        email_id: emailId,
        max_length: 100
      });

      // Update the email with summary
      setEmails(prev => prev.map(email => 
        email.id === emailId 
          ? { ...email, summary: summary.summary, key_points: summary.key_points }
          : email
      ));

      toast.success('Email summarized successfully');
    } catch (error) {
      console.error('Failed to summarize email:', error);
      toast.error('Failed to summarize email');
    } finally {
      setSummaryLoading(prev => ({ ...prev, [emailId]: false }));
    }
  };

  const handleMarkAsRead = async (emailId) => {
    try {
      await emailService.markAsRead(emailId);
      setEmails(prev => prev.map(email => 
        email.id === emailId ? { ...email, is_read: true } : email
      ));
    } catch (error) {
      console.error('Failed to mark as read:', error);
      toast.error('Failed to mark as read');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-gray-600">Loading your emails...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {user?.name?.split(' ')[0] || 'there'}!
            </h1>
            <p className="text-gray-600">
              Manage your emails with AI-powered assistance
            </p>
          </div>
          <button
            onClick={() => loadEmails(true)}
            disabled={refreshing}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="flex items-center">
              <div className="bg-blue-100 p-3 rounded-lg">
                <Mail className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Emails</p>
                <p className="text-2xl font-bold text-gray-900">{emails.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="flex items-center">
              <div className="bg-yellow-100 p-3 rounded-lg">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Unread</p>
                <p className="text-2xl font-bold text-gray-900">
                  {emails.filter(email => !email.is_read).length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="flex items-center">
              <div className="bg-green-100 p-3 rounded-lg">
                <Sparkles className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">AI Summaries</p>
                <p className="text-2xl font-bold text-gray-900">
                  {emails.filter(email => email.summary).length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search emails..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <button
              onClick={handleSearch}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Search
            </button>

            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={filterType}
                onChange={(e) => handleFilterChange(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Emails</option>
                <option value="unread">Unread</option>
                <option value="important">Important</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Email List */}
      <div className="space-y-4">
        {emails.length === 0 ? (
          <div className="text-center py-12">
            <Mail className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No emails found</h3>
            <p className="text-gray-600">
              {searchQuery || filterType !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'Your inbox is empty'
              }
            </p>
          </div>
        ) : (
          emails.map((email) => (
            <EmailCard
              key={email.id}
              email={email}
              onSummarize={() => handleSummarizeEmail(email.id)}
              onMarkAsRead={() => handleMarkAsRead(email.id)}
              summaryLoading={summaryLoading[email.id]}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default Dashboard;
