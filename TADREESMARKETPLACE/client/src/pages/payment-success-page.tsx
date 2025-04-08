import { useEffect } from "react";
import { useLocation } from "wouter";
import { useQuery } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import Navbar from "@/components/layout/navbar";
import Footer from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, Calendar, MessageSquare } from "lucide-react";

export default function PaymentSuccessPage() {
  const [, navigate] = useLocation();
  const [location] = useLocation();
  const { toast } = useToast();

  // Parse payment_intent and payment_intent_client_secret from URL
  const params = new URLSearchParams(window.location.search);
  const paymentIntentId = params.get("payment_intent");
  const paymentIntentClientSecret = params.get("payment_intent_client_secret");

  // Get the booking ID from the redirected params if available
  const { data: paymentIntent, isLoading } = useQuery({
    queryKey: ["/api/payment-intent", paymentIntentId],
    // In a real app, you'd fetch payment information
    // Since we don't have a real endpoint, we'll simulate success
    queryFn: async () => {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Return mock data based on the payment intent
      return {
        id: paymentIntentId,
        status: "succeeded",
        metadata: {
          sessionId: "123", // In a real app, this would come from your backend
        }
      };
    },
    enabled: !!paymentIntentId && !!paymentIntentClientSecret,
  });

  useEffect(() => {
    if (paymentIntent?.status === "succeeded") {
      toast({
        title: "Payment Successful",
        description: "Your booking has been confirmed!",
      });
    }
  }, [paymentIntent, toast]);

  const handleViewBookings = () => {
    navigate("/my-bookings");
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-lg mx-auto">
            <Card className="shadow-md">
              <CardHeader className="pb-6">
                <div className="flex justify-center mb-6">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                    <CheckCircle2 className="h-10 w-10 text-green-500" />
                  </div>
                </div>
                <CardTitle className="text-2xl text-center">Payment Successful!</CardTitle>
                <CardDescription className="text-center text-base">
                  Your tutoring session has been confirmed.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="bg-gray-50 p-4 rounded-md">
                  <p className="text-center font-medium">
                    Thank you for your payment. We've sent a confirmation email with all the details of your booking.
                  </p>
                </div>
                
                <div className="space-y-4">
                  <h3 className="font-medium text-gray-700">Next Steps:</h3>
                  
                  <div className="flex items-start gap-3">
                    <Calendar className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                    <p className="text-gray-600">
                      Your session is now scheduled. You can view all your upcoming sessions in your bookings dashboard.
                    </p>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <MessageSquare className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                    <p className="text-gray-600">
                      Feel free to message your tutor before the session to discuss any specific topics you'd like to focus on.
                    </p>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex flex-col space-y-3">
                <Button 
                  className="w-full" 
                  onClick={handleViewBookings}
                >
                  View My Bookings
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => navigate("/")}
                >
                  Return to Homepage
                </Button>
              </CardFooter>
            </Card>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
