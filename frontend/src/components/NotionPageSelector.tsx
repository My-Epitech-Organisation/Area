/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** NotionPageSelector - GitHub App-like page/database selector
 */

import React, { useEffect, useState } from 'react';
import { API_BASE } from '../utils/helper';

interface NotionPage {
  page_id: string;
  page_type: 'page' | 'database';
  title: string;
  workspace_id: string;
  icon: {
    type: 'emoji' | 'external' | 'file';
    emoji?: string;
    external?: { url: string };
    file?: { url: string };
  } | null;
  url: string;
  is_accessible: boolean;
  updated_at: string;
}

interface NotionPageSelectorProps {
  value?: string; // Selected page_id or database_id
  onChange: (pageId: string, pageType: 'page' | 'database', title: string) => void;
  filterType?: 'page' | 'database' | 'all'; // Filter by type
  label?: string;
  placeholder?: string;
  required?: boolean;
}

const NotionPageSelector: React.FC<NotionPageSelectorProps> = ({
  value,
  onChange,
  filterType = 'all',
  label,
  placeholder = 'Select a Notion page or database',
  required = false,
}) => {
  const [pages, setPages] = useState<NotionPage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchPages();
  }, [filterType]);

  const fetchPages = async () => {
    try {
      const token = localStorage.getItem('access');
      if (!token) {
        setError('Not authenticated');
        setLoading(false);
        return;
      }

      const params = new URLSearchParams();
      if (filterType !== 'all') {
        params.append('type', filterType);
      }

      const response = await fetch(`${API_BASE}/api/notion-pages/?${params}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPages(data.pages || []);
        setError(null);
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.message || 'Failed to load Notion pages');
      }
    } catch (err) {
      console.error('Error fetching Notion pages:', err);
      setError('Connection error');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const token = localStorage.getItem('access');
      if (!token) return;

      const response = await fetch(`${API_BASE}/api/notion-pages/refresh/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        await fetchPages();
      }
    } catch (err) {
      console.error('Error refreshing pages:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const handleSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const pageId = e.target.value;
    const selectedPage = pages.find((p) => p.page_id === pageId);
    
    if (selectedPage) {
      onChange(pageId, selectedPage.page_type, selectedPage.title);
    }
  };

  const renderIcon = (icon: NotionPage['icon']) => {
    if (!icon) return '📄';
    
    if (icon.type === 'emoji' && icon.emoji) {
      return icon.emoji;
    }
    
    return '📄';
  };

  const filteredPages = searchQuery
    ? pages.filter((p) =>
        p.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : pages;

  if (loading) {
    return (
      <div className="mb-4">
        {label && (
          <label className="block text-sm font-medium text-gray-300 mb-2">
            {label} {required && <span className="text-red-400">*</span>}
          </label>
        )}
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          Loading your Notion pages...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mb-4">
        {label && (
          <label className="block text-sm font-medium text-gray-300 mb-2">
            {label} {required && <span className="text-red-400">*</span>}
          </label>
        )}
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
          <p className="text-sm text-red-300 mb-2">⚠️ {error}</p>
          <button
            onClick={fetchPages}
            className="text-xs text-blue-400 hover:text-blue-300 underline"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  if (pages.length === 0) {
    return (
      <div className="mb-4">
        {label && (
          <label className="block text-sm font-medium text-gray-300 mb-2">
            {label} {required && <span className="text-red-400">*</span>}
          </label>
        )}
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
          <p className="text-sm text-yellow-200 mb-2">
            📭 No Notion pages found
          </p>
          <p className="text-xs text-gray-400 mb-3">
            You need to share pages/databases with the AREA integration during OAuth authorization.
          </p>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white text-xs rounded-lg transition-colors"
          >
            {refreshing ? 'Refreshing...' : 'Refresh from Notion'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium text-gray-300 mb-2">
          {label} {required && <span className="text-red-400">*</span>}
        </label>
      )}
      
      <div className="space-y-2">
        {/* Search input */}
        {pages.length > 5 && (
          <input
            type="text"
            placeholder="🔍 Search pages..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:border-blue-500"
          />
        )}

        {/* Select dropdown */}
        <select
          value={value || ''}
          onChange={handleSelect}
          required={required}
          className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500 appearance-none cursor-pointer hover:bg-white/10 transition-colors"
        >
          <option value="" className="bg-gray-800 text-gray-400">
            {placeholder}
          </option>
          {filteredPages.map((page) => (
            <option
              key={page.page_id}
              value={page.page_id}
              className="bg-gray-800 text-white"
            >
              {renderIcon(page.icon)} {page.title} ({page.page_type})
            </option>
          ))}
        </select>

        {/* Helper text */}
        <div className="flex items-center justify-between">
          <p className="text-xs text-gray-500">
            {filteredPages.length} {filterType !== 'all' ? filterType : 'item'}
            {filteredPages.length !== 1 ? 's' : ''} available
          </p>
          <button
            type="button"
            onClick={handleRefresh}
            disabled={refreshing}
            className="text-xs text-blue-400 hover:text-blue-300 underline disabled:text-gray-600"
            title="Refresh from Notion API"
          >
            {refreshing ? '⟳ Refreshing...' : '⟳ Refresh'}
          </button>
        </div>

        {/* Selected page info */}
        {value && (
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-2">
            <p className="text-xs text-blue-200">
              ✓ Selected: {pages.find((p) => p.page_id === value)?.title}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default NotionPageSelector;
