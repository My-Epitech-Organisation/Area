/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** Login page tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Login from '../Login';
import { API_BASE } from '../../utils/helper';

describe('Login', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    (globalThis as any).fetch = vi.fn();
  });

  it('should render login form', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    expect(screen.getByPlaceholderText(/email/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument();
  });

  it('should allow typing in email field', async () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const emailInput = screen.getByPlaceholderText(/email/i) as HTMLInputElement;
    await userEvent.type(emailInput, 'test@example.com');

    expect(emailInput.value).toBe('test@example.com');
  });

  it('should allow typing in password field', async () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const passwordInput = screen.getByPlaceholderText(/password/i) as HTMLInputElement;
    await userEvent.type(passwordInput, 'password123');

    expect(passwordInput.value).toBe('password123');
  });

  it('should submit form with valid credentials', async () => {
    const mockFetch = (globalThis as any).fetch as any;

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access: 'access-token',
        refresh: 'refresh-token',
      }),
    });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
      }),
    });

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const emailInput = screen.getByPlaceholderText(/email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE}/auth/login/`,
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: 'test@example.com', password: 'password123' }),
        })
      );
    });
  });

  it('should display error on failed login', async () => {
    const mockFetch = (globalThis as any).fetch as any;

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({
        detail: 'Invalid credentials',
      }),
    });

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const emailInput = screen.getByPlaceholderText(/email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'wrongpassword');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });

  it('should have link to signup page', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const signupLink = screen.getByText(/don't have an account/i).closest('a');
    expect(signupLink).toHaveAttribute('href', '/signup');
  });

  it('should have link to forgot password page', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const forgotLink = screen.getByText(/forgot password/i).closest('a');
    expect(forgotLink).toHaveAttribute('href', '/forgot-password');
  });

  it('should disable submit button during loading', async () => {
    const mockFetch = (globalThis as any).fetch as any;

    mockFetch.mockImplementationOnce(() => new Promise(() => {}));

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const emailInput = screen.getByPlaceholderText(/email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');

    expect(submitButton).not.toBeDisabled();
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });
  });

  it('should show loading text on button during submission', async () => {
    const mockFetch = (globalThis as any).fetch as any;

    mockFetch.mockImplementationOnce(() => new Promise(() => {}));

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const emailInput = screen.getByPlaceholderText(/email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/logging in/i)).toBeInTheDocument();
    });
  });

  it('should handle network error', async () => {
    const mockFetch = (globalThis as any).fetch as any;

    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const emailInput = screen.getByPlaceholderText(/email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/network error/i)).toBeInTheDocument();
    });
  });

  it('should store tokens on successful login', async () => {
    const mockFetch = (globalThis as any).fetch as any;

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access: 'access-token-123',
        refresh: 'refresh-token-456',
      }),
    });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
      }),
    });

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const emailInput = screen.getByPlaceholderText(/email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(localStorage.getItem('access')).toBe('access-token-123');
      expect(localStorage.getItem('refresh')).toBe('refresh-token-456');
    });
  });
});
