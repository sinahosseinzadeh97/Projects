import { Card, CardContent } from '@/components/ui/card';
import { BarChart, Lock, BookOpen, Wallet } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Skeleton } from '@/components/ui/skeleton';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: {
    value: string;
    isPositive: boolean;
  };
  icon: React.ReactNode;
}

function StatCard({ title, value, change, icon }: StatCardProps) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm text-muted-foreground">{title}</p>
            <h3 className="text-2xl font-semibold mt-1">{value}</h3>
            {change && (
              <div className="flex items-center mt-1">
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  className={`h-4 w-4 ${change.isPositive ? 'text-green-500' : 'text-red-500'} mr-1`} 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  {change.isPositive ? (
                    <path 
                      fillRule="evenodd" 
                      d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" 
                      clipRule="evenodd" 
                    />
                  ) : (
                    <path 
                      fillRule="evenodd" 
                      d="M12 13a1 1 0 100 2h5a1 1 0 001-1v-5a1 1 0 10-2 0v2.586l-4.293-4.293a1 1 0 00-1.414 0L8 9.586 3.707 5.293a1 1 0 00-1.414 1.414l5 5a1 1 0 001.414 0L11 9.414 14.586 13H12z" 
                      clipRule="evenodd" 
                    />
                  )}
                </svg>
                <span className={`text-xs ${change.isPositive ? 'text-green-500' : 'text-red-500'}`}>
                  {change.value}
                </span>
              </div>
            )}
          </div>
          <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center">
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function StatCardSkeleton() {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex justify-between items-start">
          <div>
            <Skeleton className="h-4 w-24 mb-2" />
            <Skeleton className="h-8 w-16 mb-2" />
            <Skeleton className="h-3 w-32" />
          </div>
          <Skeleton className="h-10 w-10 rounded-full" />
        </div>
      </CardContent>
    </Card>
  );
}

export default function StatsGrid() {
  const { data: stats, isLoading: isStatsLoading } = useQuery({
    queryKey: ['/api/transactions/stats'],
  });
  
  const { data: botStatus, isLoading: isBotStatusLoading } = useQuery({
    queryKey: ['/api/bot/status'],
  });
  
  if (isStatsLoading || isBotStatusLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
      </div>
    );
  }
  
  const walletBalance = botStatus?.statsData?.balance || 0;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatCard
        title="Total Transactions"
        value={stats?.total || 0}
        change={{
          value: "+12% from last week",
          isPositive: true
        }}
        icon={<BarChart className="h-5 w-5 text-primary" />}
      />
      
      <StatCard
        title="Total Buys"
        value={stats?.buys || 0}
        change={{
          value: "+8% from last week",
          isPositive: true
        }}
        icon={<Lock className="h-5 w-5 text-green-500" />}
      />
      
      <StatCard
        title="Total Sells"
        value={stats?.sells || 0}
        change={{
          value: "-5% from last week",
          isPositive: false
        }}
        icon={<BookOpen className="h-5 w-5 text-red-500" />}
      />
      
      <StatCard
        title="Wallet Balance"
        value={`${walletBalance} SOL`}
        change={{
          value: "+3.2 SOL today",
          isPositive: true
        }}
        icon={<Wallet className="h-5 w-5 text-yellow-500" />}
      />
    </div>
  );
}
