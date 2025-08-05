import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, User, Clock, Sparkles, MessageSquare, Send, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

import LoadingSpinner from '../components/LoadingSpinner';
import ReplyBox from '../components/ReplyBox';
import { emailService, aiService } from '../services/authService';

const EmailView = ({ user }) => {
  const { emailId } = useParams();
  const [email, setEmail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [showReplyBox, setShowReplyBox] = useState(false);

  useEffect(() => {
    if (emailId) {
      loadEmailDetail();
    }
  }, [emailId]);

  const loadEmailDetail = async () => {
    try {
      setLoading(true);
      const emailData = await emailService.getEmailDetail(emailId);
      setEmail(emailData);
      
      // Mark as read
      if (!emailData.is_read) {
        await emailService.markAsRead(emailId);
        setEmail(prev => ({ ...prev, is_read: true }));
      }
    } catch (error) {
      console.error('Failed to load email:', error);
      toast.error('Failed to load email');
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    try {
      setSummaryLoading(true);
      const result = await aiService.summarizeEmail({
        email_id: emailId,
        max_length: 200
      });
      setSummary(result);
      toast.success('Email summarized successfully');
    } catch (error) {
      console.error('Failed to summarize email:', error);
      toast.error('Failed to summarize email');
    } finally {
      setSummaryLoading(false);
    }
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  const extractSenderName = (sender) => {
    try {
      const match = sender.match(/^([^<]+)/);
      return match ? match[1].trim() : sender;
    } catch {
      return sender;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-gray-600">Loading email...</p>
        </div>
      </div>
    );
  }

  if (!email) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Email not found</h3>
        <p className="text-gray-600 mb-4">The email you're looking for doesn't exist or has been deleted.</p>
        <Link
          to="/dashboard"
          className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-700"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Dashboard</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/dashboard"
          className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Inbox</span>
        </Link>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          {/* Email Header */}
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-start space-x-4 flex-1">
              <div className="bg-gray-100 p-3 rounded-full">
                <User className="h-6 w-6 text-gray-600" />
              </div>
              <div className="flex-1">
                <h1 className="text-xl font-bold text-gray-900 mb-2">
                  {email.subject}
                </h1>
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">From:</span> {extractSenderName(email.sender)}
                  </div>
                  <div>
                    <span className="font-medium">To:</span> {email.recipient}
                  </div>
                  <div className="flex items-center space-x-1">
                    <Clock className="h-4 w-4" />
                    <span>{formatDate(email.date)}</span>
                  </div>
                </div>
              </div>
            </div>
            
            {!email.is_read && (
              <span className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                New
              </span>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3 mb-6 pb-6 border-b">
            <button
              onClick={handleSummarize}
              disabled={summaryLoading || summary}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {summaryLoading ? (
                <LoadingSpinner size="small" />
              ) : (
                <Sparkles className="h-5 w-5" />
              )}
              <span>
                {summary ? 'Summarized' : summaryLoading ? 'Summarizing...' : 'Summarize with AI'}
              </span>
            </button>

            <button
              onClick={() => setShowReplyBox(!showReplyBox)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
            >
              <MessageSquare className="h-5 w-5" />
              <span>{showReplyBox ? 'Hide Reply' : 'Reply with AI'}</span>
            </button>
          </div>

          {/* AI Summary */}
          {summary && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-6">
              <div className="flex items-center space-x-2 mb-4">
                <Sparkles className="h-5 w-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-blue-900">AI Summary</h3>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-blue-900 mb-2">Summary</h4>
                  <p className="text-blue-800">{summary.summary}</p>
                </div>

                {summary.key_points && summary.key_points.length > 0 && (
                  <div>
                    <h4 className="font-medium text-blue-900 mb-2">Key Points</h4>
                    <ul className="space-y-1">
                      {summary.key_points.map((point, index) => (
                        <li key={index} className="flex items-start text-blue-800">
                          <span className="text-blue-500 mr-2 mt-1">•</span>
                          <span>{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="flex items-center justify-between text-sm text-blue-700 bg-blue-100 rounded-lg p-3">
                  <div>
                    <span className="font-medium">Original:</span> {summary.original_length} chars
                  </div>
                  <div>
                    <span className="font-medium">Summary:</span> {summary.summary_length} chars
                  </div>
                  <div>
                    <span className="font-medium">Compression:</span> {summary.compression_ratio}%
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Email Body */}
          <div className="prose max-w-none">
            <div className="bg-gray-50 rounded-lg p-6">
              <div 
                className="email-content whitespace-pre-wrap text-gray-900"
                dangerouslySetInnerHTML={{ __html: email.body.replace(/\n/g, '<br>') }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Reply Box */}
      {showReplyBox && (
        <div className="mb-6">
          <ReplyBox
            originalEmail={email}
            onSend={(replyData) => {
              toast.success('Reply sent successfully!');
              setShowReplyBox(false);
            }}
            onCancel={() => setShowReplyBox(false)}
          />
        </div>
      )}
    </div>
  );
};

export default EmailView;
