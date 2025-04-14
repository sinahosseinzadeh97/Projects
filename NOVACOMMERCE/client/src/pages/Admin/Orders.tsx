import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
import { useToast } from '@/hooks/use-toast';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const Orders = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [orderDetails, setOrderDetails] = useState(null);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);

  // Fetch all orders
  const { data: orders, isLoading } = useQuery({
    queryKey: ['/api/admin/orders'],
  });

  // Update order status mutation
  const updateOrderStatusMutation = useMutation({
    mutationFn: async ({ orderId, status }: { orderId: number, status: string }) => {
      await apiRequest('PUT', `/api/admin/orders/${orderId}/status`, { status });
    },
    onSuccess: () => {
      toast({
        title: "Order updated",
        description: "The order status has been updated successfully",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/admin/orders'] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update order status",
        variant: "destructive",
      });
    },
  });

  // Handle status change
  const handleStatusChange = (orderId: number, status: string) => {
    updateOrderStatusMutation.mutate({ orderId, status });
  };

  // View order details
  const handleViewOrder = (order) => {
    setOrderDetails(order);
    setIsViewModalOpen(true);
  };

  // Filter orders based on search query and status
  const filteredOrders = orders?.filter(order => {
    const matchesSearch = searchQuery === '' || 
      order.id.toString().includes(searchQuery) ||
      order.userId.toString().includes(searchQuery);
    
    const matchesStatus = statusFilter === '' || order.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  // Group orders by status for tabs
  const ordersByStatus = {
    all: filteredOrders || [],
    pending: filteredOrders?.filter(order => order.status === 'pending') || [],
    processing: filteredOrders?.filter(order => order.status === 'processing') || [],
    shipped: filteredOrders?.filter(order => order.status === 'shipped') || [],
    delivered: filteredOrders?.filter(order => order.status === 'delivered') || [],
    cancelled: filteredOrders?.filter(order => order.status === 'cancelled') || [],
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Get status badge
  const getStatusBadge = (status) => {
    const statusMap = {
      pending: <Badge variant="outline" className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Pending</Badge>,
      processing: <Badge variant="outline" className="bg-blue-100 text-blue-800 hover:bg-blue-100">Processing</Badge>,
      shipped: <Badge variant="outline" className="bg-indigo-100 text-indigo-800 hover:bg-indigo-100">Shipped</Badge>,
      delivered: <Badge variant="outline" className="bg-green-100 text-green-800 hover:bg-green-100">Delivered</Badge>,
      cancelled: <Badge variant="outline" className="bg-red-100 text-red-800 hover:bg-red-100">Cancelled</Badge>,
    };
    
    return statusMap[status] || <Badge variant="outline">Unknown</Badge>;
  };

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Orders Management</h1>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search by Order ID or Customer ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </div>
            <div className="w-full md:w-48">
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="processing">Processing</SelectItem>
                  <SelectItem value="shipped">Shipped</SelectItem>
                  <SelectItem value="delivered">Delivered</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Orders Tabs */}
      <Tabs defaultValue="all" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="all">
            All Orders ({ordersByStatus.all.length})
          </TabsTrigger>
          <TabsTrigger value="pending">
            Pending ({ordersByStatus.pending.length})
          </TabsTrigger>
          <TabsTrigger value="processing">
            Processing ({ordersByStatus.processing.length})
          </TabsTrigger>
          <TabsTrigger value="shipped">
            Shipped ({ordersByStatus.shipped.length})
          </TabsTrigger>
          <TabsTrigger value="delivered">
            Delivered ({ordersByStatus.delivered.length})
          </TabsTrigger>
          <TabsTrigger value="cancelled">
            Cancelled ({ordersByStatus.cancelled.length})
          </TabsTrigger>
        </TabsList>

        {Object.keys(ordersByStatus).map((status) => (
          <TabsContent key={status} value={status}>
            <Card>
              <CardHeader>
                <CardTitle>
                  {status.charAt(0).toUpperCase() + status.slice(1)} Orders
                </CardTitle>
                <CardDescription>
                  {ordersByStatus[status].length} orders found
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex justify-center items-center h-48">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Order ID</TableHead>
                          <TableHead>Customer</TableHead>
                          <TableHead>Date</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Items</TableHead>
                          <TableHead>Total</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {ordersByStatus[status].map(order => (
                          <TableRow key={order.id}>
                            <TableCell className="font-medium">#{order.id}</TableCell>
                            <TableCell>User #{order.userId}</TableCell>
                            <TableCell>{formatDate(order.createdAt)}</TableCell>
                            <TableCell>{getStatusBadge(order.status)}</TableCell>
                            <TableCell>{order.items.length} items</TableCell>
                            <TableCell>${order.total.toFixed(2)}</TableCell>
                            <TableCell>
                              <div className="flex space-x-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleViewOrder(order)}
                                >
                                  View
                                </Button>
                                
                                <Select 
                                  defaultValue={order.status}
                                  onValueChange={(value) => handleStatusChange(order.id, value)}
                                  disabled={updateOrderStatusMutation.isPending}
                                >
                                  <SelectTrigger className="w-28 h-8 text-xs">
                                    <SelectValue placeholder="Update Status" />
                                  </SelectTrigger>
                                  <SelectContent>
                                    <SelectItem value="pending">Set Pending</SelectItem>
                                    <SelectItem value="processing">Set Processing</SelectItem>
                                    <SelectItem value="shipped">Set Shipped</SelectItem>
                                    <SelectItem value="delivered">Set Delivered</SelectItem>
                                    <SelectItem value="cancelled">Set Cancelled</SelectItem>
                                  </SelectContent>
                                </Select>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                        
                        {ordersByStatus[status].length === 0 && (
                          <TableRow>
                            <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                              No orders found
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {/* Order Details Modal */}
      <Dialog open={isViewModalOpen} onOpenChange={setIsViewModalOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Order Details - #{orderDetails?.id}</DialogTitle>
            <DialogDescription>
              Placed on {formatDate(orderDetails?.createdAt)}
            </DialogDescription>
          </DialogHeader>
          
          {orderDetails && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Customer Information</h3>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p><strong>Customer ID:</strong> {orderDetails.userId}</p>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Shipping Address</h3>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p>{orderDetails.shippingAddress}</p>
                    <p>{orderDetails.shippingCity}, {orderDetails.shippingState} {orderDetails.shippingZip}</p>
                    <p>{orderDetails.shippingCountry}</p>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">Order Status</h3>
                <div className="flex items-center space-x-3">
                  {getStatusBadge(orderDetails.status)}
                  
                  <Select 
                    value={orderDetails.status}
                    onValueChange={(value) => handleStatusChange(orderDetails.id, value)}
                    disabled={updateOrderStatusMutation.isPending}
                  >
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Update Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pending">Set Pending</SelectItem>
                      <SelectItem value="processing">Set Processing</SelectItem>
                      <SelectItem value="shipped">Set Shipped</SelectItem>
                      <SelectItem value="delivered">Set Delivered</SelectItem>
                      <SelectItem value="cancelled">Set Cancelled</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">Order Items</h3>
                <div className="bg-gray-50 rounded-md overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Product</TableHead>
                        <TableHead>Price</TableHead>
                        <TableHead>Quantity</TableHead>
                        <TableHead>Total</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {orderDetails.items.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell>
                            <div className="flex items-center space-x-3">
                              <div className="h-10 w-10 rounded bg-gray-200 overflow-hidden">
                                {item.product.imageUrl ? (
                                  <img
                                    src={item.product.imageUrl}
                                    alt={item.product.name}
                                    className="h-full w-full object-cover"
                                  />
                                ) : (
                                  <div className="flex items-center justify-center h-full text-gray-400">
                                    <i className="fas fa-box"></i>
                                  </div>
                                )}
                              </div>
                              <div>
                                <div className="font-medium">{item.product.name}</div>
                                <div className="text-xs text-gray-500">ID: {item.productId}</div>
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>${item.price.toFixed(2)}</TableCell>
                          <TableCell>{item.quantity}</TableCell>
                          <TableCell>${(item.price * item.quantity).toFixed(2)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-md">
                <div className="flex justify-between mb-2">
                  <span>Subtotal:</span>
                  <span>${orderDetails.total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span>Shipping:</span>
                  <span>Calculated at checkout</span>
                </div>
                <div className="flex justify-between font-bold pt-2 border-t border-gray-200">
                  <span>Total:</span>
                  <span>${orderDetails.total.toFixed(2)}</span>
                </div>
              </div>
              
              {orderDetails.paymentIntentId && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Payment Information</h3>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p><strong>Payment ID:</strong> {orderDetails.paymentIntentId}</p>
                  </div>
                </div>
              )}
              
              <div className="flex justify-end">
                <Button variant="outline" onClick={() => setIsViewModalOpen(false)}>Close</Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Orders;
