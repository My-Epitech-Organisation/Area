/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** OAuthBadge component tests
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import OAuthBadge from '../OAuthBadge';

describe('OAuthBadge', () => {
  it('should render connected badge when isConnected is true', () => {
    render(<OAuthBadge isConnected={true} />);

    expect(screen.getByText('Connected')).toBeInTheDocument();
  });

  it('should render not connected badge when isConnected is false', () => {
    render(<OAuthBadge isConnected={false} />);

    expect(screen.getByText('Not connected')).toBeInTheDocument();
  });

  it('should apply correct styles for connected state', () => {
    const { container } = render(<OAuthBadge isConnected={true} />);

    const badge = container.querySelector('div');
    expect(badge).toHaveClass('bg-green-500/20');
    expect(badge).toHaveClass('text-green-300');
    expect(badge).toHaveClass('border-green-500/30');
  });

  it('should apply correct styles for not connected state', () => {
    const { container } = render(<OAuthBadge isConnected={false} />);

    const badge = container.querySelector('div');
    expect(badge).toHaveClass('bg-gray-500/20');
    expect(badge).toHaveClass('text-gray-400');
    expect(badge).toHaveClass('border-gray-500/30');
  });

  it('should use small size by default', () => {
    const { container } = render(<OAuthBadge isConnected={true} />);

    const badge = container.querySelector('div');
    expect(badge).toHaveClass('px-2');
    expect(badge).toHaveClass('py-1');
    expect(badge).toHaveClass('text-xs');
  });

  it('should apply medium size when specified', () => {
    const { container } = render(<OAuthBadge isConnected={true} size="md" />);

    const badge = container.querySelector('div');
    expect(badge).toHaveClass('px-3');
    expect(badge).toHaveClass('py-1.5');
    expect(badge).toHaveClass('text-sm');
  });

  it('should apply large size when specified', () => {
    const { container } = render(<OAuthBadge isConnected={true} size="lg" />);

    const badge = container.querySelector('div');
    expect(badge).toHaveClass('px-4');
    expect(badge).toHaveClass('py-2');
    expect(badge).toHaveClass('text-base');
  });

  it('should render icon for connected state', () => {
    const { container } = render(<OAuthBadge isConnected={true} />);

    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('should render icon for not connected state', () => {
    const { container } = render(<OAuthBadge isConnected={false} />);

    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('should have correct icon size for small badge', () => {
    const { container } = render(<OAuthBadge isConnected={true} size="sm" />);

    const icon = container.querySelector('svg');
    expect(icon).toHaveClass('h-3');
    expect(icon).toHaveClass('w-3');
  });

  it('should have correct icon size for medium badge', () => {
    const { container } = render(<OAuthBadge isConnected={true} size="md" />);

    const icon = container.querySelector('svg');
    expect(icon).toHaveClass('h-4');
    expect(icon).toHaveClass('w-4');
  });

  it('should have correct icon size for large badge', () => {
    const { container } = render(<OAuthBadge isConnected={true} size="lg" />);

    const icon = container.querySelector('svg');
    expect(icon).toHaveClass('h-5');
    expect(icon).toHaveClass('w-5');
  });
});
