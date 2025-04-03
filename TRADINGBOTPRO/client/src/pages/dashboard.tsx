import Layout from '@/components/layout';
import BotStatus from '@/components/bot-status';
import StatsGrid from '@/components/stats-grid';
import BotConfiguration from '@/components/bot-configuration';
import RecentTransactions from '@/components/recent-transactions';
import TransactionTracking from '@/components/transaction-tracking';
import RecentNotifications from '@/components/recent-notifications';
import TradePerformance from '@/components/trade-performance';

export default function Dashboard() {
  return (
    <Layout title="Dashboard">
      {/* Bot Status */}
      <BotStatus />
      
      {/* Stats Grid */}
      <StatsGrid />
      
      {/* Main Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bot Configuration & Recent Transactions */}
        <div className="lg:col-span-2">
          <BotConfiguration />
          <div className="mt-6">
            <RecentTransactions />
          </div>
        </div>
        
        {/* Right Column */}
        <div className="space-y-6">
          <TransactionTracking />
          <RecentNotifications />
          <TradePerformance />
        </div>
      </div>
    </Layout>
  );
}
