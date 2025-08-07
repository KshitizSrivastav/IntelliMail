import React, { useState } from 'react';
import { Send, X, Sparkles, RefreshCw, Wand2 } from 'lucide-react';
import toast from 'react-hot-toast';

import LoadingSpinner from './LoadingSpinner';
import { aiService, emailService } from '../services/authService';

const ReplyBox = ({ originalEmail, onSend, onCancel }) => {
  const [replyText, setReplyText] = useState('');
  const [selectedTone, setSelectedTone] = useState('professional');
  const [selectedLength, setSelectedLength] = useState('medium');
  const [generating, setGenerating] = useState(false);
  const [sending, setSending] = useState(false);
  const [customInstructions, setCustomInstructions] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const toneOptions = [
    { id: 'formal', name: 'Formal', description: 'Professional and respectful' },
    { id: 'friendly', name: 'Friendly', description: 'Warm and approachable' },
    { id: 'casual', name: 'Casual', description: 'Relaxed and informal' },
    { id: 'professional', name: 'Professional', description: 'Balanced and business-like' },
    { id: 'apologetic', name: 'Apologetic', description: 'Express regret and responsibility' },
    { id: 'urgent', name: 'Urgent', description: 'Convey importance and time-sensitivity' },
    { id: 'grateful', name: 'Grateful', description: 'Express appreciation' },
    { id: 'polite', name: 'Polite', description: 'Extremely courteous' }
  ];

  const lengthOptions = [
    { id: 'short', name: 'Short', description: '50-100 words' },
    { id: 'medium', name: 'Medium', description: '100-200 words' },
    { id: 'long', name: 'Long', description: '200-300 words' }
  ];

  const generateReply = async () => {
    try {
      setGenerating(true);
      
      const replyData = await aiService.generateReply({
        email_id: originalEmail.id,
        tone: selectedTone,
        length: selectedLength,
        custom_instructions: customInstructions || null
      });

      setReplyText(replyData.generated_reply);
      toast.success('Reply generated successfully!');
    } catch (error) {
      console.error('Failed to generate reply:', error);
      toast.error('Failed to generate reply');
    } finally {
      setGenerating(false);
    }
  };

  const refineReply = async () => {
    if (!replyText.trim()) {
      toast.error('Please generate or write a reply first');
      return;
    }

    try {
      setGenerating(true);
      
      const refinedData = await aiService.refineReply(
        replyText,
        selectedTone,
        customInstructions || null
      );

      setReplyText(refinedData.refined_reply);
      toast.success('Reply refined successfully!');
    } catch (error) {
      console.error('Failed to refine reply:', error);
      toast.error('Failed to refine reply');
    } finally {
      setGenerating(false);
    }
  };

  const sendReply = async () => {
    if (!replyText.trim()) {
      toast.error('Please write a reply');
      return;
    }

    try {
      setSending(true);
      
      const subject = originalEmail.subject.startsWith('Re:') 
        ? originalEmail.subject 
        : `Re: ${originalEmail.subject}`;

      await emailService.sendEmail({
        to: originalEmail.sender,
        subject: subject,
        body: replyText,
        reply_to_id: originalEmail.id
      });

      onSend({
        to: originalEmail.sender,
        subject: subject,
        body: replyText
      });
    } catch (error) {
      console.error('Failed to send reply:', error);
      toast.error('Failed to send reply');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Compose Reply</h3>
          <button
            onClick={onCancel}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Reply Context */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <div className="text-sm text-gray-600">
            <span className="font-medium">Replying to:</span> {originalEmail.subject}
          </div>
          <div className="text-sm text-gray-600">
            <span className="font-medium">From:</span> {originalEmail.sender}
          </div>
        </div>

        {/* Tone and Length Selectors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Tone Style
            </label>
            <div className="space-y-2">
              {toneOptions.map((tone) => (
                <label key={tone.id} className="flex items-center">
                  <input
                    type="radio"
                    name="tone"
                    value={tone.id}
                    checked={selectedTone === tone.id}
                    onChange={(e) => setSelectedTone(e.target.value)}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <div className="ml-3">
                    <div className="text-sm font-medium text-gray-900">{tone.name}</div>
                    <div className="text-xs text-gray-500">{tone.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Reply Length
            </label>
            <div className="space-y-2">
              {lengthOptions.map((length) => (
                <label key={length.id} className="flex items-center">
                  <input
                    type="radio"
                    name="length"
                    value={length.id}
                    checked={selectedLength === length.id}
                    onChange={(e) => setSelectedLength(e.target.value)}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <div className="ml-3">
                    <div className="text-sm font-medium text-gray-900">{length.name}</div>
                    <div className="text-xs text-gray-500">{length.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Advanced Options */}
        <div className="mb-6">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-blue-600 hover:text-blue-700 flex items-center space-x-1"
          >
            <span>{showAdvanced ? 'Hide' : 'Show'} Advanced Options</span>
          </button>

          {showAdvanced && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Instructions
              </label>
              <textarea
                value={customInstructions}
                onChange={(e) => setCustomInstructions(e.target.value)}
                placeholder="Add specific instructions for the AI (e.g., 'Include a meeting request', 'Mention our previous conversation about...')"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                rows={3}
              />
            </div>
          )}
        </div>

        {/* AI Generation Buttons */}
        <div className="flex flex-wrap gap-3 mb-6">
          <button
            onClick={generateReply}
            disabled={generating}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {generating ? (
              <LoadingSpinner size="small" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            <span>Generate AI Reply</span>
          </button>

          {replyText && (
            <button
              onClick={refineReply}
              disabled={generating}
              className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {generating ? (
                <LoadingSpinner size="small" />
              ) : (
                <Wand2 className="h-4 w-4" />
              )}
              <span>Refine Reply</span>
            </button>
          )}
        </div>

        {/* Reply Editor */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Reply Content
          </label>
          <textarea
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            placeholder="Your reply will appear here after AI generation, or you can type manually..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm resize-none"
            rows={12}
          />
          <div className="mt-2 text-xs text-gray-500">
            {replyText.length} characters • {replyText.split(/\s+/).filter(Boolean).length} words
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Cancel
          </button>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setReplyText('')}
              className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Clear</span>
            </button>

            <button
              onClick={sendReply}
              disabled={sending || !replyText.trim()}
              className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {sending ? (
                <LoadingSpinner size="small" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              <span>{sending ? 'Sending...' : 'Send Reply'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReplyBox;
