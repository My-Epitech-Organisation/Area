/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** Notification component tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Notification from '../Notification';

describe('Notification', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render success notification', () => {
    const onClose = vi.fn();
    render(<Notification type="success" message="Success message" onClose={onClose} />);

    expect(screen.getByText('Success message')).toBeInTheDocument();
  });

  it('should render error notification', () => {
    const onClose = vi.fn();
    render(<Notification type="error" message="Error message" onClose={onClose} />);

    expect(screen.getByText('Error message')).toBeInTheDocument();
  });

  it('should render info notification', () => {
    const onClose = vi.fn();
    render(<Notification type="info" message="Info message" onClose={onClose} />);

    expect(screen.getByText('Info message')).toBeInTheDocument();
  });

  it('should render warning notification', () => {
    const onClose = vi.fn();
    render(<Notification type="warning" message="Warning message" onClose={onClose} />);

    expect(screen.getByText('Warning message')).toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', async () => {
    const onClose = vi.fn();

    render(<Notification type="info" message="Test message" onClose={onClose} />);

    const closeButton = screen.getByRole('button');
    await userEvent.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('should auto-close after default duration', () => {
    const onClose = vi.fn();
    render(<Notification type="info" message="Test message" onClose={onClose} />);

    expect(onClose).not.toHaveBeenCalled();

    vi.advanceTimersByTime(5000);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('should auto-close after custom duration', () => {
    const onClose = vi.fn();
    render(<Notification type="info" message="Test message" duration={3000} onClose={onClose} />);

    expect(onClose).not.toHaveBeenCalled();

    vi.advanceTimersByTime(3000);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('should not auto-close when duration is 0', () => {
    const onClose = vi.fn();
    render(<Notification type="info" message="Test message" duration={0} onClose={onClose} />);

    vi.advanceTimersByTime(10000);

    expect(onClose).not.toHaveBeenCalled();
  });

  it('should clear timer on unmount', () => {
    const onClose = vi.fn();
    const { unmount } = render(
      <Notification type="info" message="Test message" onClose={onClose} />
    );

    unmount();
    vi.advanceTimersByTime(5000);

    expect(onClose).not.toHaveBeenCalled();
  });

  it('should apply correct styles for success type', () => {
    const onClose = vi.fn();
    const { container } = render(
      <Notification type="success" message="Success" onClose={onClose} />
    );

    const notification = container.querySelector('div');
    expect(notification).toHaveClass('bg-green-500/20');
    expect(notification).toHaveClass('border-green-500/50');
    expect(notification).toHaveClass('text-green-300');
  });

  it('should apply correct styles for error type', () => {
    const onClose = vi.fn();
    const { container } = render(<Notification type="error" message="Error" onClose={onClose} />);

    const notification = container.querySelector('div');
    expect(notification).toHaveClass('bg-red-500/20');
    expect(notification).toHaveClass('border-red-500/50');
    expect(notification).toHaveClass('text-red-300');
  });

  it('should apply correct styles for warning type', () => {
    const onClose = vi.fn();
    const { container } = render(
      <Notification type="warning" message="Warning" onClose={onClose} />
    );

    const notification = container.querySelector('div');
    expect(notification).toHaveClass('bg-yellow-500/20');
    expect(notification).toHaveClass('border-yellow-500/50');
    expect(notification).toHaveClass('text-yellow-300');
  });

  it('should apply correct styles for info type', () => {
    const onClose = vi.fn();
    const { container } = render(<Notification type="info" message="Info" onClose={onClose} />);

    const notification = container.querySelector('div');
    expect(notification).toHaveClass('bg-blue-500/20');
    expect(notification).toHaveClass('border-blue-500/50');
    expect(notification).toHaveClass('text-blue-300');
  });

  it('should render icon for each notification type', () => {
    const onClose = vi.fn();

    const { container, rerender } = render(
      <Notification type="success" message="Success" onClose={onClose} />
    );
    expect(container.querySelector('svg')).toBeInTheDocument();

    rerender(<Notification type="error" message="Error" onClose={onClose} />);
    expect(container.querySelector('svg')).toBeInTheDocument();

    rerender(<Notification type="warning" message="Warning" onClose={onClose} />);
    expect(container.querySelector('svg')).toBeInTheDocument();

    rerender(<Notification type="info" message="Info" onClose={onClose} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});
