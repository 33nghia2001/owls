/**
 * Notifications page - Lists all user notifications.
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { Bell, Check, CheckCheck, Trash2, ArrowLeft } from 'lucide-react';
import { useNotifications } from '~/lib/hooks/useNotifications';
import { useAuthStore } from '~/lib/stores';
import { Button } from '~/components/ui';
import { cn } from '~/lib/utils';
import api from '~/lib/api';

interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  link?: string;
  created_at: string;
  is_read: boolean;
}

export default function NotificationsPage() {
  const { isAuthenticated } = useAuthStore();
  const { notifications: realtimeNotifications, markAsRead } = useNotifications();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch notifications from API on mount
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const fetchNotifications = async () => {
      try {
        const response = await api.get('/notifications/');
        setNotifications(response.data.results || response.data);
      } catch (error) {
        console.error('Failed to fetch notifications:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchNotifications();
  }, [isAuthenticated]);

  // Merge realtime notifications with fetched ones
  const allNotifications = [...realtimeNotifications, ...notifications]
    .filter((n, i, arr) => arr.findIndex(x => x.id === n.id) === i)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  const handleMarkAsRead = async (notificationId: string) => {
    // Send via WebSocket
    markAsRead(notificationId);
    
    // Also update local state
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
    );
  };

  const handleMarkAllAsRead = async () => {
    try {
      await api.post('/notifications/mark-all-read/');
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <Bell className="mx-auto h-16 w-16 text-gray-300" />
        <h1 className="mt-4 text-2xl font-bold text-gray-900">Đăng nhập để xem thông báo</h1>
        <p className="mt-2 text-gray-600">Vui lòng đăng nhập để xem các thông báo của bạn.</p>
        <Link to="/auth/login">
          <Button className="mt-6">Đăng nhập</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-3xl px-4 py-8">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link 
            to="/" 
            className="rounded-full p-2 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Thông báo
          </h1>
        </div>
        
        {allNotifications.some(n => !n.is_read) && (
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleMarkAllAsRead}
            className="flex items-center gap-2"
          >
            <CheckCheck className="h-4 w-4" />
            Đánh dấu tất cả đã đọc
          </Button>
        )}
      </div>

      {/* Notifications List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse rounded-xl bg-gray-100 p-4 dark:bg-gray-800">
              <div className="h-4 w-3/4 rounded bg-gray-200 dark:bg-gray-700" />
              <div className="mt-2 h-3 w-1/2 rounded bg-gray-200 dark:bg-gray-700" />
            </div>
          ))}
        </div>
      ) : allNotifications.length === 0 ? (
        <div className="py-16 text-center">
          <Bell className="mx-auto h-16 w-16 text-gray-300" />
          <h2 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
            Chưa có thông báo
          </h2>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Bạn sẽ nhận được thông báo khi có cập nhật mới.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {allNotifications.map(notification => (
            <NotificationItem 
              key={notification.id}
              notification={notification}
              onMarkAsRead={handleMarkAsRead}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: string) => void;
}

function NotificationItem({ notification, onMarkAsRead }: NotificationItemProps) {
  const getIcon = (type: string) => {
    switch (type) {
      case 'order_confirmed':
      case 'order_shipped':
      case 'order_delivered':
        return '📦';
      case 'payment_success':
        return '💰';
      case 'new_message':
        return '💬';
      case 'promotion':
      case 'coupon':
        return '🎁';
      default:
        return '🔔';
    }
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return 'Vừa xong';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} phút trước`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} giờ trước`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)} ngày trước`;
    return date.toLocaleDateString('vi-VN');
  };

  const content = (
    <div className={cn(
      "group relative flex gap-4 rounded-xl p-4 transition-colors",
      notification.is_read 
        ? "bg-white hover:bg-gray-50 dark:bg-gray-900 dark:hover:bg-gray-800"
        : "bg-orange-50 hover:bg-orange-100 dark:bg-orange-900/20 dark:hover:bg-orange-900/30"
    )}>
      {/* Icon */}
      <span className="text-2xl">{getIcon(notification.type)}</span>
      
      {/* Content */}
      <div className="flex-1 min-w-0">
        <h3 className={cn(
          "text-sm font-medium",
          notification.is_read 
            ? "text-gray-900 dark:text-gray-100"
            : "text-gray-900 dark:text-white"
        )}>
          {notification.title}
        </h3>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
          {notification.message}
        </p>
        <span className="mt-2 block text-xs text-gray-400 dark:text-gray-500">
          {formatTime(notification.created_at)}
        </span>
      </div>

      {/* Actions */}
      {!notification.is_read && (
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onMarkAsRead(notification.id);
          }}
          className="absolute right-4 top-4 opacity-0 group-hover:opacity-100 transition-opacity"
          title="Đánh dấu đã đọc"
        >
          <Check className="h-5 w-5 text-orange-500 hover:text-orange-600" />
        </button>
      )}

      {/* Unread dot */}
      {!notification.is_read && (
        <span className="absolute left-2 top-1/2 -translate-y-1/2 h-2 w-2 rounded-full bg-orange-500" />
      )}
    </div>
  );

  if (notification.link) {
    return (
      <Link to={notification.link} onClick={() => !notification.is_read && onMarkAsRead(notification.id)}>
        {content}
      </Link>
    );
  }

  return content;
}
