import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Services from '../Services';

vi.mock('../../utils/helper', () => ({
  API_BASE: 'http://localhost:8000/api',
  getStoredUser: vi.fn(),
  fetchUserData: vi.fn(),
}));

vi.mock('../../assets/*.{png,jpg,jpeg,svg,gif}', () => ({}));

const mockAboutJson = {
  server: {
    services: [
      {
        id: 1,
        name: 'GitHub',
        Name: 'GitHub',
        description: 'Connect to GitHub',
        logo: 'github_logo.png',
      },
      {
        id: 2,
        name: 'Gmail',
        Name: 'Gmail',
        description: 'Email service',
        logo: 'gmail_logo.png',
      },
      {
        id: 3,
        name: 'Timer',
        Name: 'Timer',
        description: 'Time-based triggers',
        logo: null,
      },
      {
        id: 4,
        name: 'Spotify',
        Name: 'Spotify',
        description: 'Music streaming',
        logo: 'spotify_logo.png',
      },
    ],
  },
};

describe('Services Page', () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn((url) => {
      if (url.includes('/about.json')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAboutJson),
        } as Response);
      }
      return Promise.reject(new Error('Not found'));
    });

    localStorage.clear();

    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  const renderPage = () => {
    return render(
      <BrowserRouter>
        <Services />
      </BrowserRouter>
    );
  };

  describe('Basic Rendering', () => {
    it('should render services page title', async () => {
      renderPage();

      expect(screen.getByText('Services')).toBeInTheDocument();
      expect(screen.getByText(/explore available action/i)).toBeInTheDocument();
    });

    it('should display loading state initially', () => {
      renderPage();

      expect(screen.queryByText('GitHub')).not.toBeInTheDocument();
    });

    it('should load and display services from about.json', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('GitHub')).toBeInTheDocument();
      });

      expect(screen.getByText('Gmail')).toBeInTheDocument();
      expect(screen.getByText('Timer')).toBeInTheDocument();
      expect(screen.getByText('Spotify')).toBeInTheDocument();
    });

    it('should display service descriptions', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Connect to GitHub')).toBeInTheDocument();
      });

      expect(screen.getByText('Email service')).toBeInTheDocument();
      expect(screen.getByText('Time-based triggers')).toBeInTheDocument();
    });
  });

  describe('Search Functionality', () => {
    it('should have a search input', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search services/i)).toBeInTheDocument();
      });
    });

    it('should filter services based on search query', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('GitHub')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search services/i);
      fireEvent.change(searchInput, { target: { value: 'git' } });

      await waitFor(() => {
        expect(screen.getByText('GitHub')).toBeInTheDocument();
        expect(screen.queryByText('Gmail')).not.toBeInTheDocument();
      });
    });

    it('should show all services when search is cleared', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('GitHub')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search services/i);
      fireEvent.change(searchInput, { target: { value: 'git' } });

      await waitFor(() => {
        expect(screen.queryByText('Gmail')).not.toBeInTheDocument();
      });

      fireEvent.change(searchInput, { target: { value: '' } });

      await waitFor(() => {
        expect(screen.getByText('Gmail')).toBeInTheDocument();
      });
    });

    it('should be case-insensitive when filtering', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('GitHub')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search services/i);
      fireEvent.change(searchInput, { target: { value: 'GITHUB' } });

      await waitFor(() => {
        expect(screen.getByText('GitHub')).toBeInTheDocument();
      });
    });
  });

  describe('View Mode Toggle', () => {
    it('should have carousel and list view mode buttons', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Carousel')).toBeInTheDocument();
      });

      expect(screen.getByText('List')).toBeInTheDocument();
    });

    it('should start in list mode by default', async () => {
      renderPage();

      await waitFor(() => {
        const listButton = screen.getByText('List');
        expect(listButton.closest('button')).toHaveClass('bg-purple-600');
      });
    });

    it('should switch to carousel mode when clicked', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Carousel')).toBeInTheDocument();
      });

      const carouselButton = screen.getByText('Carousel');
      fireEvent.click(carouselButton);

      await waitFor(() => {
        expect(carouselButton.closest('button')).toHaveClass('bg-indigo-600');
      });
    });

    it('should switch back to list mode', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('List')).toBeInTheDocument();
      });

      const carouselButton = screen.getByText('Carousel');
      fireEvent.click(carouselButton);

      await waitFor(() => {
        expect(carouselButton.closest('button')).toHaveClass('bg-indigo-600');
      });

      const listButton = screen.getByText('List');
      fireEvent.click(listButton);

      await waitFor(() => {
        expect(listButton.closest('button')).toHaveClass('bg-purple-600');
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message when fetch fails', async () => {
      globalThis.fetch = vi.fn(() => Promise.reject(new Error('Network error')));

      renderPage();

      await waitFor(() => {
        expect(screen.getByText(/network error|failed to load/i)).toBeInTheDocument();
      });
    });

    it('should display error when about.json returns non-ok response', async () => {
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: false,
          status: 500,
        } as Response)
      );

      renderPage();

      await waitFor(() => {
        expect(screen.getByText(/http 500/i)).toBeInTheDocument();
      });
    });

    it('should handle malformed JSON gracefully', async () => {
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.reject(new Error('Invalid JSON')),
        } as Response)
      );

      renderPage();

      await waitFor(() => {
        expect(screen.getByText(/invalid json|failed to load/i)).toBeInTheDocument();
      });
    });
  });

  describe('Service History', () => {
    it('should display history section', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText(/recently visited|no services visited/i)).toBeInTheDocument();
      });
    });

    it('should load history from localStorage', async () => {
      const mockHistory = [
        {
          id: 5,
          Name: 'Discord',
          description: 'Chat app',
          logo: null,
        },
      ];

      localStorage.setItem('area_service_history', JSON.stringify(mockHistory));

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Discord')).toBeInTheDocument();
      });
    });

    it('should handle invalid history data in localStorage', async () => {
      localStorage.setItem('area_service_history', 'invalid json');

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Services')).toBeInTheDocument();
      });
    });

    it('should handle non-array history data', async () => {
      localStorage.setItem('area_service_history', JSON.stringify({ not: 'an array' }));

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Services')).toBeInTheDocument();
      });
    });
  });

  describe('Service Links', () => {
    it('should render links to service detail pages', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('GitHub')).toBeInTheDocument();
      });

      const githubLink = screen.getByText('GitHub').closest('a');
      expect(githubLink).toHaveAttribute('href', '/services/1');
    });

    it('should have links for all services', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('GitHub')).toBeInTheDocument();
      });

      const links = screen.getAllByRole('link');
      const serviceLinks = links.filter((link) =>
        link.getAttribute('href')?.startsWith('/services/')
      );

      expect(serviceLinks.length).toBeGreaterThan(0);
    });
  });

  describe('Internal Services Detection', () => {
    it('should identify timer as internal service', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Timer')).toBeInTheDocument();
      });

      expect(screen.getByText('Time-based triggers')).toBeInTheDocument();
    });
  });

  describe('Logo Resolution', () => {
    it('should handle services with logo URLs', async () => {
      const customServices = {
        server: {
          services: [
            {
              id: 1,
              name: 'CustomService',
              Name: 'CustomService',
              description: 'Custom',
              logo: 'https://example.com/logo.png',
            },
          ],
        },
      };

      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(customServices),
        } as Response)
      );

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('CustomService')).toBeInTheDocument();
      });
    });

    it('should handle services without logos', async () => {
      const servicesWithoutLogos = {
        server: {
          services: [
            {
              id: 1,
              name: 'NoLogoService',
              Name: 'NoLogoService',
              description: 'No logo',
              logo: null,
            },
          ],
        },
      };

      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(servicesWithoutLogos),
        } as Response)
      );

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('NoLogoService')).toBeInTheDocument();
      });
    });

    it('should handle protocol-relative URLs in logos', async () => {
      const servicesWithRelativeUrls = {
        server: {
          services: [
            {
              id: 1,
              name: 'RelativeURL',
              Name: 'RelativeURL',
              description: 'Relative',
              logo: '//example.com/logo.png',
            },
          ],
        },
      };

      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(servicesWithRelativeUrls),
        } as Response)
      );

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('RelativeURL')).toBeInTheDocument();
      });
    });
  });

  describe('User Integration', () => {
    it('should load user from localStorage', async () => {
      const { getStoredUser } = await import('../../utils/helper');
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
        email_verified: true,
      });

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Services')).toBeInTheDocument();
      });
    });

    it('should show email verification banner for unverified users', async () => {
      const { getStoredUser } = await import('../../utils/helper');
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
        email_verified: false,
      });

      renderPage();

      await waitFor(() => {
        expect(screen.getByText(/verify your email/i)).toBeInTheDocument();
      });
    });
  });

  describe('Window Focus Handling', () => {
    it('should refresh user data when window gains focus', async () => {
      const { getStoredUser, fetchUserData } = await import('../../utils/helper');
      const mockUser = {
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
        email_verified: false,
      };

      vi.mocked(getStoredUser).mockReturnValue(mockUser);
      vi.mocked(fetchUserData).mockResolvedValue({
        ...mockUser,
        email_verified: true,
      });

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Services')).toBeInTheDocument();
      });

      fireEvent.focus(window);

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });
  });

  describe('Responsive Design', () => {
    it('should adjust radius for mobile devices', async () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 500,
      });

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Services')).toBeInTheDocument();
      });
    });

    it('should work with desktop dimensions', async () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1920,
      });

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Services')).toBeInTheDocument();
      });
    });
  });
});
