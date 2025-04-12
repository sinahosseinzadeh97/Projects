import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";

const Dashboard = () => {
  const [activeTimeFrame, setActiveTimeFrame] = useState('week');

  // Fetch orders
  const { data: orders, isLoading: ordersLoading } = useQuery({
    queryKey: ['/api/admin/orders'],
  });

  // Fetch products
  const { data: products, isLoading: productsLoading } = useQuery({
    queryKey: ['/api/products'],
  });

  // Fetch categories
  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['/api/categories'],
  });

  // Calculate statistics from orders data
  const calculateStatistics = () => {
    if (!orders) return {
      totalSales: 0,
      orderCount: 0,
      averageOrderValue: 0,
      pendingOrders: 0,
    };

    const totalSales = orders.reduce((sum, order) => sum + order.total, 0);
    const orderCount = orders.length;
    const averageOrderValue = orderCount > 0 ? totalSales / orderCount : 0;
    const pendingOrders = orders.filter(order => order.status === 'pending').length;

    return {
      totalSales,
      orderCount,
      averageOrderValue,
      pendingOrders,
    };
  };

  // Process orders data for charts
  const processOrdersForCharts = () => {
    if (!orders) return { 
      salesData: [], 
      categoryData: [], 
      statusData: [],
      topProducts: [] 
    };

    // Create a map of dates to sales totals
    const salesByDate = new Map();
    
    // Create a map of categories to sales totals
    const salesByCategory = new Map();
    
    // Create a map of order status to counts
    const ordersByStatus = new Map();
    
    // Create a map of products to sales
    const salesByProduct = new Map();

    // Initialize status counts
    ['pending', 'processing', 'shipped', 'delivered', 'cancelled'].forEach(status => {
      ordersByStatus.set(status, 0);
    });

    // Process each order
    orders.forEach(order => {
      // Format date based on active time frame
      let dateKey;
      const orderDate = new Date(order.createdAt);
      
      if (activeTimeFrame === 'week') {
        dateKey = orderDate.toLocaleDateString('en-US', { weekday: 'short' });
      } else if (activeTimeFrame === 'month') {
        dateKey = orderDate.toLocaleDateString('en-US', { day: '2-digit' });
      } else {
        dateKey = orderDate.toLocaleDateString('en-US', { month: 'short' });
      }

      // Add to sales by date
      salesByDate.set(dateKey, (salesByDate.get(dateKey) || 0) + order.total);
      
      // Add to status counts
      ordersByStatus.set(order.status, (ordersByStatus.get(order.status) || 0) + 1);

      // Process order items
      if (order.items) {
        order.items.forEach(item => {
          // Process product sales
          salesByProduct.set(item.product.id, {
            id: item.product.id,
            name: item.product.name,
            sales: (salesByProduct.get(item.product.id)?.sales || 0) + (item.price * item.quantity),
            quantity: (salesByProduct.get(item.product.id)?.quantity || 0) + item.quantity,
          });
          
          // Process category sales if product has category
          if (item.product.categoryId) {
            salesByCategory.set(item.product.categoryId, (salesByCategory.get(item.product.categoryId) || 0) + (item.price * item.quantity));
          }
        });
      }
    });

    // Prepare sales data for chart
    const salesData = Array.from(salesByDate, ([date, amount]) => ({ date, amount }));
    
    // Sort by date if needed
    if (activeTimeFrame === 'month') {
      salesData.sort((a, b) => parseInt(a.date) - parseInt(b.date));
    }

    // Prepare category data for chart
    const categoryData = Array.from(salesByCategory, ([categoryId, amount]) => {
      const category = categories?.find(cat => cat.id === categoryId);
      return {
        name: category?.name || `Category ${categoryId}`,
        value: amount,
      };
    });

    // Prepare status data for chart
    const statusData = Array.from(ordersByStatus, ([status, count]) => ({
      name: status.charAt(0).toUpperCase() + status.slice(1),
      value: count,
    }));

    // Get top 5 products by sales
    const topProducts = Array.from(salesByProduct.values())
      .sort((a, b) => b.sales - a.sales)
      .slice(0, 5);

    return {
      salesData,
      categoryData,
      statusData,
      topProducts,
    };
  };

  const { totalSales, orderCount, averageOrderValue, pendingOrders } = calculateStatistics();
  const { salesData, categoryData, statusData, topProducts } = processOrdersForCharts();

  // Colors for charts
  const COLORS = ['#6366f1', '#8884d8', '#82ca9d', '#ffc658', '#ff8042'];
  const STATUS_COLORS = {
    'Pending': '#f59e0b',
    'Processing': '#6366f1',
    'Shipped': '#3b82f6',
    'Delivered': '#10b981',
    'Cancelled': '#ef4444',
  };

  // Loading state
  if (ordersLoading || productsLoading || categoriesLoading) {
    return (
      <div className="p-4">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="bg-slate-900 text-white p-3 rounded-lg mb-6 shadow-md">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center">
            <div className="p-2 bg-primary-600 text-white rounded-lg mr-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-sm text-gray-300">DEVELOPER</h3>
              <p className="text-lg font-bold">Sina Mohammadhosseinzadeh</p>
            </div>
          </div>
          <div className="mt-3 md:mt-0">
            <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full">Active</span>
          </div>
        </div>
      </div>

      <div className="flex flex-col md:flex-row justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Dashboard Overview</h1>
        <Tabs defaultValue="week" value={activeTimeFrame} onValueChange={setActiveTimeFrame} className="w-full md:w-auto">
          <TabsList>
            <TabsTrigger value="week">This Week</TabsTrigger>
            <TabsTrigger value="month">This Month</TabsTrigger>
            <TabsTrigger value="year">This Year</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-6 flex flex-col items-center justify-center">
            <div className="rounded-full p-3 bg-primary-100 mb-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6 text-primary-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Total Sales</p>
              <h3 className="text-2xl font-bold">${totalSales.toFixed(2)}</h3>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 flex flex-col items-center justify-center">
            <div className="rounded-full p-3 bg-blue-100 mb-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6 text-blue-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Total Orders</p>
              <h3 className="text-2xl font-bold">{orderCount}</h3>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 flex flex-col items-center justify-center">
            <div className="rounded-full p-3 bg-green-100 mb-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6 text-green-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Avg. Order Value</p>
              <h3 className="text-2xl font-bold">${averageOrderValue.toFixed(2)}</h3>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 flex flex-col items-center justify-center">
            <div className="rounded-full p-3 bg-yellow-100 mb-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6 text-yellow-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Pending Orders</p>
              <h3 className="text-2xl font-bold">{pendingOrders}</h3>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sales Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Sales Overview</CardTitle>
            <CardDescription>
              {activeTimeFrame === 'week' ? 'Daily sales for this week' : 
               activeTimeFrame === 'month' ? 'Daily sales for this month' : 
               'Monthly sales for this year'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={salesData}
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`$${value}`, 'Sales']} />
                  <Legend />
                  <Line type="monotone" dataKey="amount" stroke="#6366f1" strokeWidth={2} activeDot={{ r: 8 }} name="Sales" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Order Status</CardTitle>
            <CardDescription>Distribution of order status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.name] || COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [value, 'Orders']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Best Selling Products & Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Top Products</CardTitle>
            <CardDescription>Best selling products by revenue</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={topProducts}
                  layout="vertical"
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={100} />
                  <Tooltip formatter={(value) => [`$${value}`, 'Sales']} />
                  <Bar dataKey="sales" fill="#6366f1" name="Sales" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Sales by Category</CardTitle>
            <CardDescription>Revenue distribution by category</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`$${value.toFixed(2)}`, 'Revenue']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Orders */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Orders</CardTitle>
          <CardDescription>Latest 5 orders placed on the store</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="py-3 text-left font-medium">Order ID</th>
                  <th className="py-3 text-left font-medium">Customer</th>
                  <th className="py-3 text-left font-medium">Date</th>
                  <th className="py-3 text-left font-medium">Status</th>
                  <th className="py-3 text-left font-medium">Total</th>
                </tr>
              </thead>
              <tbody>
                {orders && orders.slice(0, 5).map((order) => (
                  <tr key={order.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 font-medium">#{order.id}</td>
                    <td className="py-3">User #{order.userId}</td>
                    <td className="py-3">{new Date(order.createdAt).toLocaleDateString()}</td>
                    <td className="py-3">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                        ${order.status === 'delivered' ? 'bg-green-100 text-green-800' : 
                          order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                          order.status === 'processing' ? 'bg-blue-100 text-blue-800' : 
                          order.status === 'shipped' ? 'bg-indigo-100 text-indigo-800' : 
                          'bg-red-100 text-red-800'}`}
                      >
                        {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                      </span>
                    </td>
                    <td className="py-3">${order.total.toFixed(2)}</td>
                  </tr>
                ))}
                {(!orders || orders.length === 0) && (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-gray-500">
                      No orders found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
