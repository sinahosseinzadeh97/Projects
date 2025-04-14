import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useLocation } from "wouter";

import Navbar from "@/components/layout/navbar";
import Footer from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2 } from "lucide-react";

const tutorSchema = z.object({
  expertise: z.string().min(1, "Please select your area of expertise"),
  experience: z.string().min(1, "Years of experience is required"),
  education: z.string().min(3, "Education information is required"),
  hourlyRate: z.string().min(1, "Hourly rate is required"),
  bio: z.string().min(30, "Bio must be at least 30 characters").max(500, "Bio must not exceed 500 characters"),
});

export default function BecomeTutorPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [, navigate] = useLocation();
  
  // Redirect if not logged in
  if (!user) {
    useEffect(() => {
      navigate("/auth?redirect=/become-tutor");
    }, [navigate]);
    
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }
  
  // Redirect if already a tutor
  if (user.role === "tutor") {
    useEffect(() => {
      navigate("/account-settings");
    }, [navigate]);
    
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }
  
  const form = useForm<z.infer<typeof tutorSchema>>({
    resolver: zodResolver(tutorSchema),
    defaultValues: {
      expertise: "",
      experience: "",
      education: "",
      hourlyRate: "",
      bio: "",
    },
  });
  
  const becomeTutorMutation = useMutation({
    mutationFn: async (data: z.infer<typeof tutorSchema>) => {
      const res = await apiRequest("POST", "/api/user/become-tutor", data);
      return await res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/user"] });
      toast({
        title: "Application submitted!",
        description: "Your tutor application has been submitted successfully.",
      });
      setTimeout(() => navigate("/account-settings"), 1500);
    },
    onError: (error: Error) => {
      toast({
        title: "Submission failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
  
  const onSubmit = (data: z.infer<typeof tutorSchema>) => {
    becomeTutorMutation.mutate(data);
  };
  
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Become a Tutor</h1>
            <p className="text-gray-600 mb-8">
              Share your knowledge and earn by becoming a tutor on our platform. Fill out the form below to get started.
            </p>
            
            <Card>
              <CardHeader>
                <CardTitle>Tutor Application</CardTitle>
                <CardDescription>
                  Provide information about your expertise and experience
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                    <FormField
                      control={form.control}
                      name="expertise"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Area of Expertise</FormLabel>
                          <Select 
                            onValueChange={field.onChange} 
                            value={field.value || undefined}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select your primary subject" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="mathematics">Mathematics</SelectItem>
                              <SelectItem value="english">English</SelectItem>
                              <SelectItem value="science">Science</SelectItem>
                              <SelectItem value="history">History</SelectItem>
                              <SelectItem value="computer-science">Computer Science</SelectItem>
                              <SelectItem value="foreign-language">Foreign Language</SelectItem>
                              <SelectItem value="arts">Arts</SelectItem>
                              <SelectItem value="music">Music</SelectItem>
                              <SelectItem value="other">Other</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="experience"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Years of Experience</FormLabel>
                          <FormControl>
                            <Input 
                              type="number" 
                              min="0"
                              {...field} 
                            />
                          </FormControl>
                          <FormDescription>
                            How many years have you been teaching or practicing in this field?
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="education"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Education</FormLabel>
                          <FormControl>
                            <Input 
                              {...field} 
                              placeholder="e.g., B.Sc. Computer Science, Stanford University"
                            />
                          </FormControl>
                          <FormDescription>
                            Your highest education qualification relevant to your teaching area
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="hourlyRate"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Hourly Rate ($)</FormLabel>
                          <FormControl>
                            <Input 
                              type="number"
                              min="5" 
                              {...field} 
                            />
                          </FormControl>
                          <FormDescription>
                            How much you charge per hour of tutoring
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="bio"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Bio</FormLabel>
                          <FormControl>
                            <Textarea 
                              {...field} 
                              placeholder="Tell students about yourself, your teaching style, and what they can expect..."
                              rows={5}
                            />
                          </FormControl>
                          <FormDescription>
                            {field.value?.length || 0}/500 characters
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <Button
                      type="submit"
                      className="w-full"
                      disabled={becomeTutorMutation.isPending}
                    >
                      {becomeTutorMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Submitting...
                        </>
                      ) : (
                        "Submit Application"
                      )}
                    </Button>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
} 