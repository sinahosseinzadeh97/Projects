import { BellIcon } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { useQuery } from '@tanstack/react-query';
import { Skeleton } from '@/components/ui/skeleton';

interface HeaderProps {
  title: string;
}

export default function Header({ title }: HeaderProps) {
  const { data: user, isLoading: isUserLoading } = useQuery({
    queryKey: ['/api/user'],
  });
  
  const { data: notifications } = useQuery({
    queryKey: ['/api/notifications'],
  });
  
  // Check if there are any unread notifications
  const hasUnreadNotifications = notifications?.some(
    (notification: any) => !notification.isRead
  );

  return (
    <header className="bg-card border-b border-border p-4 flex items-center justify-between">
      <h1 className="text-xl font-semibold">{title}</h1>
      
      <div className="flex items-center space-x-4">
        <div className="relative">
          <button className="p-2 rounded-md bg-secondary text-foreground hover:bg-accent">
            <BellIcon className="h-5 w-5" />
            {hasUnreadNotifications && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-primary rounded-full"></span>
            )}
          </button>
        </div>
        
        {isUserLoading ? (
          <Skeleton className="h-8 w-8 rounded-full" />
        ) : (
          <Avatar className="h-8 w-8 bg-primary/20 text-primary">
            <AvatarFallback>{user?.avatarInitials || 'U'}</AvatarFallback>
          </Avatar>
        )}
      </div>
    </header>
  );
}
