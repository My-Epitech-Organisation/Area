import React from 'react';

interface OAuthBadgeProps {
  isConnected: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const OAuthBadge: React.FC<OAuthBadgeProps> = ({ isConnected, size = 'sm' }) => {
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  const iconSizes = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5',
  };

  if (isConnected) {
    return (
      <div
        className={`inline-flex items-center gap-1.5 bg-green-500/20 text-green-300 rounded-full border border-green-500/30 ${sizeClasses[size]} font-medium`}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className={iconSizes[size]}
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clipRule="evenodd"
          />
        </svg>
        <span>Connected</span>
      </div>
    );
  }

  return (
    <div
      className={`inline-flex items-center gap-1.5 bg-gray-500/20 text-gray-400 rounded-full border border-gray-500/30 ${sizeClasses[size]} font-medium`}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className={iconSizes[size]}
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293z"
          clipRule="evenodd"
        />
      </svg>
      <span>Not connected</span>
    </div>
  );
};

export default OAuthBadge;
