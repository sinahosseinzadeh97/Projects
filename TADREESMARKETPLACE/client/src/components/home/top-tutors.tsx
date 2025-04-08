import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowRight, Star } from "lucide-react";

export default function TopTutors() {
  const [, navigate] = useLocation();
  
  const { data: topTutors, isLoading } = useQuery({
    queryKey: ["/api/tutors/top"],
  });

  const handleViewAllClick = () => {
    navigate("/tutors");
  };

  const handleTutorClick = (id: number) => {
    navigate(`/tutor/${id}`);
  };

  return (
    <section className="py-16 bg-white">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center mb-12">
          <h2 className="font-poppins font-semibold text-3xl">Top Tutors</h2>
          <Button 
            variant="ghost" 
            className="text-primary font-medium flex items-center"
            onClick={handleViewAllClick}
          >
            View All Tutors
            <ArrowRight className="ml-1 h-4 w-4" />
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {isLoading ? (
            Array(3).fill(0).map((_, i) => (
              <Card key={i} className="overflow-hidden">
                <CardContent className="p-6">
                  <div className="flex items-start mb-4">
                    <Skeleton className="w-16 h-16 rounded-full mr-4" />
                    <div className="space-y-2">
                      <Skeleton className="h-5 w-32" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-20" />
                    </div>
                  </div>
                  <Skeleton className="h-20 w-full mb-4" />
                  <div className="flex flex-wrap gap-2 mb-4">
                    <Skeleton className="h-6 w-16 rounded-full" />
                    <Skeleton className="h-6 w-20 rounded-full" />
                    <Skeleton className="h-6 w-24 rounded-full" />
                  </div>
                  <div className="flex justify-between items-center">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-4 w-20" />
                  </div>
                </CardContent>
              </Card>
            ))
          ) : topTutors?.map((tutor) => (
            <Card 
              key={tutor.id} 
              className="overflow-hidden cursor-pointer hover:shadow-md transition-shadow duration-200"
              onClick={() => handleTutorClick(tutor.id)}
            >
              <CardContent className="p-6">
                <div className="flex items-start mb-4">
                  <div className="w-16 h-16 rounded-full overflow-hidden mr-4">
                    <img
                      src={tutor.profilePicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(tutor.name)}&background=3F51B5&color=fff`}
                      alt={tutor.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <h3 className="font-poppins font-semibold text-xl">{tutor.name}</h3>
                    <p className="text-neutral-700">{tutor.headline}</p>
                    <div className="flex items-center mt-1">
                      <div className="flex items-center text-amber-500">
                        {Array(5).fill(0).map((_, i) => (
                          <Star
                            key={i}
                            className="h-4 w-4 fill-current"
                            fill={i < Math.floor(tutor.rating) ? "currentColor" : "none"}
                          />
                        ))}
                      </div>
                      <span className="text-neutral-500 text-sm ml-1">({tutor.reviewCount} reviews)</span>
                    </div>
                  </div>
                </div>
                <p className="text-neutral-700 mb-4 line-clamp-2">{tutor.shortBio}</p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {tutor.subjects.slice(0, 3).map((subject, index) => (
                    <Badge key={index} variant="outline" className="bg-primary/10 text-primary border-none">
                      {subject}
                    </Badge>
                  ))}
                </div>
                <div className="flex justify-between items-center">
                  <div className="text-neutral-700 text-sm flex items-center">
                    <span className="material-icons text-sm align-middle">paid</span>
                    ${tutor.hourlyRate} / hour
                  </div>
                  <Button variant="link" className="text-primary p-0 h-auto">View Profile</Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
