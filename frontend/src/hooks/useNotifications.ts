import { useState, useCallback } from 'react';
import type { NotificationType } from '../components/Notification';

export interface NotificationData {
  id: string;
  type: NotificationType;
  message: string;
}

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<NotificationData[]>([]);

  const addNotification = useCallback((type: NotificationType, message: string) => {
    const id = `${Date.now()}-${Math.random()}`;
    const notification: NotificationData = { id, type, message };

    setNotifications((prev) => [...prev, notification]);

    return id;
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const success = useCallback(
    (message: string) => {
      return addNotification('success', message);
    },
    [addNotification]
  );

  const error = useCallback(
    (message: string) => {
      return addNotification('error', message);
    },
    [addNotification]
  );

  const info = useCallback(
    (message: string) => {
      return addNotification('info', message);
    },
    [addNotification]
  );

  const warning = useCallback(
    (message: string) => {
      return addNotification('warning', message);
    },
    [addNotification]
  );

  return {
    notifications,
    addNotification,
    removeNotification,
    success,
    error,
    info,
    warning,
  };
};
