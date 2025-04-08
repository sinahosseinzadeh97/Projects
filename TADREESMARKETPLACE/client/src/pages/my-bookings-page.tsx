import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { useLocation } from "wouter";
import Navbar from "@/components/layout/navbar";
import Footer from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Loader2, Calendar, Clock, MessageSquare, Star } from "lucide-react";

export default function MyBookingsPage() {
  const { user } = useAuth();
  const [, navigate] = useLocation();
  const [activeTab, setActiveTab] = useState("upcoming");
  
  // Fetch bookings
  const { data: bookings, isLoading, error } = useQuery({
    queryKey: ["/api/bookings"],
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
  
  // Group bookings by status
  const upcomingBookings = bookings?.filter(booking => 
    booking.status === "confirmed" && new Date(booking.date) > new Date()
  ) || [];
  
  const pastBookings = bookings?.filter(booking => 
    booking.status === "completed" || new Date(booking.date) < new Date()
  ) || [];
  
  const cancelledBookings = bookings?.filter(booking => 
    booking.status === "cancelled"
  ) || [];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "confirmed":
        return <Badge className="bg-green-500">Confirmed</Badge>;
      case "pending":
        return <Badge variant="outline" className="bg-yellow-100 text-yellow-800 border-yellow-300">Pending</Badge>;
      case "cancelled":
        return <Badge variant="outline" className="bg-red-100 text-red-800 border-red-300">Cancelled</Badge>;
      case "completed":
        return <Badge variant="outline" className="bg-blue-100 text-blue-800 border-blue-300">Completed</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleViewTutor = (tutorId: number) => {
    navigate(`/tutor/${tutorId}`);
  };

  const handleLeaveReview = (bookingId: number, tutorId: number) => {
    // In a real app, navigate to a review form or show a modal
    navigate(`/tutor/${tutorId}?review=true`);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="max-w-5xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">My Bookings</h1>
            
            <Tabs defaultValue="upcoming" value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-3 mb-8">
                <TabsTrigger value="upcoming" className="text-base">
                  Upcoming ({upcomingBookings.length})
                </TabsTrigger>
                <TabsTrigger value="past" className="text-base">
                  Past ({pastBookings.length})
                </TabsTrigger>
                <TabsTrigger value="cancelled" className="text-base">
                  Cancelled ({cancelledBookings.length})
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="upcoming">
                {upcomingBookings.length === 0 ? (
                  <Card>
                    <CardContent className="py-12 text-center">
                      <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                      <h3 className="text-xl font-medium mb-2">No upcoming bookings</h3>
                      <p className="text-muted-foreground mb-6">You don't have any upcoming tutoring sessions scheduled.</p>
                      <Button onClick={() => navigate("/tutors")}>Find a Tutor</Button>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-6">
                    {upcomingBookings.map((booking) => (
                      <Card key={booking.id} className="overflow-hidden">
                        <CardContent className="p-0">
                          <div className="p-6">
                            <div className="flex flex-col md:flex-row justify-between">
                              <div className="md:w-3/4">
                                <div className="flex items-center justify-between mb-4">
                                  <div className="flex items-center">
                                    <div className="w-12 h-12 rounded-full overflow-hidden mr-4">
                                      <img
                                        src={booking.tutor.user.profilePicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(booking.tutor.user.name)}&background=3F51B5&color=fff`}
                                        alt={booking.tutor.user.name}
                                        className="w-full h-full object-cover"
                                      />
                                    </div>
                                    <div>
                                      <h3 className="font-medium text-lg">{booking.tutor.user.name}</h3>
                                      <p className="text-gray-600">{booking.subject}</p>
                                    </div>
                                  </div>
                                  <div className="hidden md:block">
                                    {getStatusBadge(booking.status)}
                                  </div>
                                </div>
                                
                                <div className="mb-4 md:hidden">
                                  {getStatusBadge(booking.status)}
                                </div>
                                
                                <div className="space-y-3">
                                  <div className="flex items-center text-gray-600">
                                    <Calendar className="h-5 w-5 mr-2 text-primary" />
                                    <span>{formatDate(booking.date)}</span>
                                  </div>
                                  <div className="flex items-center text-gray-600">
                                    <Clock className="h-5 w-5 mr-2 text-primary" />
                                    <span>{formatTime(booking.date)} ({booking.duration} minutes)</span>
                                  </div>
                                </div>
                              </div>
                              
                              <div className="md:w-1/4 flex flex-col justify-center items-center mt-6 md:mt-0 space-y-3">
                                <Button 
                                  variant="outline" 
                                  className="w-full"
                                  onClick={() => handleViewTutor(booking.tutor.id)}
                                >
                                  View Tutor
                                </Button>
                                <Button 
                                  variant="outline" 
                                  className="w-full"
                                >
                                  <MessageSquare className="h-4 w-4 mr-2" />
                                  Message
                                </Button>
                                <Button 
                                  variant="outline" 
                                  className="w-full text-red-500 hover:text-red-700 hover:bg-red-50"
                                >
                                  Cancel
                                </Button>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="past">
                {pastBookings.length === 0 ? (
                  <Card>
                    <CardContent className="py-12 text-center">
                      <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                      <h3 className="text-xl font-medium mb-2">No past bookings</h3>
                      <p className="text-muted-foreground mb-6">You don't have any completed tutoring sessions yet.</p>
                      <Button onClick={() => navigate("/tutors")}>Find a Tutor</Button>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-6">
                    {pastBookings.map((booking) => (
                      <Card key={booking.id} className="overflow-hidden">
                        <CardContent className="p-0">
                          <div className="p-6">
                            <div className="flex flex-col md:flex-row justify-between">
                              <div className="md:w-3/4">
                                <div className="flex items-center justify-between mb-4">
                                  <div className="flex items-center">
                                    <div className="w-12 h-12 rounded-full overflow-hidden mr-4">
                                      <img
                                        src={booking.tutor.user.profilePicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(booking.tutor.user.name)}&background=3F51B5&color=fff`}
                                        alt={booking.tutor.user.name}
                                        className="w-full h-full object-cover"
                                      />
                                    </div>
                                    <div>
                                      <h3 className="font-medium text-lg">{booking.tutor.user.name}</h3>
                                      <p className="text-gray-600">{booking.subject}</p>
                                    </div>
                                  </div>
                                  <div className="hidden md:block">
                                    {getStatusBadge(booking.status === "completed" ? "completed" : "completed")}
                                  </div>
                                </div>
                                
                                <div className="mb-4 md:hidden">
                                  {getStatusBadge(booking.status === "completed" ? "completed" : "completed")}
                                </div>
                                
                                <div className="space-y-3">
                                  <div className="flex items-center text-gray-600">
                                    <Calendar className="h-5 w-5 mr-2 text-primary" />
                                    <span>{formatDate(booking.date)}</span>
                                  </div>
                                  <div className="flex items-center text-gray-600">
                                    <Clock className="h-5 w-5 mr-2 text-primary" />
                                    <span>{formatTime(booking.date)} ({booking.duration} minutes)</span>
                                  </div>
                                </div>
                              </div>
                              
                              <div className="md:w-1/4 flex flex-col justify-center items-center mt-6 md:mt-0 space-y-3">
                                <Button 
                                  variant="outline" 
                                  className="w-full"
                                  onClick={() => handleViewTutor(booking.tutor.id)}
                                >
                                  View Tutor
                                </Button>
                                <Button 
                                  className="w-full"
                                  onClick={() => handleLeaveReview(booking.id, booking.tutor.id)}
                                >
                                  <Star className="h-4 w-4 mr-2" />
                                  Leave Review
                                </Button>
                                <Button 
                                  variant="outline" 
                                  className="w-full"
                                >
                                  Book Again
                                </Button>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="cancelled">
                {cancelledBookings.length === 0 ? (
                  <Card>
                    <CardContent className="py-12 text-center">
                      <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                      <h3 className="text-xl font-medium mb-2">No cancelled bookings</h3>
                      <p className="text-muted-foreground mb-6">You don't have any cancelled tutoring sessions.</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-6">
                    {cancelledBookings.map((booking) => (
                      <Card key={booking.id} className="overflow-hidden">
                        <CardContent className="p-0">
                          <div className="p-6">
                            <div className="flex flex-col md:flex-row justify-between">
                              <div className="md:w-3/4">
                                <div className="flex items-center justify-between mb-4">
                                  <div className="flex items-center">
                                    <div className="w-12 h-12 rounded-full overflow-hidden mr-4">
                                      <img
                                        src={booking.tutor.user.profilePicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(booking.tutor.user.name)}&background=3F51B5&color=fff`}
                                        alt={booking.tutor.user.name}
                                        className="w-full h-full object-cover"
                                      />
                                    </div>
                                    <div>
                                      <h3 className="font-medium text-lg">{booking.tutor.user.name}</h3>
                                      <p className="text-gray-600">{booking.subject}</p>
                                    </div>
                                  </div>
                                  <div className="hidden md:block">
                                    {getStatusBadge("cancelled")}
                                  </div>
                                </div>
                                
                                <div className="mb-4 md:hidden">
                                  {getStatusBadge("cancelled")}
                                </div>
                                
                                <div className="space-y-3">
                                  <div className="flex items-center text-gray-600">
                                    <Calendar className="h-5 w-5 mr-2 text-primary" />
                                    <span>{formatDate(booking.date)}</span>
                                  </div>
                                  <div className="flex items-center text-gray-600">
                                    <Clock className="h-5 w-5 mr-2 text-primary" />
                                    <span>{formatTime(booking.date)} ({booking.duration} minutes)</span>
                                  </div>
                                </div>
                              </div>
                              
                              <div className="md:w-1/4 flex flex-col justify-center items-center mt-6 md:mt-0 space-y-3">
                                <Button 
                                  variant="outline" 
                                  className="w-full"
                                  onClick={() => handleViewTutor(booking.tutor.id)}
                                >
                                  View Tutor
                                </Button>
                                <Button 
                                  className="w-full"
                                >
                                  Book Again
                                </Button>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
