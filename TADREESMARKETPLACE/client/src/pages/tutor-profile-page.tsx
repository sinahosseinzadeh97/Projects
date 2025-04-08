import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams, useLocation } from "wouter";
import Navbar from "@/components/layout/navbar";
import Footer from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { ChevronLeft, Star, Clock, DollarSign, Calendar, MessageSquare, School, Award, User } from "lucide-react";
import { Loader2 } from "lucide-react";

export default function TutorProfilePage() {
  const params = useParams();
  const tutorId = params.id;
  const [, navigate] = useLocation();
  const [activeTab, setActiveTab] = useState("about");

  // Get tutor details
  const { data: tutor, isLoading, error } = useQuery({
    queryKey: [`/api/tutors/${tutorId}`],
  });

  // Get similar tutors
  const { data: similarTutors } = useQuery({
    queryKey: ["/api/tutors/similar", tutorId],
  });

  if (isLoading) {
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

  if (error || !tutor) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Tutor not found</h2>
            <p className="text-gray-600 mb-6">The tutor you're looking for doesn't exist or may have been removed.</p>
            <Button onClick={() => navigate("/tutors")}>Browse Tutors</Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const handleBookSession = (calendlyUrl: string) => {
    window.open(calendlyUrl, "_blank");
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          {/* Back button */}
          <Button
            variant="ghost"
            className="mb-6 flex items-center text-primary"
            onClick={() => navigate("/tutors")}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Back to Tutors
          </Button>

          {/* Tutor profile card */}
          <Card className="mb-8 overflow-hidden">
            <CardContent className="p-0">
              <div className="p-8">
                <div className="flex flex-col md:flex-row">
                  {/* Tutor profile header */}
                  <div className="md:w-1/4 flex flex-col items-center text-center mb-6 md:mb-0">
                    <div className="w-32 h-32 rounded-full overflow-hidden mb-4">
                      <img
                        src={tutor.profilePicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(tutor.name)}&background=3F51B5&color=fff`}
                        alt={tutor.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <h2 className="font-poppins font-semibold text-2xl mb-2">{tutor.name}</h2>
                    <p className="text-neutral-dark text-lg mb-2">{tutor.headline}</p>
                    
                    <div className="flex items-center justify-center mb-3">
                      <div className="flex items-center text-amber-500">
                        {Array(5).fill(0).map((_, i) => (
                          <Star
                            key={i}
                            className="h-4 w-4 fill-current"
                            fill={i < Math.floor(tutor.rating) ? "currentColor" : "none"}
                          />
                        ))}
                      </div>
                      <span className="text-neutral-medium text-sm ml-1">({tutor.reviewCount} reviews)</span>
                    </div>
                    
                    <p className="text-neutral-dark text-lg font-medium mb-4 flex items-center justify-center">
                      <DollarSign className="h-5 w-5 mr-1" />
                      ${tutor.hourlyRate} / hour
                    </p>
                    
                    <div className="flex flex-col w-full space-y-3">
                      <Button 
                        className="bg-[#FF9800] hover:bg-[#F57C00] text-white w-full flex items-center justify-center"
                        onClick={() => handleBookSession(tutor.calendlyUrl)}
                      >
                        <Calendar className="mr-2 h-5 w-5" />
                        Book a Session
                      </Button>
                      <Button variant="outline" className="w-full flex items-center justify-center">
                        <MessageSquare className="mr-2 h-5 w-5" />
                        Message
                      </Button>
                    </div>
                  </div>
                  
                  {/* Tutor details */}
                  <div className="md:w-3/4 md:pl-8">
                    <Tabs defaultValue="about" value={activeTab} onValueChange={setActiveTab} className="w-full">
                      <TabsList className="w-full justify-start border-b mb-6 bg-transparent">
                        <TabsTrigger value="about" className="rounded-none data-[state=active]:border-b-2 data-[state=active]:border-primary">About</TabsTrigger>
                        <TabsTrigger value="experience" className="rounded-none data-[state=active]:border-b-2 data-[state=active]:border-primary">Experience & Education</TabsTrigger>
                        <TabsTrigger value="reviews" className="rounded-none data-[state=active]:border-b-2 data-[state=active]:border-primary">Reviews ({tutor.reviewCount})</TabsTrigger>
                      </TabsList>
                      
                      <TabsContent value="about" className="mt-0">
                        <div className="mb-6">
                          <h3 className="font-poppins font-semibold text-xl mb-4">About Me</h3>
                          <p className="text-neutral-dark mb-4">{tutor.bio}</p>
                        </div>
                        
                        <div className="mb-6">
                          <h3 className="font-poppins font-semibold text-xl mb-4">Subjects & Expertise</h3>
                          <div className="flex flex-wrap gap-2 mb-4">
                            {tutor.subjects.map((subject, index) => (
                              <Badge key={index} variant="outline" className="bg-primary/10 text-primary border-none py-1 px-3 rounded-full">
                                {subject}
                              </Badge>
                            ))}
                          </div>
                          {tutor.experienceLevels && (
                            <div className="mt-4">
                              <h4 className="font-medium mb-2">Experience Level:</h4>
                              <ul className="list-disc list-inside text-neutral-dark space-y-1 ml-2">
                                {tutor.experienceLevels.map((level, index) => (
                                  <li key={index}>{level}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                        
                        <div>
                          <h3 className="font-poppins font-semibold text-xl mb-4">Availability</h3>
                          <div className="flex flex-wrap gap-4 mb-2">
                            {tutor.availability.map((slot, index) => (
                              <div key={index} className="bg-neutral-100 p-3 rounded-md">
                                <p className="font-medium">{slot.day}</p>
                                <p className="text-neutral-dark">{slot.time}</p>
                              </div>
                            ))}
                          </div>
                          <p className="text-neutral-medium text-sm mt-2">* Available times are shown in your local timezone. Book a session to see exact availability.</p>
                        </div>
                      </TabsContent>
                      
                      <TabsContent value="experience" className="mt-0">
                        <div className="mb-6">
                          <h3 className="font-poppins font-semibold text-xl mb-4">Education & Qualifications</h3>
                          <ul className="space-y-4">
                            {tutor.education.map((edu, index) => (
                              <li key={index} className="flex items-start">
                                <div className="text-primary mr-3 mt-1">
                                  <School className="h-5 w-5" />
                                </div>
                                <div>
                                  <p className="font-medium">{edu.degree}</p>
                                  <p className="text-neutral-dark">{edu.institution}, {edu.year}</p>
                                </div>
                              </li>
                            ))}
                            {tutor.certifications.map((cert, index) => (
                              <li key={index} className="flex items-start">
                                <div className="text-primary mr-3 mt-1">
                                  <Award className="h-5 w-5" />
                                </div>
                                <div>
                                  <p className="font-medium">{cert.name}</p>
                                  <p className="text-neutral-dark">{cert.issuer}, {cert.year}</p>
                                </div>
                              </li>
                            ))}
                          </ul>
                        </div>
                        
                        <div>
                          <h3 className="font-poppins font-semibold text-xl mb-4">Professional Experience</h3>
                          <ul className="space-y-4">
                            {tutor.experience.map((exp, index) => (
                              <li key={index} className="flex items-start">
                                <div className="text-primary mr-3 mt-1">
                                  <User className="h-5 w-5" />
                                </div>
                                <div>
                                  <p className="font-medium">{exp.position}</p>
                                  <p className="text-neutral-dark">{exp.company}, {exp.period}</p>
                                  {exp.description && <p className="text-neutral-dark mt-1">{exp.description}</p>}
                                </div>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </TabsContent>
                      
                      <TabsContent value="reviews" className="mt-0">
                        <div className="flex justify-between items-center mb-6">
                          <h3 className="font-poppins font-semibold text-xl">Reviews ({tutor.reviewCount})</h3>
                          <div className="flex items-center">
                            <div className="text-amber-500 flex items-center mr-2">
                              {Array(5).fill(0).map((_, i) => (
                                <Star
                                  key={i}
                                  className="h-4 w-4 fill-current"
                                  fill={i < Math.floor(tutor.rating) ? "currentColor" : "none"}
                                />
                              ))}
                            </div>
                            <span className="font-medium">{tutor.rating} out of 5</span>
                          </div>
                        </div>
                        
                        <div className="space-y-6">
                          {tutor.reviews.map((review, index) => (
                            <div key={index} className="border-b border-neutral-200 pb-6 last:border-0 last:pb-0">
                              <div className="flex justify-between mb-2">
                                <div className="flex items-center">
                                  <div className="w-10 h-10 rounded-full overflow-hidden mr-3">
                                    <img 
                                      src={review.userPicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(review.userName)}&background=E0E0E0&color=333`} 
                                      alt={review.userName} 
                                      className="w-full h-full object-cover"
                                    />
                                  </div>
                                  <div>
                                    <p className="font-medium">{review.userName}</p>
                                    <p className="text-neutral-medium text-sm">{review.date}</p>
                                  </div>
                                </div>
                                <div className="text-amber-500 flex items-center">
                                  {Array(5).fill(0).map((_, i) => (
                                    <Star
                                      key={i}
                                      className="h-4 w-4 fill-current"
                                      fill={i < review.rating ? "currentColor" : "none"}
                                    />
                                  ))}
                                </div>
                              </div>
                              <p className="text-neutral-dark">{review.comment}</p>
                            </div>
                          ))}
                          
                          {tutor.reviewCount > 3 && (
                            <Button variant="link" className="w-full">
                              View All Reviews
                            </Button>
                          )}
                        </div>
                      </TabsContent>
                    </Tabs>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Similar Tutors */}
          {similarTutors && similarTutors.length > 0 && (
            <div>
              <h3 className="font-poppins font-semibold text-xl mb-6">Similar Tutors You Might Like</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {similarTutors.map((tutor) => (
                  <Card 
                    key={tutor.id} 
                    className="cursor-pointer hover:shadow-md transition-shadow duration-200"
                    onClick={() => navigate(`/tutor/${tutor.id}`)}
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
                          <p className="text-neutral-dark">{tutor.headline}</p>
                          <div className="flex items-center mt-1">
                            <div className="flex items-center text-amber-500">
                              {Array(5).fill(0).map((_, i) => (
                                <Star
                                  key={i}
                                  className="h-3 w-3 fill-current"
                                  fill={i < Math.floor(tutor.rating) ? "currentColor" : "none"}
                                />
                              ))}
                            </div>
                            <span className="text-neutral-medium text-sm ml-1">({tutor.reviewCount})</span>
                          </div>
                        </div>
                      </div>
                      <p className="text-neutral-dark mb-4 line-clamp-2">{tutor.shortBio}</p>
                      <div className="flex flex-wrap gap-2 mb-4">
                        {tutor.subjects.slice(0, 3).map((subject, index) => (
                          <Badge key={index} variant="outline" className="bg-primary/10 text-primary border-none py-1 px-3 rounded-full">
                            {subject}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex justify-between items-center">
                        <div className="text-neutral-dark text-sm flex items-center">
                          <DollarSign className="h-4 w-4 mr-1" />
                          ${tutor.hourlyRate} / hour
                        </div>
                        <Button variant="link" className="text-primary p-0 h-auto">View Profile</Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}
