import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import Navbar from "@/components/layout/navbar";
import Footer from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { Loader2, Camera, User, Mail, Shield, CreditCard } from "lucide-react";

const profileSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  bio: z.string().optional(),
});

const passwordSchema = z.object({
  currentPassword: z.string().min(1, "Current password is required"),
  newPassword: z.string().min(8, "Password must be at least 8 characters"),
  confirmPassword: z.string(),
}).refine(data => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

export default function AccountSettingsPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("profile");
  const { toast } = useToast();
  
  const profileForm = useForm<z.infer<typeof profileSchema>>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: user?.name || "",
      email: user?.email || "",
      bio: user?.bio || "",
    },
  });
  
  const passwordForm = useForm<z.infer<typeof passwordSchema>>({
    resolver: zodResolver(passwordSchema),
    defaultValues: {
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    },
  });
  
  // Profile update mutation
  const updateProfileMutation = useMutation({
    mutationFn: async (data: z.infer<typeof profileSchema>) => {
      const res = await apiRequest("PATCH", "/api/user/profile", data);
      return await res.json();
    },
    onSuccess: (data) => {
      queryClient.setQueryData(["/api/user"], (oldData: any) => ({
        ...oldData,
        ...data,
      }));
      toast({
        title: "Profile updated",
        description: "Your profile information has been updated successfully.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Update failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
  
  // Password update mutation
  const updatePasswordMutation = useMutation({
    mutationFn: async (data: z.infer<typeof passwordSchema>) => {
      const res = await apiRequest("PATCH", "/api/user/password", data);
      return await res.json();
    },
    onSuccess: () => {
      passwordForm.reset({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
      toast({
        title: "Password updated",
        description: "Your password has been changed successfully.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Update failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
  
  const onProfileSubmit = (data: z.infer<typeof profileSchema>) => {
    updateProfileMutation.mutate(data);
  };
  
  const onPasswordSubmit = (data: z.infer<typeof passwordSchema>) => {
    updatePasswordMutation.mutate(data);
  };
  
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Account Settings</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
              {/* Sidebar */}
              <div className="md:col-span-3">
                <div className="bg-white rounded-lg shadow-sm p-6 space-y-1">
                  <Button
                    variant={activeTab === "profile" ? "default" : "ghost"}
                    className="w-full justify-start"
                    onClick={() => setActiveTab("profile")}
                  >
                    <User className="mr-2 h-5 w-5" />
                    Profile
                  </Button>
                  <Button
                    variant={activeTab === "security" ? "default" : "ghost"}
                    className="w-full justify-start"
                    onClick={() => setActiveTab("security")}
                  >
                    <Shield className="mr-2 h-5 w-5" />
                    Security
                  </Button>
                  <Button
                    variant={activeTab === "payment" ? "default" : "ghost"}
                    className="w-full justify-start"
                    onClick={() => setActiveTab("payment")}
                  >
                    <CreditCard className="mr-2 h-5 w-5" />
                    Payment Methods
                  </Button>
                </div>
              </div>
              
              {/* Main content */}
              <div className="md:col-span-9">
                {activeTab === "profile" && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Profile Information</CardTitle>
                      <CardDescription>
                        Update your personal information and public profile
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-8">
                        {/* Profile picture */}
                        <div className="flex flex-col items-center sm:flex-row sm:items-start gap-4">
                          <Avatar className="h-24 w-24">
                            <AvatarImage 
                              src={user?.profilePicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.name || "User")}&background=3F51B5&color=fff`} 
                              alt={user?.name || "User"} 
                            />
                            <AvatarFallback>{user?.name?.charAt(0) || "U"}</AvatarFallback>
                          </Avatar>
                          <div className="flex flex-col items-center sm:items-start gap-2">
                            <h3 className="font-medium">Profile Photo</h3>
                            <p className="text-sm text-muted-foreground">
                              Upload a clear photo of yourself to help tutors and students recognize you.
                            </p>
                            <div className="flex gap-2 mt-1">
                              <Button size="sm" className="gap-1">
                                <Camera className="h-4 w-4" />
                                Upload
                              </Button>
                              <Button size="sm" variant="outline">
                                Remove
                              </Button>
                            </div>
                          </div>
                        </div>
                        
                        <Separator />
                        
                        {/* Profile form */}
                        <Form {...profileForm}>
                          <form onSubmit={profileForm.handleSubmit(onProfileSubmit)} className="space-y-6">
                            <FormField
                              control={profileForm.control}
                              name="name"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Full Name</FormLabel>
                                  <FormControl>
                                    <Input {...field} />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            
                            <FormField
                              control={profileForm.control}
                              name="email"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Email Address</FormLabel>
                                  <FormControl>
                                    <Input {...field} />
                                  </FormControl>
                                  <FormDescription>
                                    This is the email used for login and notifications
                                  </FormDescription>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            
                            <FormField
                              control={profileForm.control}
                              name="bio"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Bio</FormLabel>
                                  <FormControl>
                                    <Textarea 
                                      {...field} 
                                      placeholder="Tell us a bit about yourself..."
                                      rows={4}
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
                              disabled={updateProfileMutation.isPending}
                            >
                              {updateProfileMutation.isPending ? (
                                <>
                                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                  Saving...
                                </>
                              ) : (
                                "Save Changes"
                              )}
                            </Button>
                          </form>
                        </Form>
                      </div>
                    </CardContent>
                  </Card>
                )}
                
                {activeTab === "security" && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Security Settings</CardTitle>
                      <CardDescription>
                        Update your password and security preferences
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Form {...passwordForm}>
                        <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)} className="space-y-6">
                          <FormField
                            control={passwordForm.control}
                            name="currentPassword"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>Current Password</FormLabel>
                                <FormControl>
                                  <Input 
                                    type="password" 
                                    {...field} 
                                  />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                          
                          <div className="grid gap-6 sm:grid-cols-2">
                            <FormField
                              control={passwordForm.control}
                              name="newPassword"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>New Password</FormLabel>
                                  <FormControl>
                                    <Input 
                                      type="password" 
                                      {...field} 
                                    />
                                  </FormControl>
                                  <FormDescription>
                                    Must be at least 8 characters
                                  </FormDescription>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            
                            <FormField
                              control={passwordForm.control}
                              name="confirmPassword"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Confirm New Password</FormLabel>
                                  <FormControl>
                                    <Input 
                                      type="password" 
                                      {...field} 
                                    />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                          </div>
                          
                          <Button
                            type="submit"
                            disabled={updatePasswordMutation.isPending}
                          >
                            {updatePasswordMutation.isPending ? (
                              <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Updating...
                              </>
                            ) : (
                              "Update Password"
                            )}
                          </Button>
                        </form>
                      </Form>
                    </CardContent>
                  </Card>
                )}
                
                {activeTab === "payment" && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Payment Methods</CardTitle>
                      <CardDescription>
                        Manage your payment methods for booking sessions
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="rounded-md border p-6 text-center">
                        <CreditCard className="mx-auto h-10 w-10 text-muted-foreground mb-3" />
                        <h3 className="text-lg font-medium mb-2">No payment methods added yet</h3>
                        <p className="text-muted-foreground mb-4">
                          Add a payment method to book tutoring sessions quickly and securely.
                        </p>
                        <Button>
                          Add Payment Method
                        </Button>
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
