import { useState } from 'react';
import { useParams, useLocation } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { useToast } from "@/hooks/use-toast";
import Navbar from "@/components/layout/navbar";
import Footer from "@/components/layout/footer";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Loader2, Check, CreditCard, AlertCircle } from "lucide-react";

// This is a simplified version without Stripe integration
const MockPaymentForm = ({ sessionData, onCompleteBooking }: { sessionData: any, onCompleteBooking: () => void }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    
    // Simulate payment processing
    setTimeout(() => {
      setIsProcessing(false);
      toast({
        title: "Booking Confirmed",
        description: "Your session has been successfully booked!",
      });
      onCompleteBooking();
    }, 1500);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Card Information</label>
          <div className="p-3 border rounded-md bg-gray-50 flex items-center">
            <CreditCard className="h-5 w-5 text-gray-400 mr-2" />
            <p className="text-gray-500">Mock payment - No real payment required</p>
          </div>
          <p className="text-xs text-gray-500">For demonstration purposes, no actual payment will be processed.</p>
        </div>
      </div>
      
      <div className="pt-4">
        <Button 
          type="submit" 
          className="w-full" 
          disabled={isProcessing}
        >
          {isProcessing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Processing...
            </>
          ) : (
            `Complete Booking - $${(sessionData?.price || 0).toFixed(2)}`
          )}
        </Button>
      </div>
    </form>
  );
};

export default function CheckoutPage() {
  const params = useParams();
  const sessionId = params.sessionId;
  const [, navigate] = useLocation();
  const { toast } = useToast();

  // Get session details
  const { data: sessionData, isLoading: isSessionLoading } = useQuery({
    queryKey: [`/api/sessions/${sessionId}`],
  });

  const handleCompleteBooking = () => {
    // Navigate to payment success page
    navigate('/payment-success');
  };

  if (isSessionLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </main>
        <Footer />
      </div>
    );
  }

  if (!sessionData) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Session not found</h2>
            <p className="text-gray-600 mb-6">The session you're trying to pay for doesn't exist or may have expired.</p>
            <Button onClick={() => navigate("/tutors")}>Browse Tutors</Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">Complete Your Booking</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
              {/* Checkout form */}
              <div className="md:col-span-3">
                <Card>
                  <CardHeader>
                    <CardTitle>Payment Details</CardTitle>
                    <CardDescription>
                      Complete your booking (Demo Mode)
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <MockPaymentForm 
                      sessionData={sessionData} 
                      onCompleteBooking={handleCompleteBooking}
                    />
                  </CardContent>
                </Card>
              </div>
              
              {/* Order summary */}
              <div className="md:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Booking Summary</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="w-12 h-12 rounded-full overflow-hidden flex-shrink-0">
                          <img
                            src={sessionData.tutor?.profilePicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(sessionData.tutor?.name || 'Tutor')}&background=3F51B5&color=fff`}
                            alt={sessionData.tutor?.name || 'Tutor'}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <div>
                          <h3 className="font-medium">{sessionData.tutor?.name || 'Tutor'}</h3>
                          <p className="text-sm text-gray-500">{sessionData.subject || 'Subject'}</p>
                        </div>
                      </div>
                      
                      <div className="bg-gray-50 p-3 rounded-md space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Date:</span>
                          <span className="font-medium">{sessionData.date || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Time:</span>
                          <span className="font-medium">{sessionData.time || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Duration:</span>
                          <span className="font-medium">{sessionData.duration || 0} minutes</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                  <Separator />
                  <CardFooter className="flex flex-col p-6 gap-4">
                    <div className="flex justify-between w-full text-lg">
                      <span className="font-medium">Total:</span>
                      <span className="font-bold">${(sessionData.price || 0).toFixed(2)}</span>
                    </div>
                    <div className="w-full">
                      <p className="text-xs text-gray-500 flex items-start gap-2">
                        <Check className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                        <span>
                          By completing this booking, you agree to Tadrees.com's terms of service and cancellation policy.
                        </span>
                      </p>
                    </div>
                  </CardFooter>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
