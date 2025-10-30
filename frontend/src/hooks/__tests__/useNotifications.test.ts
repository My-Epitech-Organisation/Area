/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** useNotifications tests
 */

import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useNotifications } from '../useNotifications';

describe('useNotifications', () => {
  it('should initialize with empty notifications', () => {
    const { result } = renderHook(() => useNotifications());

    expect(result.current.notifications).toEqual([]);
  });

  it('should add a notification', () => {
    const { result } = renderHook(() => useNotifications());

    act(() => {
      result.current.addNotification('info', 'Test message');
    });

    expect(result.current.notifications).toHaveLength(1);
    expect(result.current.notifications[0].type).toBe('info');
    expect(result.current.notifications[0].message).toBe('Test message');
    expect(result.current.notifications[0].id).toBeDefined();
  });

  it('should add multiple notifications', () => {
    const { result } = renderHook(() => useNotifications());

    act(() => {
      result.current.addNotification('info', 'Message 1');
      result.current.addNotification('success', 'Message 2');
      result.current.addNotification('error', 'Message 3');
    });

    expect(result.current.notifications).toHaveLength(3);
    expect(result.current.notifications[0].message).toBe('Message 1');
    expect(result.current.notifications[1].message).toBe('Message 2');
    expect(result.current.notifications[2].message).toBe('Message 3');
  });

  it('should generate unique IDs for notifications', () => {
    const { result } = renderHook(() => useNotifications());

    let id1 = '';
    let id2 = '';

    act(() => {
      id1 = result.current.addNotification('info', 'Message 1');
      id2 = result.current.addNotification('info', 'Message 2');
    });

    expect(id1).not.toBe(id2);
  });

  it('should remove a notification by ID', () => {
    const { result } = renderHook(() => useNotifications());

    let notificationId = '';

    act(() => {
      notificationId = result.current.addNotification('info', 'Test message');
    });

    expect(result.current.notifications).toHaveLength(1);

    act(() => {
      result.current.removeNotification(notificationId);
    });

    expect(result.current.notifications).toHaveLength(0);
  });

  it('should only remove the specified notification', () => {
    const { result } = renderHook(() => useNotifications());

    let id1 = '';
    let id2 = '';
    let id3 = '';

    act(() => {
      id1 = result.current.addNotification('info', 'Message 1');
      id2 = result.current.addNotification('success', 'Message 2');
      id3 = result.current.addNotification('error', 'Message 3');
    });

    expect(result.current.notifications).toHaveLength(3);

    act(() => {
      result.current.removeNotification(id2);
    });

    expect(result.current.notifications).toHaveLength(2);
    expect(result.current.notifications.find((n) => n.id === id1)).toBeDefined();
    expect(result.current.notifications.find((n) => n.id === id2)).toBeUndefined();
    expect(result.current.notifications.find((n) => n.id === id3)).toBeDefined();
  });

  it('should add success notification', () => {
    const { result } = renderHook(() => useNotifications());

    act(() => {
      result.current.success('Success message');
    });

    expect(result.current.notifications).toHaveLength(1);
    expect(result.current.notifications[0].type).toBe('success');
    expect(result.current.notifications[0].message).toBe('Success message');
  });

  it('should add error notification', () => {
    const { result } = renderHook(() => useNotifications());

    act(() => {
      result.current.error('Error message');
    });

    expect(result.current.notifications).toHaveLength(1);
    expect(result.current.notifications[0].type).toBe('error');
    expect(result.current.notifications[0].message).toBe('Error message');
  });

  it('should add info notification', () => {
    const { result } = renderHook(() => useNotifications());

    act(() => {
      result.current.info('Info message');
    });

    expect(result.current.notifications).toHaveLength(1);
    expect(result.current.notifications[0].type).toBe('info');
    expect(result.current.notifications[0].message).toBe('Info message');
  });

  it('should add warning notification', () => {
    const { result } = renderHook(() => useNotifications());

    act(() => {
      result.current.warning('Warning message');
    });

    expect(result.current.notifications).toHaveLength(1);
    expect(result.current.notifications[0].type).toBe('warning');
    expect(result.current.notifications[0].message).toBe('Warning message');
  });

  it('should return notification ID from helper methods', () => {
    const { result } = renderHook(() => useNotifications());

    let successId = '';
    let errorId = '';

    act(() => {
      successId = result.current.success('Success');
      errorId = result.current.error('Error');
    });

    expect(successId).toBeDefined();
    expect(errorId).toBeDefined();
    expect(successId).not.toBe(errorId);
  });

  it('should handle removing non-existent notification gracefully', () => {
    const { result } = renderHook(() => useNotifications());

    act(() => {
      result.current.addNotification('info', 'Message');
    });

    expect(result.current.notifications).toHaveLength(1);

    act(() => {
      result.current.removeNotification('non-existent-id');
    });

    expect(result.current.notifications).toHaveLength(1);
  });
});
