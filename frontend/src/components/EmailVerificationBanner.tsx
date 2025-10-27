/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** EmailVerificationBanner
 */

import React, { useState } from 'react';
import { API_BASE } from '../utils/helper';

interface EmailVerificationBannerProps {
  user: {
    email?: string;
    email_verified?: boolean;
  } | null;
  onVerificationSent?: () => void;
}

const EmailVerificationBanner: React.FC<EmailVerificationBannerProps> = ({
  user,
  onVerificationSent,
}) => {
  const [isResending, setIsResending] = useState(false);
  const [resendMessage, setResendMessage] = useState<{
    type: 'success' | 'error';
    text: string;
  } | null>(null);

  // Don't show banner if user is verified or user data not loaded
  if (!user || user.email_verified) {
    return null;
  }

  const handleResendVerification = async () => {
    setIsResending(true);
    setResendMessage(null);

    try {
      const token = localStorage.getItem('access');
      if (!token) {
        setResendMessage({ type: 'error', text: 'Please log in again' });
        return;
      }

      const response = await fetch(`${API_BASE}/auth/resend-verification/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setResendMessage({
          type: 'success',
          text: 'Verification email sent! Please check your inbox.',
        });
        if (onVerificationSent) {
          onVerificationSent();
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        setResendMessage({
          type: 'error',
          text: errorData.message || errorData.detail || 'Failed to send verification email',
        });
      }
    } catch (error) {
      console.error('Error resending verification:', error);
      setResendMessage({
        type: 'error',
        text: 'Network error. Please try again.',
      });
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="mb-6 rounded-lg border-2 border-yellow-500 bg-yellow-50 p-4 shadow-md dark:border-yellow-600 dark:bg-yellow-900/20">
      <div className="flex items-start">
        {/* Warning Icon */}
        <div className="flex-shrink-0">
          <svg
            className="h-6 w-6 text-yellow-600 dark:text-yellow-500"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="2"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
            />
          </svg>
        </div>

        {/* Content */}
        <div className="ml-3 flex-1">
          <h3 className="text-lg font-semibold text-yellow-800 dark:text-yellow-300">
            📧 Email Verification Required
          </h3>
          <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-400">
            <p className="mb-2">
              <strong>Your account is not verified yet.</strong> To use AREA services and create
              automations, you must verify your email address.
            </p>
            <p className="mb-3">
              We sent a verification link to <strong>{user.email || 'your email'}</strong>. Please
              check your inbox (and spam folder) and click the link to activate your account.
            </p>

            {/* Resend Message */}
            {resendMessage && (
              <div
                className={`mb-3 rounded p-2 ${
                  resendMessage.type === 'success'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                    : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                }`}
              >
                {resendMessage.text}
              </div>
            )}

            {/* Resend Button */}
            <button
              onClick={handleResendVerification}
              disabled={isResending}
              className="inline-flex items-center rounded-md bg-yellow-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-yellow-700 dark:hover:bg-yellow-600"
            >
              {isResending ? (
                <>
                  <svg
                    className="-ml-1 mr-2 h-4 w-4 animate-spin text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Sending...
                </>
              ) : (
                <>
                  <svg
                    className="-ml-1 mr-2 h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth="2"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"
                    />
                  </svg>
                  Resend Verification Email
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailVerificationBanner;
