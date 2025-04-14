import { useState } from 'react';
import { Link, useLocation } from 'wouter';
import { useCart } from '@/lib/cartStore';
import { useAuth } from '@/lib/auth';
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const Cart = () => {
  const { cart, isLoading, removeFromCart, updateQuantity, clearCart, getCartTotal } = useCart();
  const { isAuthenticated } = useAuth();
  const [, navigate] = useLocation();
  const [promoCode, setPromoCode] = useState('');
  const [promoError, setPromoError] = useState('');
  const [discount, setDiscount] = useState(0);

  // Calculate totals
  const subtotal = getCartTotal();
  const shipping = subtotal > 50 ? 0 : 10;
  const tax = subtotal * 0.08; // 8% tax
  const total = subtotal + shipping + tax - discount;

  const handleQuantityChange = (itemId: number, newQuantity: number) => {
    if (newQuantity < 1) {
      return;
    }
    updateQuantity(itemId, newQuantity);
  };

  const handleApplyPromo = () => {
    // Simple promo code logic for demonstration
    if (promoCode.toLowerCase() === 'discount10') {
      setDiscount(subtotal * 0.1); // 10% off
      setPromoError('');
    } else if (promoCode.toLowerCase() === 'freeship') {
      setDiscount(shipping);
      setPromoError('');
    } else {
      setDiscount(0);
      setPromoError('Invalid promo code. Try "DISCOUNT10" or "FREESHIP"');
    }
  };

  const handleCheckout = () => {
    if (!isAuthenticated) {
      navigate('/login?redirect=checkout');
    } else {
      navigate('/checkout');
    }
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

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl md:text-3xl font-bold mb-6">Your Cart</h1>
      
      {cart && cart.items && cart.items.length > 0 ? (
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Cart Items */}
          <div className="lg:w-8/12">
            <Card>
              <CardHeader>
                <CardTitle>Cart Items ({cart.items.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[120px]">Product</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead>Price</TableHead>
                        <TableHead>Quantity</TableHead>
                        <TableHead>Total</TableHead>
                        <TableHead className="w-[100px]">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {cart.items.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell>
                            <Link href={`/product/${item.product.slug || item.productId}`}>
                              <img 
                                src={item.product.imageUrl || 'https://via.placeholder.com/80x80?text=Product'} 
                                alt={item.product.name} 
                                className="w-20 h-20 object-cover rounded-md"
                              />
                            </Link>
                          </TableCell>
                          <TableCell>
                            <Link href={`/product/${item.product.slug || item.productId}`} className="font-medium hover:text-primary-600">
                              {item.product.name}
                            </Link>
                          </TableCell>
                          <TableCell>${item.product.price.toFixed(2)}</TableCell>
                          <TableCell>
                            <div className="flex items-center">
                              <button 
                                className="px-2 py-1 border border-gray-300 rounded-l-md bg-gray-100 hover:bg-gray-200"
                                onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                              >
                                <i className="fas fa-minus"></i>
                              </button>
                              <Input
                                type="number"
                                value={item.quantity}
                                onChange={(e) => handleQuantityChange(item.id, parseInt(e.target.value) || 1)}
                                min="1"
                                className="w-12 rounded-none text-center"
                              />
                              <button 
                                className="px-2 py-1 border border-gray-300 rounded-r-md bg-gray-100 hover:bg-gray-200"
                                onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                              >
                                <i className="fas fa-plus"></i>
                              </button>
                            </div>
                          </TableCell>
                          <TableCell>${(item.product.price * item.quantity).toFixed(2)}</TableCell>
                          <TableCell>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="text-red-500 hover:text-red-700 hover:bg-red-50"
                              onClick={() => removeFromCart(item.id)}
                            >
                              <i className="fas fa-trash"></i>
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="outline" onClick={() => clearCart()}>Clear Cart</Button>
                <Button asChild>
                  <Link href="/products">Continue Shopping</Link>
                </Button>
              </CardFooter>
            </Card>
          </div>
          
          {/* Order Summary */}
          <div className="lg:w-4/12">
            <Card>
              <CardHeader>
                <CardTitle>Order Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal</span>
                  <span>${subtotal.toFixed(2)}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Shipping</span>
                  <span>{shipping > 0 ? `$${shipping.toFixed(2)}` : 'Free'}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax (8%)</span>
                  <span>${tax.toFixed(2)}</span>
                </div>
                
                {discount > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Discount</span>
                    <span>-${discount.toFixed(2)}</span>
                  </div>
                )}
                
                <Separator />
                
                <div className="flex justify-between font-bold">
                  <span>Total</span>
                  <span>${total.toFixed(2)}</span>
                </div>
                
                <div className="pt-4">
                  <div className="mb-4">
                    <label className="text-sm font-medium mb-1 block">Promo Code</label>
                    <div className="flex space-x-2">
                      <Input
                        placeholder="Enter promo code"
                        value={promoCode}
                        onChange={(e) => setPromoCode(e.target.value)}
                      />
                      <Button onClick={handleApplyPromo}>Apply</Button>
                    </div>
                    {promoError && <p className="text-red-500 text-xs mt-1">{promoError}</p>}
                    {discount > 0 && <p className="text-green-600 text-xs mt-1">Promo code applied successfully!</p>}
                  </div>
                  
                  <Button className="w-full" size="lg" onClick={handleCheckout}>
                    {isAuthenticated ? 'Proceed to Checkout' : 'Sign in to Checkout'}
                  </Button>
                  
                  <div className="mt-4 text-center text-sm text-gray-500">
                    <p>Secure Checkout</p>
                    <div className="flex justify-center mt-2 space-x-2">
                      <i className="fab fa-cc-visa text-xl"></i>
                      <i className="fab fa-cc-mastercard text-xl"></i>
                      <i className="fab fa-cc-amex text-xl"></i>
                      <i className="fab fa-cc-paypal text-xl"></i>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      ) : (
        <div className="text-center py-16 bg-gray-50 rounded-lg">
          <div className="mb-4 text-6xl text-gray-300">
            <i className="fas fa-shopping-cart"></i>
          </div>
          <h2 className="text-2xl font-bold mb-2">Your cart is empty</h2>
          <p className="text-gray-500 mb-6">Looks like you haven't added any products to your cart yet.</p>
          <Button asChild size="lg">
            <Link href="/products">Start Shopping</Link>
          </Button>
        </div>
      )}
    </div>
  );
};

export default Cart;
