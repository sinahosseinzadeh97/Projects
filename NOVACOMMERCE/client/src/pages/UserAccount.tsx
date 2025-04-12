import { useState, useEffect } from 'react';
import { Link, useLocation } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/lib/auth';
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
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const UserAccount = () => {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const { toast } = useToast();
  const [location, navigate] = useLocation();
  const searchParams = new URLSearchParams(location.split('?')[1] || '');
  const activeTab = searchParams.get('tab') || 'profile';
  const reviewProductId = searchParams.get('reviewProduct');
  
  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, isLoading]);

  // Fetch orders
  const { data: orders, isLoading: isLoadingOrders } = useQuery({
    queryKey: ['/api/orders/user'],
    enabled: isAuthenticated && activeTab === 'orders',
  });

  // Fetch wishlist
  const { data: wishlist, isLoading: isLoadingWishlist } = useQuery({
    queryKey: ['/api/wishlist'],
    enabled: isAuthenticated && activeTab === 'wishlist',
  });

  const handleNavigation = (tab: string) => {
    navigate(`/account?tab=${tab}`);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null; // Will redirect in useEffect
  }

  // Get user initials for avatar
  const getUserInitials = () => {
    if (user.firstName && user.lastName) {
      return `${user.firstName[0]}${user.lastName[0]}`;
    }
    return user.username.substring(0, 2).toUpperCase();
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl md:text-3xl font-bold">My Account</h1>
          <Button variant="outline" onClick={logout}>
            <i className="fas fa-sign-out-alt mr-2"></i> Logout
          </Button>
        </div>
        
        <div className="flex flex-col md:flex-row gap-8">
          {/* Sidebar */}
          <div className="md:w-1/4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center mb-6">
                  <Avatar className="h-20 w-20 mb-4">
                    <AvatarFallback className="text-lg">{getUserInitials()}</AvatarFallback>
                  </Avatar>
                  <h2 className="text-xl font-bold">{user.firstName || user.username}</h2>
                  <p className="text-gray-500">{user.email}</p>
                </div>
                
                <div className="space-y-1">
                  <Button 
                    variant={activeTab === 'profile' ? 'default' : 'ghost'} 
                    className="w-full justify-start"
                    onClick={() => handleNavigation('profile')}
                  >
                    <i className="fas fa-user mr-2"></i> Profile
                  </Button>
                  <Button 
                    variant={activeTab === 'orders' ? 'default' : 'ghost'} 
                    className="w-full justify-start"
                    onClick={() => handleNavigation('orders')}
                  >
                    <i className="fas fa-shopping-bag mr-2"></i> Orders
                  </Button>
                  <Button 
                    variant={activeTab === 'wishlist' ? 'default' : 'ghost'} 
                    className="w-full justify-start"
                    onClick={() => handleNavigation('wishlist')}
                  >
                    <i className="fas fa-heart mr-2"></i> Wishlist
                  </Button>
                  <Button 
                    variant={activeTab === 'addresses' ? 'default' : 'ghost'} 
                    className="w-full justify-start"
                    onClick={() => handleNavigation('addresses')}
                  >
                    <i className="fas fa-map-marker-alt mr-2"></i> Addresses
                  </Button>
                  <Button 
                    variant={activeTab === 'reviews' ? 'default' : 'ghost'} 
                    className="w-full justify-start"
                    onClick={() => handleNavigation('reviews')}
                  >
                    <i className="fas fa-star mr-2"></i> Reviews
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
          
          {/* Main Content */}
          <div className="md:w-3/4">
            <Tabs value={activeTab} onValueChange={handleNavigation}>
              <TabsList className="w-full">
                <TabsTrigger value="profile">Profile</TabsTrigger>
                <TabsTrigger value="orders">Orders</TabsTrigger>
                <TabsTrigger value="wishlist">Wishlist</TabsTrigger>
                <TabsTrigger value="addresses">Addresses</TabsTrigger>
                <TabsTrigger value="reviews">Reviews</TabsTrigger>
              </TabsList>
              
              {/* Profile Tab */}
              <TabsContent value="profile">
                <ProfileTab user={user} />
              </TabsContent>
              
              {/* Orders Tab */}
              <TabsContent value="orders">
                <OrdersTab orders={orders} isLoading={isLoadingOrders} />
              </TabsContent>
              
              {/* Wishlist Tab */}
              <TabsContent value="wishlist">
                <WishlistTab wishlist={wishlist} isLoading={isLoadingWishlist} />
              </TabsContent>
              
              {/* Addresses Tab */}
              <TabsContent value="addresses">
                <AddressesTab />
              </TabsContent>
              
              {/* Reviews Tab */}
              <TabsContent value="reviews">
                <ReviewsTab productId={reviewProductId ? parseInt(reviewProductId) : undefined} />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
};

