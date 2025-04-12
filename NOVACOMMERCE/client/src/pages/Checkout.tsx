import { useState, useEffect } from 'react';
import { Link, useLocation } from 'wouter';
import { useStripe, Elements, PaymentElement, useElements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { useCart } from '@/lib/cartStore';
import { useAuth } from '@/lib/auth';
import { apiRequest } from '@/lib/queryClient';
import { useToast } from '@/hooks/use-toast';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Separator } from '@/components/ui/separator';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

// Make sure to call `loadStripe` outside of a component's render to avoid recreating the `Stripe` object on every render.
if (!import.meta.env.VITE_STRIPE_PUBLIC_KEY) {
  console.warn('Missing required Stripe key: VITE_STRIPE_PUBLIC_KEY. Payment functionality will be limited.');
}

const stripePromise = import.meta.env.VITE_STRIPE_PUBLIC_KEY 
  ? loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY) 
  : null;

// Form schema
const checkoutFormSchema = z.object({
  firstName: z.string().min(2, 'First name is required'),
  lastName: z.string().min(2, 'Last name is required'),
  email: z.string().email('Invalid email address'),
  phone: z.string().min(10, 'Valid phone number is required'),
  address: z.string().min(5, 'Address is required'),
  city: z.string().min(2, 'City is required'),
  state: z.string().min(2, 'State is required'),
  zipCode: z.string().min(5, 'ZIP code is required'),
  country: z.string().min(2, 'Country is required'),
  saveInfo: z.boolean().optional(),
});

