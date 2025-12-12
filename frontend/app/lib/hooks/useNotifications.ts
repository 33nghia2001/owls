/**
 * WebSocket hook for real-time notifications.
 * Connects to backend WebSocket and provides notification state.
 */
import { useEffect, useCallback, useState, useRef } from 'react';
import { useAuthStore } from '~/lib/stores';
import toast from 'react-hot-toast';

interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  link?: string;
  created_at: string;
  is_read: boolean;
}

interface UseNotificationsReturn {
  unreadCount: number;
  notifications: Notification[];
  isConnected: boolean;
  markAsRead: (notificationId: string) => void;
  reconnect: () => void;
}

// WebSocket URL - should match backend routing
const getWebSocketUrl = (): string | null => {
  // Skip WebSocket if not configured (e.g., Koyeb free tier doesn't support WS)
  const host = import.meta.env.VITE_WS_HOST;
  if (!host) {
    return null;
  }
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${wsProtocol}//${host}/ws/notifications/`;
};

export function useNotifications(): UseNotificationsReturn {
  const { isAuthenticated } = useAuthStore();
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (!isAuthenticated || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = getWebSocketUrl();
    // Skip if WebSocket not configured
    if (!wsUrl) {
      return;
    }

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[WS] Notification connection established');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'unread_count':
              setUnreadCount(data.count);
              break;
              
            case 'notification':
              const notification = data.notification as Notification;
              setNotifications(prev => [notification, ...prev.slice(0, 49)]); // Keep last 50
              setUnreadCount(prev => prev + 1);
              
              // Show toast for new notifications
              showNotificationToast(notification);
              break;
              
            default:
              console.log('[WS] Unknown message type:', data.type);
          }
        } catch (e) {
          console.error('[WS] Failed to parse message:', e);
        }
      };

      ws.onclose = (event) => {
        console.log('[WS] Connection closed:', event.code, event.reason);
        setIsConnected(false);
        wsRef.current = null;

        // Attempt reconnection with exponential backoff
        if (isAuthenticated && reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          reconnectAttemptsRef.current++;
          console.log(`[WS] Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})`);
          reconnectTimeoutRef.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = (error) => {
        console.error('[WS] Error:', error);
      };
    } catch (error) {
      console.error('[WS] Failed to create connection:', error);
    }
  }, [isAuthenticated]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const markAsRead = useCallback((notificationId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'mark_read',
        notification_id: notificationId
      }));
      
      // Optimistic update
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      );
    }
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    setTimeout(connect, 100);
  }, [connect, disconnect]);

  // Connect when authenticated, disconnect when not
  useEffect(() => {
    if (isAuthenticated) {
      connect();
    } else {
      disconnect();
      setUnreadCount(0);
      setNotifications([]);
    }

    return () => {
      disconnect();
    };
  }, [isAuthenticated, connect, disconnect]);

  return {
    unreadCount,
    notifications,
    isConnected,
    markAsRead,
    reconnect
  };
}

// Helper function to show notification toast
function showNotificationToast(notification: Notification) {
  const toastOptions: Parameters<typeof toast>[1] = {
    duration: 5000,
    position: 'top-right',
  };

  switch (notification.type) {
    case 'order_confirmed':
    case 'order_shipped':
    case 'order_delivered':
      toast.success(notification.message, {
        ...toastOptions,
        icon: '📦',
      });
      break;
      
    case 'payment_success':
      toast.success(notification.message, {
        ...toastOptions,
        icon: '💰',
      });
      break;
      
    case 'new_message':
      toast(notification.message, {
        ...toastOptions,
        icon: '💬',
      });
      break;
      
    case 'promotion':
    case 'coupon':
      toast(notification.message, {
        ...toastOptions,
        icon: '🎁',
      });
      break;
      
    default:
      toast(notification.message, toastOptions);
  }
}

export default useNotifications;
