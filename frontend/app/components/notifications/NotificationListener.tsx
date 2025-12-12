/**
 * Global notification listener component.
 * Mounts once in root layout to maintain WebSocket connection.
 */
import { useEffect } from 'react';
import { useNotifications } from '~/lib/hooks/useNotifications';
import { useAuthStore } from '~/lib/stores';

interface NotificationListenerProps {
  // Callback to update header badge count
  onUnreadCountChange?: (count: number) => void;
}

export function NotificationListener({ onUnreadCountChange }: NotificationListenerProps) {
  const { unreadCount, isConnected } = useNotifications();
  const { isAuthenticated } = useAuthStore();

  // Notify parent of unread count changes
  useEffect(() => {
    if (onUnreadCountChange) {
      onUnreadCountChange(unreadCount);
    }
  }, [unreadCount, onUnreadCountChange]);

  // Optional: Debug logging in dev
  useEffect(() => {
    if (import.meta.env.DEV) {
      console.log('[NotificationListener] Status:', {
        isAuthenticated,
        isConnected,
        unreadCount,
      });
    }
  }, [isAuthenticated, isConnected, unreadCount]);

  // This component doesn't render anything visible
  // It just maintains the WebSocket connection
  return null;
}

export default NotificationListener;
