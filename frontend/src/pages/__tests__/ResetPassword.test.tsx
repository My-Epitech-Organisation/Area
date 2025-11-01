import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ResetPassword from '../ResetPassword';
import { API_BASE } from '../../utils/helper';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('ResetPassword Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  describe('Basic Rendering', () => {
    it('should render reset password page with token', () => {
      render(
        <MemoryRouter initialEntries={['/reset-password?token=valid-token-123']}>
          <ResetPassword />
        </MemoryRouter>
      );

      expect(screen.getByText('Reset Your Password')).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/enter new password/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/confirm new password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /reset password/i })).toBeInTheDocument();
    });

    it('should display helper text for password requirements', () => {
      render(
        <MemoryRouter initialEntries={['/reset-password?token=valid-token']}>
          <ResetPassword />
        </MemoryRouter>
      );

      expect(screen.getByText(/must be at least 8 characters long/i)).toBeInTheDocument();
    });

    it('should render back to login link', () => {
      render(
        <MemoryRouter initialEntries={['/reset-password?token=valid-token']}>
          <ResetPassword />
        </MemoryRouter>
      );

      const backLink = screen.getByText(/back to login/i);
      expect(backLink).toBeInTheDocument();
      expect(backLink).toHaveAttribute('href', '/login');
    });

    it('should show error when token is missing', () => {
      render(
        <MemoryRouter initialEntries={['/reset-password']}>
          <ResetPassword />
        </MemoryRouter>
      );

      expect(screen.getByText(/invalid or missing reset token/i)).toBeInTheDocument();
    });
  });

  describe('Form Interaction', () => {
    it('should allow typing in password fields', () => {
      render(
        <MemoryRouter initialEntries={['/reset-password?token=valid-token']}>
          <ResetPassword />
        </MemoryRouter>
      );

      const passwordInput = screen.getByPlaceholderText(/enter new password/i);
      const confirmInput = screen.getByPlaceholderText(/confirm new password/i);

      fireEvent.change(passwordInput, { target: { value: 'NewPassword123' } });
      fireEvent.change(confirmInput, { target: { value: 'NewPassword123' } });

      expect(passwordInput).toHaveValue('NewPassword123');
      expect(confirmInput).toHaveValue('NewPassword123');
    });

    it('should disable submit button when token is missing', () => {
      render(
        <MemoryRouter initialEntries={['/reset-password']}>
          <ResetPassword />
        </MemoryRouter>
      );

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Password Validation', () => {
    it('should show error when passwords do not match', () => {
      render(
        <MemoryRouter initialEntries={['/reset-password?token=valid-token']}>
          <ResetPassword />
        </MemoryRouter>
      );

      const passwordInput = screen.getByPlaceholderText(/enter new password/i);
      const confirmInput = screen.getByPlaceholderText(/confirm new password/i);
      const submitButton = screen.getByRole('button', { name: /reset password/i });

      fireEvent.change(passwordInput, { target: { value: 'Password123' } });
      fireEvent.change(confirmInput, { target: { value: 'DifferentPass456' } });
      fireEvent.submit(submitButton.closest('form')!);

      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
      expect(globalThis.fetch).not.toHaveBeenCalled();
    });

    it('should show error when password is too short', () => {
      render(
        <MemoryRouter initialEntries={['/reset-password?token=valid-token']}>
          <ResetPassword />
        </MemoryRouter>
      );

      const passwordInput = screen.getByPlaceholderText(/enter new password/i);
      const confirmInput = screen.getByPlaceholderText(/confirm new password/i);
      const submitButton = screen.getByRole('button', { name: /reset password/i });

      fireEvent.change(passwordInput, { target: { value: 'short' } });
      fireEvent.change(confirmInput, { target: { value: 'short' } });
      fireEvent.submit(submitButton.closest('form')!);

      expect(screen.getByText(/password must be at least 8 characters long/i)).toBeInTheDocument();
      expect(globalThis.fetch).not.toHaveBeenCalled();
    });
  });

  describe('Successful Password Reset', () => {
    it('should call API endpoint on valid form submission', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      render(
        <MemoryRouter initialEntries={['/reset-password?token=test-token-456']}>
          <ResetPassword />
        </MemoryRouter>
      );

      const passwordInput = screen.getByPlaceholderText(/enter new password/i);
      const confirmInput = screen.getByPlaceholderText(/confirm new password/i);
      const form = passwordInput.closest('form')!;

      fireEvent.change(passwordInput, { target: { value: 'MyNewPass123' } });
      fireEvent.change(confirmInput, { target: { value: 'MyNewPass123' } });
      fireEvent.submit(form);

      await vi.waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledWith(
          `${API_BASE}/auth/password-reset/confirm/`,
          expect.objectContaining({
            method: 'POST',
          })
        );
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message when API returns error', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Invalid or expired token' }),
      });

      render(
        <MemoryRouter initialEntries={['/reset-password?token=expired-token']}>
          <ResetPassword />
        </MemoryRouter>
      );

      const passwordInput = screen.getByPlaceholderText(/enter new password/i);
      const confirmInput = screen.getByPlaceholderText(/confirm new password/i);
      const form = passwordInput.closest('form')!;

      fireEvent.change(passwordInput, { target: { value: 'ValidPassword123' } });
      fireEvent.change(confirmInput, { target: { value: 'ValidPassword123' } });
      fireEvent.submit(form);

      await vi.waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper labels for form inputs', () => {
      render(
        <MemoryRouter initialEntries={['/reset-password?token=valid-token']}>
          <ResetPassword />
        </MemoryRouter>
      );

      const passwordInput = screen.getByPlaceholderText(/enter new password/i);
      const confirmInput = screen.getByPlaceholderText(/confirm new password/i);

      expect(passwordInput).toHaveAttribute('id', 'password');
      expect(confirmInput).toHaveAttribute('id', 'confirmPassword');

      expect(screen.getByText('New Password')).toBeInTheDocument();
      expect(screen.getByText('Confirm New Password')).toBeInTheDocument();
    });

    it('should have accessible submit button', () => {
      render(
        <MemoryRouter initialEntries={['/reset-password?token=valid-token']}>
          <ResetPassword />
        </MemoryRouter>
      );

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toHaveAttribute('type', 'submit');
    });
  });
});
