import Layout from '@/components/layout';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowUp, ArrowDown, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Skeleton } from '@/components/ui/skeleton';
import { useState } from 'react';

export default function Transactions() {
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const pageSize = 10;
  
  const { data: transactions, isLoading } = useQuery({
    queryKey: ['/api/transactions'],
  });
  
  // Filter transactions based on user selection and search query
  const filteredTransactions = transactions?.filter((tx: any) => {
    // Type filter
    if (filter !== 'all' && tx.type !== filter) {
      return false;
    }
    
    // Search query
    if (search) {
      const searchLower = search.toLowerCase();
      return (
        tx.tokenSymbol.toLowerCase().includes(searchLower) ||
        tx.txId.toLowerCase().includes(searchLower) ||
        tx.fromWallet.toLowerCase().includes(searchLower) ||
        tx.toWallet.toLowerCase().includes(searchLower)
      );
    }
    
    return true;
  });
  
  const totalTransactions = filteredTransactions?.length || 0;
  const totalPages = Math.ceil(totalTransactions / pageSize);
  
  const displayedTransactions = filteredTransactions?.slice(
    (page - 1) * pageSize, 
    page * pageSize
  );
  
  const handlePrevPage = () => {
    setPage((prev) => Math.max(prev - 1, 1));
  };
  
  const handleNextPage = () => {
    setPage((prev) => Math.min(prev + 1, totalPages));
  };
  
  // Format timestamp to date and time
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <Layout title="Transactions">
      <Card className="mb-6">
        <CardContent className="p-5">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <h2 className="text-lg font-semibold">Transaction History</h2>
              <p className="text-sm text-muted-foreground">
                View all transactions performed by the bot
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-2">
              <div className="relative">
                <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search transactions..."
                  className="pl-8 w-full sm:w-64"
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    setPage(1); // Reset to first page on search
                  }}
                />
              </div>
              
              <Select
                value={filter}
                onValueChange={(value) => {
                  setFilter(value);
                  setPage(1); // Reset to first page on filter change
                }}
              >
                <SelectTrigger className="w-full sm:w-32">
                  <SelectValue placeholder="Filter" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="buy">Buy</SelectItem>
                  <SelectItem value="sell">Sell</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-5">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left font-medium px-3 py-3">Type</th>
                  <th className="text-left font-medium px-3 py-3">Token</th>
                  <th className="text-left font-medium px-3 py-3">Amount</th>
                  <th className="text-left font-medium px-3 py-3">Status</th>
                  <th className="text-left font-medium px-3 py-3">Date & Time</th>
                  <th className="text-left font-medium px-3 py-3">Transaction ID</th>
                  <th className="text-right font-medium px-3 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  Array(pageSize).fill(0).map((_, i) => (
                    <tr key={i} className="border-b border-border">
                      <td className="px-3 py-3">
                        <div className="flex items-center">
                          <Skeleton className="h-6 w-6 rounded-full mr-2" />
                          <Skeleton className="h-4 w-16" />
                        </div>
                      </td>
                      <td className="px-3 py-3"><Skeleton className="h-4 w-16" /></td>
                      <td className="px-3 py-3"><Skeleton className="h-4 w-16" /></td>
                      <td className="px-3 py-3"><Skeleton className="h-6 w-24 rounded-full" /></td>
                      <td className="px-3 py-3"><Skeleton className="h-4 w-32" /></td>
                      <td className="px-3 py-3"><Skeleton className="h-4 w-48" /></td>
                      <td className="px-3 py-3 text-right"><Skeleton className="h-4 w-16 ml-auto" /></td>
                    </tr>
                  ))
                ) : displayedTransactions?.length ? (
                  displayedTransactions.map((tx: any) => (
                    <tr key={tx.id} className="border-b border-border hover:bg-secondary/30">
                      <td className="px-3 py-3">
                        <div className="flex items-center">
                          <span className={`h-6 w-6 rounded-full ${tx.type === 'buy' ? 'bg-green-500/20' : 'bg-red-500/20'} flex items-center justify-center mr-2`}>
                            {tx.type === 'buy' ? (
                              <ArrowUp className="h-3 w-3 text-green-500" />
                            ) : (
                              <ArrowDown className="h-3 w-3 text-red-500" />
                            )}
                          </span>
                          {tx.type === 'buy' ? 'Buy' : 'Sell'}
                        </div>
                      </td>
                      <td className="px-3 py-3">{tx.tokenSymbol}</td>
                      <td className="px-3 py-3">{tx.amount} SOL</td>
                      <td className="px-3 py-3">
                        <Badge
                          variant="outline"
                          className={`
                            ${tx.status === 'completed' ? 'bg-green-500/20 text-green-500' : 
                            tx.status === 'failed' ? 'bg-red-500/20 text-red-500' : 
                            'bg-yellow-500/20 text-yellow-500'}
                          `}
                        >
                          {tx.status.charAt(0).toUpperCase() + tx.status.slice(1)}
                        </Badge>
                      </td>
                      <td className="px-3 py-3">{formatTimestamp(tx.timestamp)}</td>
                      <td className="px-3 py-3">
                        <span className="font-mono text-xs">{tx.txId}</span>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <Button variant="link" className="text-primary hover:underline p-0 h-auto">
                          View Details
                        </Button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="px-3 py-6 text-center text-muted-foreground">
                      No transactions found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          <div className="mt-4 flex flex-col sm:flex-row justify-between items-center text-sm text-muted-foreground gap-4">
            <div>
              Showing {displayedTransactions?.length || 0} of {totalTransactions} transactions
            </div>
            <div className="flex items-center space-x-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={handlePrevPage}
                disabled={page === 1 || isLoading || totalPages === 0}
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Previous
              </Button>
              <div className="text-sm">
                Page {page} of {totalPages || 1}
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleNextPage}
                disabled={page === totalPages || totalPages === 0 || isLoading}
              >
                Next
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </Layout>
  );
}
