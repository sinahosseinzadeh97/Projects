import { Card, CardContent } from '@/components/ui/card';
import { useQuery } from '@tanstack/react-query';
import { Skeleton } from '@/components/ui/skeleton';
import { Check } from 'lucide-react';

export default function TransactionTracking() {
  const { data: botConfig, isLoading: isConfigLoading } = useQuery({
    queryKey: ['/api/bot/config'],
  });
  
  const { data: wallets, isLoading: isWalletsLoading } = useQuery({
    queryKey: ['/api/wallets'],
  });
  
  const { data: botStatus, isLoading: isStatusLoading } = useQuery({
    queryKey: ['/api/bot/status'],
  });
  
  const isLoading = isConfigLoading || isWalletsLoading || isStatusLoading;
  
  // Group wallets by level
  const walletsByLevel = wallets?.reduce((acc: Record<number, any[]>, wallet: any) => {
    if (!acc[wallet.level]) {
      acc[wallet.level] = [];
    }
    acc[wallet.level].push(wallet);
    return acc;
  }, {}) || {};
  
  // Get the parent wallet
  const parentWallet = wallets?.find((wallet: any) => wallet.isParent);
  
  // Prepare the tracking levels
  const trackingLevels = [];
  const trackingDepth = botConfig?.trackingDepth || 4;
  
  for (let i = 1; i <= trackingDepth; i++) {
    const levelWallets = walletsByLevel[i] || [];
    let label = '';
    let count = '';
    
    if (i === 1) {
      label = 'Parent Wallet';
      count = parentWallet ? parentWallet.address.substring(0, 4) + '...' + parentWallet.address.substring(parentWallet.address.length - 3) : '';
    } else if (i === 2) {
      label = 'Secondary Wallets';
      count = `${levelWallets.length} wallets monitored`;
    } else if (i === 3) {
      label = 'Tertiary Wallets';
      count = `${levelWallets.length} wallets monitored`;
    } else {
      label = `Level ${i} Wallets`;
      count = `${levelWallets.length} wallets monitored`;
    }
    
    trackingLevels.push({
      level: i,
      label,
      count,
      status: i === trackingDepth ? 'warning' : 'success'
    });
  }

  return (
    <Card>
      <div className="border-b border-border px-5 py-4">
        <h2 className="text-lg font-medium">Transaction Tracking</h2>
      </div>
      <CardContent className="p-5">
        <div className="flex flex-col items-center mb-4">
          <div className="w-full h-16 bg-secondary/50 rounded-lg mb-2 flex items-center justify-center relative overflow-hidden">
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-primary"></div>
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-full bg-green-500/20 flex items-center justify-center">
                <Check className="h-4 w-4 text-green-500" />
              </div>
              <div>
                <p className="text-sm font-medium">
                  {isLoading ? (
                    <Skeleton className="h-4 w-24" />
                  ) : (
                    botStatus?.status === 'active' ? 'Tracking Active' : 'Tracking Inactive'
                  )}
                </p>
                {isLoading ? (
                  <Skeleton className="h-3 w-16" />
                ) : (
                  <p className="text-xs text-muted-foreground">
                    Level {trackingDepth} Depth
                  </p>
                )}
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 gap-2 w-full">
            {isLoading ? (
              Array(trackingDepth).fill(0).map((_, i) => (
                <div key={i} className="p-3 bg-secondary/30 rounded-md">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      <Skeleton className="h-6 w-6 rounded-full mr-2" />
                      <div>
                        <Skeleton className="h-3 w-24 mb-1" />
                        <Skeleton className="h-2 w-16" />
                      </div>
                    </div>
                    <Skeleton className="h-2 w-2 rounded-full" />
                  </div>
                </div>
              ))
            ) : (
              trackingLevels.map((level) => (
                <div key={level.level} className="p-3 bg-secondary/30 rounded-md">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      <div className="h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center mr-2">
                        <span className="text-xs font-medium">{level.level}</span>
                      </div>
                      <div>
                        <p className="text-xs font-medium">{level.label}</p>
                        <p className="text-xs text-muted-foreground">{level.count}</p>
                      </div>
                    </div>
                    <span className={`h-2 w-2 rounded-full ${
                      level.status === 'success' ? 'bg-green-500' : 
                      level.status === 'warning' ? 'bg-yellow-500 animate-pulse' : 
                      'bg-red-500'
                    }`} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-border">
          <h3 className="text-sm font-medium mb-2">Current Tracking Stats</h3>
          {isStatusLoading ? (
            <div className="space-y-2">
              {Array(4).fill(0).map((_, i) => (
                <div key={i} className="flex justify-between">
                  <Skeleton className="h-3 w-32" />
                  <Skeleton className="h-3 w-8" />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-xs text-muted-foreground">Transactions Monitored:</span>
                <span className="text-xs font-medium">{botStatus?.statsData?.transactionsMonitored || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-muted-foreground">Total Wallets Tracked:</span>
                <span className="text-xs font-medium">{botStatus?.statsData?.totalWalletsTracked || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-muted-foreground">Buy Opportunities Found:</span>
                <span className="text-xs font-medium">{botStatus?.statsData?.buyOpportunitiesFound || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-muted-foreground">Sell Signals Generated:</span>
                <span className="text-xs font-medium">{botStatus?.statsData?.sellSignalsGenerated || 0}</span>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
