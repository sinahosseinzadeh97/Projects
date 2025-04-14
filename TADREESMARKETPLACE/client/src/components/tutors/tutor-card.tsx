import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Star, Clock, DollarSign } from "lucide-react";

type AvailabilityType = {
  day: string;
  time: string;
};

type TutorCardProps = {
  tutor: {
    id: number;
    name: string;
    profilePicture?: string;
    headline: string;
    bio: string;
    subjects: string[];
    hourlyRate: number;
    rating: number;
    reviewCount: number;
    availability: AvailabilityType[] | string[]; // Accept both formats
  };
  onClick: () => void;
};

export default function TutorCard({ tutor, onClick }: TutorCardProps) {
  // Format availability properly
  const formatAvailability = (availability: AvailabilityType[] | string[]) => {
    if (!availability.length) return "Not specified";
    
    // Check if availability items are objects or strings
    if (typeof availability[0] === 'object' && availability[0] !== null) {
      // It's an array of objects with day and time
      return (availability as AvailabilityType[]).map(item => 
        `${item.day} (${item.time})`
      ).join(', ');
    } else {
      // It's already an array of strings
      return (availability as string[]).join(', ');
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow duration-200">
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row">
          {/* Tutor info */}
          <div className="md:w-1/4 flex flex-col items-center text-center mb-4 md:mb-0">
            <div className="w-24 h-24 rounded-full overflow-hidden mb-2">
              <img
                src={tutor.profilePicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(tutor.name)}&background=3F51B5&color=fff`}
                alt={tutor.name}
                className="w-full h-full object-cover"
              />
            </div>
            <h3 className="font-poppins font-semibold text-lg">{tutor.name}</h3>
            <div className="flex items-center justify-center">
              <div className="flex items-center text-amber-500">
                {Array(5).fill(0).map((_, i) => (
                  <Star
                    key={i}
                    className="h-4 w-4 fill-current"
                    fill={i < Math.floor(tutor.rating) ? "currentColor" : "none"}
                  />
                ))}
              </div>
              <span className="text-neutral-medium text-sm ml-1">({tutor.reviewCount})</span>
            </div>
            <p className="text-neutral-dark text-sm mt-1 flex items-center justify-center">
              <DollarSign className="h-4 w-4 mr-0.5" />
              {tutor.hourlyRate} / hour
            </p>
          </div>
          
          {/* Tutor details */}
          <div className="md:w-2/4 md:px-6">
            <h4 className="font-medium text-lg mb-2">{tutor.headline}</h4>
            <p className="text-neutral-dark mb-3 line-clamp-2">{tutor.bio}</p>
            <div className="flex flex-wrap gap-2 mb-3">
              {tutor.subjects.slice(0, 4).map((subject, index) => (
                <Badge key={index} variant="outline" className="bg-primary/10 text-primary border-none py-1 px-3 rounded-full">
                  {subject}
                </Badge>
              ))}
            </div>
            <div className="text-neutral-dark text-sm flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              <span>Available: {formatAvailability(tutor.availability)}</span>
            </div>
          </div>
          
          {/* Action buttons */}
          <div className="md:w-1/4 flex flex-col justify-center items-center mt-4 md:mt-0">
            <Button 
              variant="link" 
              className="text-primary mb-3"
              onClick={onClick}
            >
              View Full Profile
            </Button>
            <Button 
              className="bg-[#FF9800] hover:bg-[#F57C00] text-white w-full mb-2"
              onClick={onClick}
            >
              Book Session
            </Button>
            <Button 
              variant="outline" 
              className="w-full"
              onClick={onClick}
            >
              Message
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
