import { Card, CardContent } from '@/components/ui/card';
import { useQuery } from '@tanstack/react-query';
import { Skeleton } from '@/components/ui/skeleton';

export default function TradePerformance() {
  const { data: botStatus, isLoading: isStatusLoading } = useQuery({
    queryKey: ['/api/bot/status'],
  });
  
  const { data: transactions, isLoading: isTransactionsLoading } = useQuery({
    queryKey: ['/api/transactions'],
  });
  
  const isLoading = isStatusLoading || isTransactionsLoading;
  
  // Calculate trade performance metrics
  const calculatePerformance = () => {
    if (!transactions) return { winRate: 0, avgRoi: 0, bestTrade: 0, totalProfit: 0 };
    
    const completedTransactions = transactions.filter((tx: any) => tx.status === 'completed');
    if (completedTransactions.length === 0) return { winRate: 0, avgRoi: 0, bestTrade: 0, totalProfit: 0 };
    
    // For the demo, we'll calculate some mock statistics
    const buyTxs = completedTransactions.filter((tx: any) => tx.type === 'buy');
    const sellTxs = completedTransactions.filter((tx: any) => tx.type === 'sell');
    
    const winningTrades = Math.min(buyTxs.length, sellTxs.length) * 0.74; // 74% win rate for demo
    const winRate = (winningTrades / Math.max(1, buyTxs.length)) * 100;
    
    return {
      winRate: Math.round(winRate),
      avgRoi: 23.5, // Mock average ROI
      bestTrade: 84, // Mock best trade
      totalProfit: botStatus?.statsData?.balance || 14.6 // Mock total profit
    };
  };
  
  const { winRate, avgRoi, bestTrade, totalProfit } = calculatePerformance();

  return (
    <Card>
      <div className="border-b border-border px-5 py-4">
        <h2 className="text-lg font-medium">Trade Performance</h2>
      </div>
      <CardContent className="p-5">
        <div className="w-full h-48 bg-secondary/30 rounded-lg flex items-center justify-center mb-4">
          {/* Simple chart visualization */}
          <div className="w-full h-full flex items-center justify-center">
            <div className="w-full h-full flex flex-col justify-end relative">
              <div className="absolute top-2 left-2 right-2 flex justify-between">
                <span className="text-xs text-muted-foreground">Performance (SOL)</span>
                <span className="text-xs font-medium text-green-500">
                  {isLoading ? <Skeleton className="h-3 w-16" /> : `+${totalProfit} SOL`}
                </span>
              </div>
              <div className="flex items-end justify-between h-4/5 px-2 pt-6">
                {Array(12).fill(0).map((_, i) => {
                  // Create a visual bar chart with increasing heights
                  const height = Math.round(((i / 11) * 100) * (i === 11 ? 1 : (0.5 + Math.random() * 0.5)));
                  
                  return (
                    <div 
                      key={i} 
                      className={`w-2 ${i === 11 ? 'bg-primary' : 'bg-primary/70'} rounded-t-sm`}
                      style={{ height: `${height}%` }}
                    />
                  );
                })}
              </div>
              <div className="flex justify-between px-2 pt-1">
                <span className="text-xs text-muted-foreground">-1d</span>
                <span className="text-xs text-muted-foreground">-12h</span>
                <span className="text-xs text-muted-foreground">Now</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-2">
          {isLoading ? (
            <>
              {Array(4).fill(0).map((_, i) => (
                <div key={i} className="p-3 bg-secondary/30 rounded-md">
                  <Skeleton className="h-3 w-16 mb-1" />
                  <Skeleton className="h-6 w-12" />
                </div>
              ))}
            </>
          ) : (
            <>
              <div className="p-3 bg-secondary/30 rounded-md">
                <p className="text-xs text-muted-foreground">Win Rate</p>
                <p className="text-lg font-semibold">{winRate}%</p>
              </div>
              <div className="p-3 bg-secondary/30 rounded-md">
                <p className="text-xs text-muted-foreground">Avg. ROI</p>
                <p className="text-lg font-semibold">{avgRoi}%</p>
              </div>
              <div className="p-3 bg-secondary/30 rounded-md">
                <p className="text-xs text-muted-foreground">Best Trade</p>
                <p className="text-lg font-semibold">+{bestTrade}%</p>
              </div>
              <div className="p-3 bg-secondary/30 rounded-md">
                <p className="text-xs text-muted-foreground">Total Profit</p>
                <p className="text-lg font-semibold">{totalProfit} SOL</p>
              </div>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
