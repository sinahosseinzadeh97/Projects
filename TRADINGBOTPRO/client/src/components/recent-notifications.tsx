import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useQuery } from '@tanstack/react-query';
import { Skeleton } from '@/components/ui/skeleton';
import { Link } from 'wouter';
import { CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react';

interface NotificationProps {
  notification: {
    id: number;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message: string;
    timestamp: string;
  };
}

function Notification({ notification }: NotificationProps) {
  // Format the timestamp to show relative time (e.g., "2 minutes ago")
  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.round(diffMs / 60000);
    
    if (diffMins < 60) {
      return `${diffMins} minutes ago`;
    } else if (diffMins < 1440) {
      return `${Math.floor(diffMins / 60)} hours ago`;
    } else {
      return `${Math.floor(diffMins / 1440)} days ago`;
    }
  };
  
  // Get the appropriate icon based on notification type
  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500 mr-2 flex-shrink-0" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2 flex-shrink-0" />;
      case 'info':
        return <Info className="h-5 w-5 text-primary mr-2 flex-shrink-0" />;
      default:
        return <Info className="h-5 w-5 text-primary mr-2 flex-shrink-0" />;
    }
  };
  
  // Get the background color based on notification type
  const getBgColor = () => {
    switch (notification.type) {
      case 'success':
        return 'bg-green-500/10 border-l-2 border-green-500';
      case 'error':
        return 'bg-red-500/10 border-l-2 border-red-500';
      case 'warning':
        return 'bg-yellow-500/10 border-l-2 border-yellow-500';
      case 'info':
        return 'bg-primary/10 border-l-2 border-primary';
      default:
        return 'bg-primary/10 border-l-2 border-primary';
    }
  };

  return (
    <div className={`p-3 rounded-md ${getBgColor()}`}>
      <div className="flex items-start">
        {getIcon()}
        <div>
          <p className="text-sm font-medium">{notification.title}</p>
          <p className="text-xs text-muted-foreground">{notification.message}</p>
          <p className="text-xs text-muted-foreground mt-1">{formatTimeAgo(notification.timestamp)}</p>
        </div>
      </div>
    </div>
  );
}

function NotificationSkeleton() {
  return (
    <div className="p-3 bg-secondary/30 rounded-md border-l-2 border-muted">
      <div className="flex items-start">
        <Skeleton className="h-5 w-5 mr-2 flex-shrink-0" />
        <div className="w-full">
          <Skeleton className="h-4 w-2/3 mb-1" />
          <Skeleton className="h-3 w-full mb-1" />
          <Skeleton className="h-3 w-16 mt-1" />
        </div>
      </div>
    </div>
  );
}

export default function RecentNotifications() {
  const { data: notifications, isLoading } = useQuery({
    queryKey: ['/api/notifications'],
  });

  return (
    <Card>
      <div className="border-b border-border px-5 py-4 flex justify-between items-center">
        <h2 className="text-lg font-medium">Recent Notifications</h2>
        <Link href="/notifications">
          <Button variant="link" className="text-primary hover:underline p-0 h-auto">
            View All
          </Button>
        </Link>
      </div>
      <CardContent className="p-5">
        <div className="space-y-3 max-h-[300px] overflow-y-auto">
          {isLoading ? (
            <>
              <NotificationSkeleton />
              <NotificationSkeleton />
              <NotificationSkeleton />
              <NotificationSkeleton />
            </>
          ) : notifications?.length ? (
            notifications.map((notification: any) => (
              <Notification key={notification.id} notification={notification} />
            ))
          ) : (
            <div className="text-center py-4 text-muted-foreground">
              No notifications found
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