// Checkout form component
const CheckoutForm = ({ onSubmit, formData, isProcessing }) => {
  const form = useForm({
    resolver: zodResolver(checkoutFormSchema),
    defaultValues: formData,
  });
  
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="firstName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>First Name</FormLabel>
                <FormControl>
                  <Input placeholder="John" {...field} />
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
                  <Input placeholder="Doe" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input placeholder="your@email.com" type="email" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <FormField
            control={form.control}
            name="phone"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Phone</FormLabel>
                <FormControl>
                  <Input placeholder="(555) 123-4567" type="tel" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        
        <FormField
          control={form.control}
          name="address"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Address</FormLabel>
              <FormControl>
                <Input placeholder="123 Main St" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <FormField
            control={form.control}
            name="city"
            render={({ field }) => (
              <FormItem className="col-span-2">
                <FormLabel>City</FormLabel>
                <FormControl>
                  <Input placeholder="New York" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <FormField
            control={form.control}
            name="state"
            render={({ field }) => (
              <FormItem>
                <FormLabel>State</FormLabel>
                <FormControl>
                  <Input placeholder="NY" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <FormField
            control={form.control}
            name="zipCode"
            render={({ field }) => (
              <FormItem>
                <FormLabel>ZIP Code</FormLabel>
                <FormControl>
                  <Input placeholder="10001" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        
        <FormField
          control={form.control}
          name="country"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Country</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a country" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="US">United States</SelectItem>
                  <SelectItem value="CA">Canada</SelectItem>
                  <SelectItem value="UK">United Kingdom</SelectItem>
                  <SelectItem value="AU">Australia</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <Button type="submit" className="w-full" disabled={isProcessing}>
          {isProcessing ? 'Processing...' : 'Continue to Payment'}
        </Button>
      </form>
    </Form>
  );
};

// Payment form component with Stripe
const PaymentForm = () => {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();
  const { cart, clearCart } = useCart();
  const [, navigate] = useLocation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);

    try {
      const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/account?tab=orders&status=success`,
        },
      });

      if (error) {
        toast({
          title: "Payment Failed",
          description: error.message,
          variant: "destructive",
        });
      } else {
        // If we get here, the payment was successful.
        // However, the confirmPayment will redirect, so this code might not run.
        toast({
          title: "Payment Successful",
          description: "Thank you for your purchase!",
        });
        clearCart();
        navigate('/account?tab=orders&status=success');
      }
    } catch (err: any) {
      toast({
        title: "Payment Error",
        description: err.message || "An unexpected error occurred",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <PaymentElement />
      <Button 
        type="submit" 
        className="w-full" 
        disabled={!stripe || isProcessing}
      >
        {isProcessing ? 'Processing...' : 'Complete Order'}
      </Button>
    </form>
  );
};

const Checkout = () => {
  const { cart, getCartTotal } = useCart();
  const { user, isAuthenticated, isLoading } = useAuth();
  const [, navigate] = useLocation();
  const [step, setStep] = useState(1);
  const [shippingInfo, setShippingInfo] = useState({
    firstName: user?.firstName || '',
    lastName: user?.lastName || '',
    email: user?.email || '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    country: 'US',
    saveInfo: true,
  });
  const [clientSecret, setClientSecret] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login?redirect=checkout');
    }
  }, [isAuthenticated, isLoading]);

  // Redirect if cart is empty
  useEffect(() => {
    if (cart && cart.items && cart.items.length === 0) {
      navigate('/cart');
      toast({
        title: "Empty Cart",
        description: "Your cart is empty. Add some products before checkout.",
        variant: "destructive",
      });
    }
  }, [cart]);

  // Create payment intent when proceeding to payment
  useEffect(() => {
    if (step === 2 && !clientSecret) {
      const createIntent = async () => {
        try {
          const response = await apiRequest('POST', '/api/payment/create-intent', {
            amount: getCartTotal()
          });
          
          const data = await response.json();
          setClientSecret(data.clientSecret);
        } catch (error: any) {
          toast({
            title: "Payment Setup Failed",
            description: error.message || "Could not initialize payment. Please try again.",
            variant: "destructive",
          });
          setStep(1);
        }
      };
      
      createIntent();
    }
  }, [step]);

  const handleShippingSubmit = async (data) => {
    setIsProcessing(true);
    
    try {
      // Create order in database
      const orderData = {
        total: getCartTotal(),
        shippingAddress: data.address,
        shippingCity: data.city,
        shippingState: data.state,
        shippingZip: data.zipCode,
        shippingCountry: data.country,
        items: cart?.items.map(item => ({
          productId: item.productId,
          quantity: item.quantity,
          price: item.product.price
        }))
      };
      
      // Save shipping info
      setShippingInfo(data);
      
      // Move to payment step
      setStep(2);
    } catch (error: any) {
      toast({
        title: "Checkout Error",
        description: error.message || "There was a problem with your order. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // Calculate totals
  const subtotal = getCartTotal();
  const shipping = subtotal > 50 ? 0 : 10;
  const tax = subtotal * 0.08; // 8% tax
  const total = subtotal + shipping + tax;

  if (isLoading || !cart) {
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
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl md:text-3xl font-bold mb-6">Checkout</h1>
        
        {/* Checkout Progress */}
        <div className="mb-8">
          <div className="flex items-center">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
              1
            </div>
            <div className={`flex-1 h-1 mx-2 ${step >= 2 ? 'bg-primary-600' : 'bg-gray-200'}`}></div>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
              2
            </div>
          </div>
          <div className="flex justify-between mt-2 text-sm">
            <span className={step >= 1 ? 'text-primary-600 font-medium' : 'text-gray-500'}>Shipping</span>
            <span className={step >= 2 ? 'text-primary-600 font-medium' : 'text-gray-500'}>Payment</span>
          </div>
        </div>
        
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Checkout Form */}
          <div className="lg:w-8/12">
            <Card>
              <CardHeader>
                <CardTitle>{step === 1 ? 'Shipping Information' : 'Payment'}</CardTitle>
                <CardDescription>
                  {step === 1 
                    ? 'Enter your shipping details to continue' 
                    : 'Complete your payment to place your order'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {step === 1 ? (
                  <CheckoutForm 
                    onSubmit={handleShippingSubmit} 
                    formData={shippingInfo}
                    isProcessing={isProcessing}
                  />
                ) : (
                  <div>
                    {clientSecret && stripePromise ? (
                      <Elements stripe={stripePromise} options={{ clientSecret }}>
                        <PaymentForm />
                      </Elements>
                    ) : (
                      <div className="flex justify-center items-center h-40">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
              <CardFooter>
                {step === 2 && (
                  <Button 
                    variant="outline" 
                    className="w-full" 
                    onClick={() => setStep(1)}
                    disabled={isProcessing}
                  >
                    Back to Shipping
                  </Button>
                )}
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
                <Accordion type="single" collapsible defaultValue="items">
                  <AccordionItem value="items">
                    <AccordionTrigger>
                      Items ({cart.items.length})
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="space-y-3">
                        {cart.items.map((item) => (
                          <div key={item.id} className="flex items-center gap-3">
                            <img 
                              src={item.product.imageUrl || 'https://via.placeholder.com/50x50?text=Product'} 
                              alt={item.product.name} 
                              className="w-12 h-12 object-cover rounded-md"
                            />
                            <div className="flex-1">
                              <div className="font-medium">{item.product.name}</div>
                              <div className="text-sm text-gray-500">Qty: {item.quantity}</div>
                            </div>
                            <div className="font-medium">${(item.product.price * item.quantity).toFixed(2)}</div>
                          </div>
                        ))}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
                
                <Separator />
                
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
                
                <Separator />
                
                <div className="flex justify-between font-bold">
                  <span>Total</span>
                  <span>${total.toFixed(2)}</span>
                </div>
                
                <div className="pt-4 text-center text-sm text-gray-500">
                  <p>Secure Payment</p>
                  <div className="flex justify-center mt-2 space-x-2">
                    <i className="fab fa-cc-visa text-xl"></i>
                    <i className="fab fa-cc-mastercard text-xl"></i>
                    <i className="fab fa-cc-amex text-xl"></i>
                    <i className="fab fa-cc-paypal text-xl"></i>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex-col">
                <Button asChild variant="outline" className="w-full">
                  <Link href="/cart">Back to Cart</Link>
                </Button>
              </CardFooter>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
