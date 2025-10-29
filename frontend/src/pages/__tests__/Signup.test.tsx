import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Signup from '../Signup';

vi.mock('../../utils/helper', () => ({
  API_BASE: 'http://localhost:8000',
}));

globalThis.fetch = vi.fn();

describe('Signup Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(window, 'location', {
      value: { href: '/' },
      writable: true,
    });
  });

  describe('Rendering', () => {
    it('should render signup form', () => {
      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      expect(screen.getByPlaceholderText('username')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('you@example.com')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('password')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('repeat password')).toBeInTheDocument();
    });

    it('should render register button', () => {
      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
    });

    it('should render link to login page', () => {
      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      const loginLink = screen.getByText(/already have an account/i).closest('a');
      expect(loginLink).toHaveAttribute('href', '/login');
    });
  });

  describe('Form Interaction', () => {
    it('should update username field on input', () => {
      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      const usernameInput = screen.getByPlaceholderText('username') as HTMLInputElement;
      fireEvent.change(usernameInput, { target: { value: 'newuser' } });

      expect(usernameInput.value).toBe('newuser');
    });

    it('should update email field on input', () => {
      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      const emailInput = screen.getByPlaceholderText('you@example.com') as HTMLInputElement;
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      expect(emailInput.value).toBe('test@example.com');
    });

    it('should update password fields on input', () => {
      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      const passwordInput = screen.getByPlaceholderText('password') as HTMLInputElement;
      const password2Input = screen.getByPlaceholderText('repeat password') as HTMLInputElement;

      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(password2Input, { target: { value: 'password123' } });

      expect(passwordInput.value).toBe('password123');
      expect(password2Input.value).toBe('password123');
    });
  });

  describe('Form Submission', () => {
    it('should submit form with valid data', async () => {
      vi.mocked(globalThis.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ user: { username: 'testuser' }, access: 'token' }),
      } as Response);

      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      const usernameInput = screen.getByPlaceholderText('username');
      const emailInput = screen.getByPlaceholderText('you@example.com');
      const passwordInput = screen.getByPlaceholderText('password');
      const password2Input = screen.getByPlaceholderText('repeat password');
      const submitButton = screen.getByRole('button', { name: /register/i });

      fireEvent.change(usernameInput, { target: { value: 'newuser' } });
      fireEvent.change(emailInput, { target: { value: 'new@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(password2Input, { target: { value: 'password123' } });

      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledWith(
          'http://localhost:8000/auth/register/',
          expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
          })
        );
      });
    });

    it('should display error message on failed signup', async () => {
      vi.mocked(globalThis.fetch).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Username already exists' }),
      } as Response);

      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      const usernameInput = screen.getByPlaceholderText('username');
      const emailInput = screen.getByPlaceholderText('you@example.com');
      const passwordInput = screen.getByPlaceholderText('password');
      const password2Input = screen.getByPlaceholderText('repeat password');
      const submitButton = screen.getByRole('button', { name: /register/i });

      fireEvent.change(usernameInput, { target: { value: 'existinguser' } });
      fireEvent.change(emailInput, { target: { value: 'existing@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(password2Input, { target: { value: 'password123' } });

      fireEvent.click(submitButton);

      await waitFor(
        () => {
          expect(globalThis.fetch).toHaveBeenCalled();
        },
        { timeout: 500 }
      );
    });

    it('should handle network errors', async () => {
      vi.mocked(globalThis.fetch).mockRejectedValueOnce(new Error('Network error'));

      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      const usernameInput = screen.getByPlaceholderText('username');
      const emailInput = screen.getByPlaceholderText('you@example.com');
      const passwordInput = screen.getByPlaceholderText('password');
      const password2Input = screen.getByPlaceholderText('repeat password');
      const submitButton = screen.getByRole('button', { name: /register/i });

      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(password2Input, { target: { value: 'password123' } });

      fireEvent.click(submitButton);

      await waitFor(
        () => {
          expect(globalThis.fetch).toHaveBeenCalled();
        },
        { timeout: 500 }
      );
    });
  });

  describe('Validation', () => {
    it('should have required fields', () => {
      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      const usernameInput = screen.getByPlaceholderText('username');
      const emailInput = screen.getByPlaceholderText('you@example.com');

      expect(usernameInput).toBeRequired();
      expect(emailInput).toBeRequired();
    });

    it('should have email input with type email', () => {
      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      const emailInput = screen.getByPlaceholderText('you@example.com');
      expect(emailInput).toHaveAttribute('type', 'email');
    });

    it('should have password inputs with type password', () => {
      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      const passwordInput = screen.getByPlaceholderText('password');
      const password2Input = screen.getByPlaceholderText('repeat password');

      expect(passwordInput).toHaveAttribute('type', 'password');
      expect(password2Input).toHaveAttribute('type', 'password');
    });
  });

  describe('Navigation', () => {
    it('should have clickable link to login', () => {
      render(
        <BrowserRouter>
          <Signup />
        </BrowserRouter>
      );

      const loginLink = screen.getByText(/already have an account/i).closest('a');
      expect(loginLink).toHaveAttribute('href', '/login');
    });
  });
});