// Profile Tab Component
const ProfileTab = ({ user }) => {
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  
  // Form setup
  const profileFormSchema = z.object({
    firstName: z.string().optional(),
    lastName: z.string().optional(),
    email: z.string().email('Please enter a valid email address'),
    username: z.string().min(3, 'Username must be at least 3 characters'),
    currentPassword: z.string().optional(),
    newPassword: z.string().optional(),
    confirmNewPassword: z.string().optional(),
  }).refine(data => {
    if (data.newPassword && !data.currentPassword) {
      return false;
    }
    return true;
  }, {
    message: "Current password is required to set a new password",
    path: ['currentPassword'],
  }).refine(data => {
    if (data.newPassword && data.newPassword !== data.confirmNewPassword) {
      return false;
    }
    return true;
  }, {
    message: "New passwords don't match",
    path: ['confirmNewPassword'],
  });
  
  const form = useForm({
    resolver: zodResolver(profileFormSchema),
    defaultValues: {
      firstName: user.firstName || '',
      lastName: user.lastName || '',
      email: user.email || '',
      username: user.username || '',
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: '',
    },
  });
  
  const onSubmit = async (data) => {
    // This would need an API endpoint to update user profile
    toast({
      title: "Profile Updated",
      description: "Your profile has been updated successfully.",
    });
    setIsEditing(false);
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Profile Information</CardTitle>
        <CardDescription>
          View and update your personal information
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                control={form.control}
                name="firstName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>First Name</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Enter your first name" 
                        disabled={!isEditing} 
                        {...field} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="lastName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Last Name</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Enter your last name" 
                        disabled={!isEditing} 
                        {...field} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="your@email.com" 
                        type="email" 
                        disabled={!isEditing} 
                        {...field} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Username</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="username" 
                        disabled={!isEditing} 
                        {...field} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            
            {isEditing && (
              <div className="space-y-6 pt-4 border-t border-gray-200">
                <h3 className="font-medium">Change Password</h3>
                
                <FormField
                  control={form.control}
                  name="currentPassword"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Current Password</FormLabel>
                      <FormControl>
                        <Input 
                          placeholder="Enter your current password" 
                          type="password" 
                          {...field} 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormField
                    control={form.control}
                    name="newPassword"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>New Password</FormLabel>
                        <FormControl>
                          <Input 
                            placeholder="Enter new password" 
                            type="password" 
                            {...field} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="confirmNewPassword"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Confirm New Password</FormLabel>
                        <FormControl>
                          <Input 
                            placeholder="Confirm new password" 
                            type="password" 
                            {...field} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>
            )}
            
            <div className="flex justify-end space-x-2">
              {isEditing ? (
                <>
                  <Button type="button" variant="outline" onClick={() => setIsEditing(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Save Changes</Button>
                </>
              ) : (
                <Button type="button" onClick={() => setIsEditing(true)}>
                  Edit Profile
                </Button>
              )}
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

// Orders Tab Component
const OrdersTab = ({ orders, isLoading }) => {
  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    processing: 'bg-blue-100 text-blue-800',
    shipped: 'bg-indigo-100 text-indigo-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
  };
  
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>My Orders</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  if (!orders || orders.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>My Orders</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="mb-4 text-4xl text-gray-300">
              <i className="fas fa-shopping-bag"></i>
            </div>
            <h3 className="text-lg font-medium mb-2">No orders yet</h3>
            <p className="text-gray-500 mb-4">You haven't placed any orders yet.</p>
            <Button asChild>
              <Link href="/products">Start Shopping</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>My Orders</CardTitle>
        <CardDescription>
          Track and manage your orders
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order ID</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Total</TableHead>
                <TableHead>Items</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {orders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell className="font-medium">#{order.id}</TableCell>
                  <TableCell>
                    {new Date(order.createdAt).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <span className={`py-1 px-2 rounded-full text-xs ${statusColors[order.status]}`}>
                      {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                    </span>
                  </TableCell>
                  <TableCell>${order.total.toFixed(2)}</TableCell>
                  <TableCell>{order.items.length} items</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm">
                      <i className="fas fa-eye mr-1"></i> View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

// Wishlist Tab Component
const WishlistTab = ({ wishlist, isLoading }) => {
  const { toast } = useToast();
  
  const handleRemoveFromWishlist = async (productId: number) => {
    try {
      await apiRequest('DELETE', `/api/wishlist/${productId}`);
      toast({
        title: "Removed from wishlist",
        description: "Item has been removed from your wishlist",
      });
      // Would need to invalidate the query to refresh the list
    } catch (error) {
      toast({
        title: "Error",
        description: "Could not remove item from wishlist",
        variant: "destructive",
      });
    }
  };
  
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>My Wishlist</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  if (!wishlist || wishlist.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>My Wishlist</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="mb-4 text-4xl text-gray-300">
              <i className="fas fa-heart"></i>
            </div>
            <h3 className="text-lg font-medium mb-2">Your wishlist is empty</h3>
            <p className="text-gray-500 mb-4">Save items you'd like to purchase later.</p>
            <Button asChild>
              <Link href="/products">Explore Products</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>My Wishlist</CardTitle>
        <CardDescription>
          Products you've saved for later
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {wishlist.map((item) => (
            <Card key={item.id} className="overflow-hidden">
              <div className="relative h-48">
                <img 
                  src={item.product.imageUrl || 'https://via.placeholder.com/300x200?text=Product'} 
                  alt={item.product.name} 
                  className="w-full h-full object-cover"
                />
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="absolute top-2 right-2 bg-white hover:bg-gray-100 text-red-500"
                  onClick={() => handleRemoveFromWishlist(item.productId)}
                >
                  <i className="fas fa-times"></i>
                </Button>
              </div>
              <CardContent className="p-4">
                <Link 
                  href={`/product/${item.product.slug || item.productId}`}
                  className="font-medium text-lg hover:text-primary-600 block mb-1"
                >
                  {item.product.name}
                </Link>
                <p className="text-gray-600 mb-2 text-sm line-clamp-2">
                  {item.product.description || 'No description available'}
                </p>
                <div className="flex justify-between items-center mt-2">
                  <span className="font-bold">${item.product.price.toFixed(2)}</span>
                  <Button asChild size="sm">
                    <Link href={`/product/${item.product.slug || item.productId}`}>
                      View Product
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// Addresses Tab Component
const AddressesTab = () => {
  const [addresses, setAddresses] = useState([
    {
      id: 1,
      name: 'Home',
      isDefault: true,
      address: '123 Main St',
      city: 'New York',
      state: 'NY',
      zipCode: '10001',
      country: 'United States',
    },
    {
      id: 2,
      name: 'Work',
      isDefault: false,
      address: '456 Office Blvd',
      city: 'Chicago',
      state: 'IL',
      zipCode: '60601',
      country: 'United States',
    },
  ]);
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>My Addresses</CardTitle>
        <CardDescription>
          Manage your shipping addresses
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {addresses.map((address) => (
            <Card key={address.id}>
              <CardContent className="p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-medium">{address.name}</h3>
                    {address.isDefault && (
                      <span className="text-xs bg-primary-100 text-primary-800 px-2 py-0.5 rounded-full">
                        Default
                      </span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="sm">
                      <i className="fas fa-pencil-alt mr-1"></i> Edit
                    </Button>
                    <Button variant="ghost" size="sm" className="text-red-500">
                      <i className="fas fa-trash-alt mr-1"></i> Delete
                    </Button>
                  </div>
                </div>
                <div className="text-gray-600 text-sm">
                  <p>{address.address}</p>
                  <p>{address.city}, {address.state} {address.zipCode}</p>
                  <p>{address.country}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        
        <Button>
          <i className="fas fa-plus mr-2"></i> Add New Address
        </Button>
      </CardContent>
    </Card>
  );
};

// Reviews Tab Component
const ReviewsTab = ({ productId }) => {
  const { toast } = useToast();
  const [showReviewForm, setShowReviewForm] = useState(!!productId);
  
  // Product detail if we're reviewing a specific product
  const { data: product } = useQuery({
    queryKey: [`/api/products/${productId}`],
    enabled: !!productId,
  });
  
  // Form setup
  const reviewFormSchema = z.object({
    productId: z.number(),
    rating: z.number().min(1, 'Please select a rating').max(5),
    comment: z.string().min(10, 'Please write a comment of at least 10 characters'),
  });
  
  const form = useForm({
    resolver: zodResolver(reviewFormSchema),
    defaultValues: {
      productId: productId || 0,
      rating: 5,
      comment: '',
    },
  });
  
  const onSubmit = async (data) => {
    try {
      await apiRequest('POST', '/api/reviews', data);
      toast({
        title: "Review Submitted",
        description: "Thank you for your review!",
      });
      setShowReviewForm(false);
      form.reset();
    } catch (error) {
      toast({
        title: "Error",
        description: "Could not submit your review. Please try again.",
        variant: "destructive",
      });
    }
  };
  
  // Star rating component
  const StarRating = ({ value, onChange }) => {
    return (
      <div className="flex">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            className={`text-2xl ${star <= value ? 'text-amber-500' : 'text-gray-300'}`}
            onClick={() => onChange(star)}
          >
            <i className="fas fa-star"></i>
          </button>
        ))}
      </div>
    );
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>My Reviews</CardTitle>
        <CardDescription>
          View and write product reviews
        </CardDescription>
      </CardHeader>
      <CardContent>
        {showReviewForm && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>
                {product 
                  ? `Write a Review for ${product.name}` 
                  : 'Write a Review'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  {!productId && (
                    <FormField
                      control={form.control}
                      name="productId"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Select Product</FormLabel>
                          <FormControl>
                            <select 
                              className="w-full border border-gray-300 rounded-md px-4 py-2"
                              {...field}
                              onChange={(e) => field.onChange(parseInt(e.target.value))}
                            >
                              <option value="">Select a product</option>
                              <option value="1">Product 1</option>
                              <option value="2">Product 2</option>
                            </select>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  )}
                  
                  <FormField
                    control={form.control}
                    name="rating"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Rating</FormLabel>
                        <FormControl>
                          <StarRating 
                            value={field.value} 
                            onChange={(value) => field.onChange(value)} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="comment"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Review</FormLabel>
                        <FormControl>
                          <Textarea 
                            placeholder="Write your review here..." 
                            className="min-h-[120px]"
                            {...field} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <div className="flex justify-end gap-2">
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={() => setShowReviewForm(false)}
                    >
                      Cancel
                    </Button>
                    <Button type="submit">Submit Review</Button>
                  </div>
                </form>
              </Form>
            </CardContent>
          </Card>
        )}
        
        <div className="text-center py-8">
          <div className="mb-4 text-4xl text-gray-300">
            <i className="fas fa-star"></i>
          </div>
          <h3 className="text-lg font-medium mb-2">No reviews yet</h3>
          <p className="text-gray-500 mb-4">You haven't written any reviews.</p>
          {!showReviewForm && (
            <Button onClick={() => setShowReviewForm(true)}>
              Write a Review
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default UserAccount;
