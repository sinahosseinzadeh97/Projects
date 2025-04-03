import { Link, useLocation } from 'wouter';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  BarChart2,
  Settings,
  HelpCircle,
  DollarSign
} from 'lucide-react';
import { Separator } from '@/components/ui/separator';
import { useQuery } from '@tanstack/react-query';
import { Skeleton } from '@/components/ui/skeleton';

interface NavLinkProps {
  href: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  isActive: boolean;
}

const NavLink = ({ href, icon, children, isActive }: NavLinkProps) => {
  return (
    <Link href={href}>
      <div
        className={cn(
          "flex items-center px-3 py-2 text-sm font-medium rounded-md cursor-pointer",
          isActive 
            ? "bg-primary text-white" 
            : "text-foreground hover:bg-accent hover:text-white"
        )}
      >
        <span className="mr-3">{icon}</span>
        {children}
      </div>
    </Link>
  );
};

export default function Sidebar() {
  const [location] = useLocation();
  
  const { data: user, isLoading: isUserLoading } = useQuery({
    queryKey: ['/api/user'],
  });

  return (
    <div className="bg-card w-full md:w-64 md:min-h-screen flex-shrink-0 border-r border-border">
      <div className="p-4 flex flex-col h-full">
        <div className="flex items-center space-x-2 mb-8">
          <div className="h-8 w-8 rounded-md bg-primary flex items-center justify-center">
            <DollarSign className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-lg font-semibold">Sina mohammadhosseinzadeh</h1>
        </div>
        
        <nav className="space-y-1 flex-1">
          <NavLink
            href="/"
            icon={<LayoutDashboard className="h-5 w-5" />}
            isActive={location === '/' || location === '/dashboard'}
          >
            Dashboard
          </NavLink>
          
          <NavLink
            href="/transactions"
            icon={<BarChart2 className="h-5 w-5" />}
            isActive={location === '/transactions'}
          >
            Transactions
          </NavLink>
          
          <NavLink
            href="/settings"
            icon={<Settings className="h-5 w-5" />}
            isActive={location === '/settings'}
          >
            Settings
          </NavLink>
          
          <NavLink
            href="/help"
            icon={<HelpCircle className="h-5 w-5" />}
            isActive={location === '/help'}
          >
            Help
          </NavLink>
        </nav>
        
        <Separator className="my-4" />
        
        <div className="flex items-center px-3 py-2 text-sm font-medium text-muted-foreground">
          {isUserLoading ? (
            <>
              <Skeleton className="h-8 w-8 rounded-full mr-3" />
              <div className="flex-1">
                <Skeleton className="h-4 w-32 mb-1" />
                <Skeleton className="h-3 w-16" />
              </div>
            </>
          ) : (
            <>
              <div className="h-8 w-8 rounded-full bg-primary/20 text-primary flex items-center justify-center mr-3">
                <span>{user?.avatarInitials || 'U'}</span>
              </div>
              <div className="flex-1">
                <p className="text-foreground">{user?.username || 'User'}</p>
                <p className="text-xs text-muted-foreground">{user?.role || 'User'}</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
