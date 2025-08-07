import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, User, Sparkles, MessageSquare, Eye } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

const EmailCard = ({ email, onSummarize, onMarkAsRead, summaryLoading }) => {
  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = Math.abs(now - date);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) return 'Today';
      if (diffDays === 2) return 'Yesterday';
      if (diffDays <= 7) return `${diffDays} days ago`;
      
      return date.toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const extractSenderName = (sender) => {
    try {
      // Extract name from "Name <email@domain.com>" format
      const match = sender.match(/^([^<]+)/);
      return match ? match[1].trim() : sender;
    } catch {
      return sender;
    }
  };

  return (
    <div className={`bg-white rounded-xl shadow-sm border transition-all duration-200 hover:shadow-md hover:border-gray-300 ${
      !email.is_read ? 'border-l-4 border-l-blue-500' : ''
    }`}>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start space-x-3 flex-1 min-w-0">
            <div className="bg-gray-100 p-2 rounded-full">
              <User className="h-4 w-4 text-gray-600" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-1">
                <h3 className="text-sm font-medium text-gray-900 truncate">
                  {extractSenderName(email.sender)}
                </h3>
                {!email.is_read && (
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                    New
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500">{email.sender}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 text-xs text-gray-500">
            <Clock className="h-3 w-3" />
            <span>{formatDate(email.date)}</span>
          </div>
        </div>

        {/* Subject */}
        <Link to={`/email/${email.id}`}>
          <h2 className="text-lg font-semibold text-gray-900 mb-2 hover:text-blue-600 transition-colors line-clamp-2">
            {email.subject}
          </h2>
        </Link>

        {/* Snippet */}
        <p className="text-gray-600 text-sm mb-4 line-clamp-3">
          {email.snippet}
        </p>

        {/* AI Summary */}
        {email.summary && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="flex items-center space-x-2 mb-2">
              <Sparkles className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-900">AI Summary</span>
            </div>
            <p className="text-sm text-blue-800 mb-2">{email.summary}</p>
            {email.key_points && email.key_points.length > 0 && (
              <div>
                <p className="text-xs font-medium text-blue-900 mb-1">Key Points:</p>
                <ul className="text-xs text-blue-700 space-y-1">
                  {email.key_points.map((point, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-blue-500 mr-1">•</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={onSummarize}
              disabled={summaryLoading || email.summary}
              className="flex items-center space-x-2 px-3 py-1.5 text-sm bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {summaryLoading ? (
                <LoadingSpinner size="small" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              <span>
                {email.summary ? 'Summarized' : summaryLoading ? 'Summarizing...' : 'Summarize'}
              </span>
            </button>

            <Link
              to={`/email/${email.id}`}
              className="flex items-center space-x-2 px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
            >
              <MessageSquare className="h-4 w-4" />
              <span>Reply</span>
            </Link>
          </div>

          <div className="flex items-center space-x-2">
            {!email.is_read && (
              <button
                onClick={onMarkAsRead}
                className="flex items-center space-x-1 px-2 py-1 text-xs text-gray-600 hover:text-gray-800 transition-colors"
              >
                <Eye className="h-3 w-3" />
                <span>Mark read</span>
              </button>
            )}
            
            <span className="text-xs text-gray-400">
              Thread ID: {email.thread_id?.slice(-8)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailCard;
