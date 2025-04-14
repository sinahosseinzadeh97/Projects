import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";

export default function HeroSection() {
  const [, navigate] = useLocation();

  return (
    <section className="bg-primary-light bg-opacity-10 py-16">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center">
          <div className="md:w-1/2 mb-10 md:mb-0">
            <h1 className="font-poppins font-bold text-4xl md:text-5xl text-neutral-900 leading-tight mb-4">
              Find the Perfect Tutor for Your Learning Journey
            </h1>
            <p className="text-neutral-700 text-lg mb-8">
              Connect with expert tutors in any subject, book sessions that fit your schedule, and accelerate your learning.
            </p>
            <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
              <Button 
                size="lg"
                onClick={() => navigate('/tutors')}
                className="text-base"
              >
                Find a Tutor Now
              </Button>
              <Button 
                variant="outline" 
                size="lg"
                onClick={() => navigate('/become-tutor')}
                className="text-base"
              >
                Become a Tutor
              </Button>
            </div>
          </div>
          <div className="md:w-1/2">
            <img 
              src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1200&h=800&q=80" 
              alt="Students learning with tutor" 
              className="rounded-lg shadow-lg"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
