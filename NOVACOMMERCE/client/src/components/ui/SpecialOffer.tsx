import { useState, useEffect } from 'react';
import { Link } from 'wouter';

interface CountdownTimerProps {
  targetDate: Date;
}

interface SpecialOfferProps {
  product: {
    id: number;
    name: string;
    slug: string;
    description: string;
    imageUrl: string;
  };
  targetDate: Date;
}

const CountdownTimer = ({ targetDate }: CountdownTimerProps) => {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0
  });
  
  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date();
      const difference = targetDate.getTime() - now.getTime();
      
      if (difference > 0) {
        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);
        
        setTimeLeft({ days, hours, minutes, seconds });
      } else {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 });
      }
    };
    
    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 1000);
    
    return () => clearInterval(timer);
  }, [targetDate]);
  
  return (
    <div className="flex gap-4 mb-6">
      <div className="text-center">
        <div className="bg-gray-100 rounded-lg p-2 mb-1">
          <span className="text-xl font-bold">{timeLeft.days}</span>
        </div>
        <span className="text-xs text-gray-500">Days</span>
      </div>
      <div className="text-center">
        <div className="bg-gray-100 rounded-lg p-2 mb-1">
          <span className="text-xl font-bold">{timeLeft.hours.toString().padStart(2, '0')}</span>
        </div>
        <span className="text-xs text-gray-500">Hours</span>
      </div>
      <div className="text-center">
        <div className="bg-gray-100 rounded-lg p-2 mb-1">
          <span className="text-xl font-bold">{timeLeft.minutes.toString().padStart(2, '0')}</span>
        </div>
        <span className="text-xs text-gray-500">Mins</span>
      </div>
      <div className="text-center">
        <div className="bg-gray-100 rounded-lg p-2 mb-1">
          <span className="text-xl font-bold">{timeLeft.seconds.toString().padStart(2, '0')}</span>
        </div>
        <span className="text-xs text-gray-500">Secs</span>
      </div>
    </div>
  );
};

const SpecialOffer = ({ product, targetDate }: SpecialOfferProps) => {
  return (
    <section className="py-12 bg-primary-50">
      <div className="container mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="flex flex-col md:flex-row">
            <div className="md:w-1/2 p-6 md:p-12 flex flex-col justify-center">
              <h2 className="text-2xl md:text-3xl font-bold mb-4">Special Deal of the Month</h2>
              <p className="text-gray-600 mb-6">{product.description}</p>
              
              <CountdownTimer targetDate={targetDate} />
              
              <Link 
                href={`/product/${product.slug}`}
                className="bg-primary-600 text-white text-center py-3 px-6 rounded-lg font-medium hover:bg-primary-700 transition duration-200 w-full md:w-auto"
              >
                Shop Now
              </Link>
            </div>
            <div className="md:w-1/2">
              <img 
                src={product.imageUrl || 'https://via.placeholder.com/800x600?text=Special+Offer'} 
                alt={product.name} 
                className="w-full h-full object-cover" 
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SpecialOffer;
