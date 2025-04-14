import { useAuth } from "@/hooks/use-auth";
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { useLocation } from "wouter";
import React from "react";
import { Loader2 } from "lucide-react";

import Navbar from "@/components/layout/navbar";
import Footer from "@/components/layout/footer";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Calendar, Users, BookOpen, BookCheck, Clock, CreditCard } from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();
  const [, navigate] = useLocation();
  
  // Redirect if not logged in
  if (!user) {
    // Instead of returning null, use useEffect for navigation
    // and return a loading element
    React.useEffect(() => {
      navigate("/auth");
    }, [navigate]);
    
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }
  
  // Fetch bookings for the user
  const { data: bookings = [] } = useQuery({
    queryKey: ["/api/bookings"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/bookings");
      return res.json();
    },
    enabled: !!user,
  });
  
  const upcomingBookings = bookings.filter((booking: any) => 
    booking.status !== "cancelled" && booking.status !== "completed" && new Date(booking.date) > new Date()
  ).slice(0, 3);
  
  const pastBookings = bookings.filter((booking: any) => 
    booking.status === "completed" || new Date(booking.date) < new Date()
  ).slice(0, 3);
  
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              {user.role === "student" && (
                <Button onClick={() => navigate("/tutors")}>
                  Find Tutors
                </Button>
              )}
              {user.role === "tutor" && (
                <Button onClick={() => navigate("/account-settings")}>
                  Manage Profile
                </Button>
              )}
            </div>
            
            {/* Welcome Card */}
            <Card className="mb-8">
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <Avatar className="h-16 w-16">
                    <AvatarImage 
                      src={user.profilePicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=3F51B5&color=fff`} 
                      alt={user.name} 
                    />
                    <AvatarFallback>{user.name.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <div>
                    <h2 className="text-2xl font-semibold">Welcome back, {user.name}!</h2>
                    <p className="text-gray-500">
                      {user.role === "student" 
                        ? "Continue your learning journey with top tutors" 
                        : "Manage your tutoring sessions and connect with students"}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            {/* Dashboard Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Main Content */}
              <div className="lg:col-span-2 space-y-8">
                <Card>
                  <CardHeader>
                    <CardTitle>Upcoming Sessions</CardTitle>
                    <CardDescription>
                      Your scheduled tutoring sessions
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {upcomingBookings.length > 0 ? (
                      <div className="space-y-4">
                        {upcomingBookings.map((booking: any) => (
                          <div key={booking.id} className="flex items-start p-4 border rounded-lg">
                            <div className="mr-4 mt-1">
                              <Calendar className="h-10 w-10 text-primary" />
                            </div>
                            <div className="flex-1">
                              <div className="flex justify-between items-start">
                                <div>
                                  <h4 className="font-medium">
                                    {user.role === "student" ? booking.tutor.user.name : `Session with ${booking.student?.name || "Student"}`}
                                  </h4>
                                  <p className="text-sm text-gray-500">{booking.subject}</p>
                                </div>
                                <div className="text-right">
                                  <p className="font-medium">{new Date(booking.date).toLocaleDateString()}</p>
                                  <p className="text-sm text-gray-500">
                                    {new Date(booking.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                  </p>
                                </div>
                              </div>
                              <div className="mt-2 flex justify-between">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                  {booking.status}
                                </span>
                                <Button variant="outline" size="sm" onClick={() => navigate(`/bookings/${booking.id}`)}>
                                  View Details
                                </Button>
                              </div>
                            </div>
                          </div>
                        ))}
                        
                        <div className="text-center mt-4">
                          <Button variant="link" onClick={() => navigate("/my-bookings")}>
                            View All Sessions
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <Clock className="mx-auto h-12 w-12 text-gray-400 mb-3" />
                        <h3 className="text-lg font-medium text-gray-900 mb-1">No upcoming sessions</h3>
                        <p className="text-gray-500 mb-4">
                          {user.role === "student" 
                            ? "Book a session with a tutor to get started" 
                            : "You don't have any upcoming sessions scheduled"}
                        </p>
                        {user.role === "student" && (
                          <Button onClick={() => navigate("/tutors")}>
                            Find a Tutor
                          </Button>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader>
                    <CardTitle>Past Sessions</CardTitle>
                    <CardDescription>
                      Your completed tutoring sessions
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {pastBookings.length > 0 ? (
                      <div className="space-y-4">
                        {pastBookings.map((booking: any) => (
                          <div key={booking.id} className="flex items-start p-4 border rounded-lg">
                            <div className="mr-4 mt-1">
                              <BookCheck className="h-10 w-10 text-green-500" />
                            </div>
                            <div className="flex-1">
                              <div className="flex justify-between items-start">
                                <div>
                                  <h4 className="font-medium">
                                    {user.role === "student" ? booking.tutor.user.name : `Session with ${booking.student?.name || "Student"}`}
                                  </h4>
                                  <p className="text-sm text-gray-500">{booking.subject}</p>
                                </div>
                                <div className="text-right">
                                  <p className="font-medium">{new Date(booking.date).toLocaleDateString()}</p>
                                  <p className="text-sm text-gray-500">
                                    {new Date(booking.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                  </p>
                                </div>
                              </div>
                              {booking.status === "completed" && user.role === "student" && !booking.reviewSubmitted && (
                                <div className="mt-2 flex justify-end">
                                  <Button variant="outline" size="sm" onClick={() => navigate(`/review/${booking.id}`)}>
                                    Leave Review
                                  </Button>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                        
                        <div className="text-center mt-4">
                          <Button variant="link" onClick={() => navigate("/my-bookings")}>
                            View All Sessions
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <BookOpen className="mx-auto h-12 w-12 text-gray-400 mb-3" />
                        <h3 className="text-lg font-medium text-gray-900 mb-1">No past sessions</h3>
                        <p className="text-gray-500">Your completed sessions will appear here</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
              
              {/* Sidebar */}
              <div className="space-y-8">
                <Card>
                  <CardHeader>
                    <CardTitle>Quick Links</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Button variant="outline" className="w-full justify-start" onClick={() => navigate("/my-bookings")}>
                      <Calendar className="mr-2 h-5 w-5" />
                      My Bookings
                    </Button>
                    <Button variant="outline" className="w-full justify-start" onClick={() => navigate("/account-settings")}>
                      <Users className="mr-2 h-5 w-5" />
                      Account Settings
                    </Button>
                    {user.role === "student" && (
                      <Button variant="outline" className="w-full justify-start" onClick={() => navigate("/tutors")}>
                        <BookOpen className="mr-2 h-5 w-5" />
                        Find Tutors
                      </Button>
                    )}
                    {user.role === "tutor" && (
                      <Button variant="outline" className="w-full justify-start" onClick={() => navigate("/account-settings?tab=payment")}>
                        <CreditCard className="mr-2 h-5 w-5" />
                        Payment Settings
                      </Button>
                    )}
                  </CardContent>
                </Card>
                
                {/* Stats Card - only show for tutors */}
                {user.role === "tutor" && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Tutoring Stats</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                          <h4 className="text-2xl font-bold text-blue-600">
                            {bookings.filter((b: any) => b.status === "completed").length}
                          </h4>
                          <p className="text-sm text-gray-500">Completed Sessions</p>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-lg">
                          <h4 className="text-2xl font-bold text-green-600">
                            {upcomingBookings.length}
                          </h4>
                          <p className="text-sm text-gray-500">Upcoming Sessions</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
} 