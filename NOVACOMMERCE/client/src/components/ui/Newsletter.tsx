import { useState } from 'react';
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from '@/lib/queryClient';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const Newsletter = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !email.includes('@')) {
      toast({
        title: "Invalid Email",
        description: "Please enter a valid email address",
        variant: "destructive",
      });
      return;
    }
    
    setIsLoading(true);
    
    try {
      await apiRequest('POST', '/api/newsletter/subscribe', { email });
      
      toast({
        title: "Success!",
        description: "You have been subscribed to our newsletter",
      });
      
      setEmail('');
    } catch (error) {
      toast({
        title: "Subscription Failed",
        description: "Could not subscribe to newsletter. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="py-12 bg-primary-600 text-white">
      <div className="container mx-auto px-4 text-center">
        <h2 className="text-2xl md:text-3xl font-bold mb-3">Join Our Newsletter</h2>
        <p className="max-w-2xl mx-auto mb-6">Subscribe to get special offers, free giveaways, and once-in-a-lifetime deals.</p>
        
        <form onSubmit={handleSubmit} className="max-w-md mx-auto flex flex-col sm:flex-row gap-2">
          <Input
            type="email"
            placeholder="Your email address"
            required
            className="flex-grow px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-white text-gray-800"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Button 
            type="submit" 
            className="px-6 py-3 bg-white text-primary-600 font-medium rounded-lg hover:bg-gray-100 transition duration-200"
            disabled={isLoading}
          >
            {isLoading ? <span className="animate-pulse">Subscribing...</span> : 'Subscribe'}
          </Button>
        </form>
      </div>
    </section>
  );
};

export default Newsletter;
