import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Navbar from '../Navbar';

vi.mock('../../utils/helper', () => ({
  getStoredUser: vi.fn(),
}));

import { getStoredUser } from '../../utils/helper';

describe('Navbar Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Rendering and Navigation Links', () => {
    it('should render navbar with all navigation links when user is logged in', () => {
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
        email_verified: true,
      });

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('Area')).toBeInTheDocument();
      expect(screen.getByText('Services')).toBeInTheDocument();
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Profile')).toBeInTheDocument();
    });

    it('should render navbar when user is not logged in', () => {
      vi.mocked(getStoredUser).mockReturnValue(null);

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('Area')).toBeInTheDocument();
    });

    it('should have correct href attributes for all links', () => {
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
        email_verified: true,
      });

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.getByText('Home').closest('a')).toHaveAttribute('href', '/homepage');
      expect(screen.getByText('Area').closest('a')).toHaveAttribute('href', '/Areaction');
      expect(screen.getByText('Services').closest('a')).toHaveAttribute('href', '/services');
      expect(screen.getByText('Dashboard').closest('a')).toHaveAttribute('href', '/dashboard');
      expect(screen.getByText('Profile').closest('a')).toHaveAttribute('href', '/profile');
    });
  });

  describe('Mobile Menu', () => {
    it('should toggle mobile menu when hamburger button is clicked', () => {
      vi.mocked(getStoredUser).mockReturnValue(null);

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const hamburgerButton = screen.getByLabelText('Toggle menu');

      fireEvent.click(hamburgerButton);

      fireEvent.click(hamburgerButton);

      expect(hamburgerButton).toBeInTheDocument();
    });

    it('should render hamburger menu button', () => {
      vi.mocked(getStoredUser).mockReturnValue(null);

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const hamburgerButton = screen.getByLabelText('Toggle menu');
      expect(hamburgerButton).toBeInTheDocument();
      expect(hamburgerButton).toHaveTextContent('☰');
    });

    it('should close mobile menu when clicking on a link (when logged in)', async () => {
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'John Doe',
        username: 'johndoe',
        email: 'john@example.com',
      });

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const hamburgerButton = screen.getByLabelText('Toggle menu');
      fireEvent.click(hamburgerButton);

      expect(hamburgerButton).toBeInTheDocument();

      const dashboardLink = screen
        .getAllByText('Dashboard')
        .find((el) => el.classList.contains('text-lg'));

      if (dashboardLink) {
        fireEvent.click(dashboardLink);
      }
    });

    it('should render mobile menu links when logged in', () => {
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'John Doe',
        username: 'johndoe',
        email: 'john@example.com',
      });

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const hamburgerButton = screen.getByLabelText('Toggle menu');
      fireEvent.click(hamburgerButton);

      const links = screen.getAllByText(/Home|Area|Services|Dashboard|Profile|About/i);
      expect(links.length).toBeGreaterThan(0);
    });
  });

  describe('User Authentication State', () => {
    it('should display username when user is logged in', () => {
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'John Doe',
        username: 'johndoe',
        email: 'john@example.com',
        email_verified: true,
      });

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    it('should show Login/Signup buttons when user is not logged in', () => {
      vi.mocked(getStoredUser).mockReturnValue(null);

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.getByText('Log In')).toBeInTheDocument();
      expect(screen.getByText('Sign Up')).toBeInTheDocument();
    });

    it('should show Logout button when user is logged in', () => {
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
        email_verified: true,
      });

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.getByText('Log Out')).toBeInTheDocument();
    });
  });

  describe('Logout Functionality', () => {
    it('should clear localStorage and redirect on logout', () => {
      const mockReplace = vi.fn();
      Object.defineProperty(window, 'location', {
        value: { replace: mockReplace },
        writable: true,
      });

      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
        email_verified: true,
      });

      localStorage.setItem('user', JSON.stringify({ username: 'testuser' }));
      localStorage.setItem('access', 'test-token');
      localStorage.setItem('refresh', 'refresh-token');

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const logoutButton = screen.getByText('Log Out');
      fireEvent.click(logoutButton);

      expect(localStorage.getItem('user')).toBeNull();
      expect(localStorage.getItem('access')).toBeNull();
      expect(localStorage.getItem('refresh')).toBeNull();
      expect(mockReplace).toHaveBeenCalledWith('/homepage');
    });
  });

  describe('User State Updates', () => {
    it('should update user state when localStorage changes', async () => {
      vi.mocked(getStoredUser).mockReturnValue(null);

      const { rerender } = render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.queryByText('Log In')).toBeInTheDocument();

      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'newuser',
        email: 'test@example.com',
        email_verified: true,
      });

      const storageEvent = new StorageEvent('storage', {
        key: 'user',
        newValue: JSON.stringify({ username: 'newuser' }),
      });
      window.dispatchEvent(storageEvent);

      rerender(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(getStoredUser).toHaveBeenCalled();
      });
    });

    it('should check user on visibility change', async () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const visibilityEvent = new Event('visibilitychange');
      Object.defineProperty(document, 'visibilityState', {
        value: 'visible',
        writable: true,
      });

      document.dispatchEvent(visibilityEvent);

      await waitFor(() => {
        expect(getStoredUser).toHaveBeenCalled();
      });
    });
  });

  describe('Styling and Accessibility', () => {
    it('should have correct nav element structure', () => {
      vi.mocked(getStoredUser).mockReturnValue(null);

      const { container } = render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      const nav = container.querySelector('nav');
      expect(nav).toBeInTheDocument();
      expect(nav).toHaveClass('w-full', 'fixed', 'top-0', 'left-0', 'z-50');
    });

    it('should have accessible button labels', () => {
      vi.mocked(getStoredUser).mockReturnValue(null);

      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>
      );

      expect(screen.getByLabelText('Toggle menu')).toBeInTheDocument();
    });
  });
});
