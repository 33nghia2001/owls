/**
 * Notification bell icon with unread count badge.
 * Uses WebSocket hook for real-time updates.
 */
import { Bell } from 'lucide-react';
import { Link } from 'react-router';
import { useNotifications } from '~/lib/hooks/useNotifications';
import { cn } from '~/lib/utils';

interface NotificationBellProps {
  className?: string;
}

export function NotificationBell({ className }: NotificationBellProps) {
  const { unreadCount, isConnected } = useNotifications();

  return (
    <Link 
      to="/notifications" 
      className={cn(
        "relative inline-flex items-center justify-center rounded-full p-2",
        "text-gray-700 hover:bg-gray-100 hover:text-orange-600",
        "dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-orange-400",
        "transition-colors duration-200",
        className
      )}
      title="Thông báo"
    >
      <Bell className="h-5 w-5" />
      
      {/* Unread count badge */}
      {unreadCount > 0 && (
        <span className={cn(
          "absolute -right-0.5 -top-0.5 flex h-5 min-w-5 items-center justify-center",
          "rounded-full bg-red-500 px-1.5 text-xs font-bold text-white",
          "animate-in zoom-in-50 duration-200"
        )}>
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
      
      {/* Connection indicator (only in dev) */}
      {import.meta.env.DEV && (
        <span 
          className={cn(
            "absolute bottom-0.5 right-0.5 h-2 w-2 rounded-full",
            isConnected ? "bg-green-500" : "bg-gray-400"
          )}
          title={isConnected ? "Connected" : "Disconnected"}
        />
      )}
    </Link>
  );
}

export default NotificationBell;
