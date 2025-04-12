import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronRight, ArrowUp, ArrowDown, ChevronLeft } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Skeleton } from '@/components/ui/skeleton';
import { useState } from 'react';
import { Link } from 'wouter';

interface TransactionProps {
  transaction: {
    id: number;
    txId: string;
    type: string;
    tokenSymbol: string;
    amount: number;
    status: string;
    timestamp: string;
  };
}

function Transaction({ transaction }: TransactionProps) {
  const isBuy = transaction.type === 'buy';
  
  // Format the timestamp to show relative time (e.g., "2 min ago")
  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.round(diffMs / 60000);
    
    if (diffMins < 60) {
      return `${diffMins} min ago`;
    } else if (diffMins < 1440) {
      return `${Math.floor(diffMins / 60)} hours ago`;
    } else {
      return `${Math.floor(diffMins / 1440)} days ago`;
    }
  };

  return (
    <tr className="border-b border-border hover:bg-secondary/30">
      <td className="px-2 py-3">
        <div className="flex items-center">
          <span className={`h-6 w-6 rounded-full ${isBuy ? 'bg-green-500/20' : 'bg-red-500/20'} flex items-center justify-center mr-2`}>
            {isBuy ? (
              <ArrowUp className="h-3 w-3 text-green-500" />
            ) : (
              <ArrowDown className="h-3 w-3 text-red-500" />
            )}
          </span>
          {isBuy ? 'Buy' : 'Sell'}
        </div>
      </td>
      <td className="px-2 py-3">{transaction.tokenSymbol}</td>
      <td className="px-2 py-3">{transaction.amount} SOL</td>
      <td className="px-2 py-3">
        <Badge
          variant="outline"
          className={`
            ${transaction.status === 'completed' ? 'bg-green-500/20 text-green-500' : 
            transaction.status === 'failed' ? 'bg-red-500/20 text-red-500' : 
            'bg-yellow-500/20 text-yellow-500'}
          `}
        >
          {transaction.status.charAt(0).toUpperCase() + transaction.status.slice(1)}
        </Badge>
      </td>
      <td className="px-2 py-3">{formatTimeAgo(transaction.timestamp)}</td>
      <td className="px-2 py-3 text-right">
        <Link href={`/transactions/${transaction.id}`}>
          <Button variant="link" className="text-primary hover:underline p-0 h-auto">
            View
          </Button>
        </Link>
      </td>
    </tr>
  );
}

function TransactionSkeleton() {
  return (
    <tr className="border-b border-border">
      <td className="px-2 py-3">
        <div className="flex items-center">
          <Skeleton className="h-6 w-6 rounded-full mr-2" />
          <Skeleton className="h-4 w-16" />
        </div>
      </td>
      <td className="px-2 py-3"><Skeleton className="h-4 w-12" /></td>
      <td className="px-2 py-3"><Skeleton className="h-4 w-16" /></td>
      <td className="px-2 py-3"><Skeleton className="h-6 w-20 rounded-full" /></td>
      <td className="px-2 py-3"><Skeleton className="h-4 w-16" /></td>
      <td className="px-2 py-3 text-right"><Skeleton className="h-4 w-8 ml-auto" /></td>
    </tr>
  );
}

export default function RecentTransactions() {
  const [page, setPage] = useState(1);
  const pageSize = 4;
  
  const { data: transactions, isLoading } = useQuery({
    queryKey: ['/api/transactions'],
  });
  
  const totalTransactions = transactions?.length || 0;
  const totalPages = Math.ceil(totalTransactions / pageSize);
  
  const displayedTransactions = transactions?.slice(
    (page - 1) * pageSize, 
    page * pageSize
  );
  
  const handlePrevPage = () => {
    setPage((prev) => Math.max(prev - 1, 1));
  };
  
  const handleNextPage = () => {
    setPage((prev) => Math.min(prev + 1, totalPages));
  };

  return (
    <Card>
      <div className="border-b border-border px-5 py-4 flex justify-between items-center">
        <h2 className="text-lg font-medium">Recent Transactions</h2>
        <Link href="/transactions">
          <Button variant="link" className="text-primary hover:underline p-0 h-auto">
            View All
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </Link>
      </div>
      <CardContent className="p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left font-medium px-2 py-3">Type</th>
                <th className="text-left font-medium px-2 py-3">Token</th>
                <th className="text-left font-medium px-2 py-3">Amount</th>
                <th className="text-left font-medium px-2 py-3">Status</th>
                <th className="text-left font-medium px-2 py-3">Time</th>
                <th className="text-right font-medium px-2 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <>
                  <TransactionSkeleton />
                  <TransactionSkeleton />
                  <TransactionSkeleton />
                  <TransactionSkeleton />
                </>
              ) : displayedTransactions?.length ? (
                displayedTransactions.map((tx) => (
                  <Transaction key={tx.id} transaction={tx} />
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-2 py-6 text-center text-muted-foreground">
                    No transactions found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        <div className="mt-4 flex justify-between items-center text-sm text-muted-foreground">
          <div>
            Showing {displayedTransactions?.length || 0} of {totalTransactions} transactions
          </div>
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline" 
              size="icon" 
              onClick={handlePrevPage}
              disabled={page === 1 || isLoading}
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
            <Button 
              variant="outline" 
              size="icon" 
              onClick={handleNextPage}
              disabled={page === totalPages || totalPages === 0 || isLoading}
            >
              <ChevronRight className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
