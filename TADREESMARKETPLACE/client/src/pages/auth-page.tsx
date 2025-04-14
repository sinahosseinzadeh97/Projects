import { useState } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/hooks/use-auth";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { insertUserSchema } from "@shared/schema";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { BookOpen, School, Mail, Lock, Loader2, AlertCircle } from "lucide-react";

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(1, "Password is required"),
  rememberMe: z.boolean().optional(),
});

const registerSchema = insertUserSchema.extend({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters long"),
  confirmPassword: z.string(),
  role: z.enum(["student", "tutor"]),
  termsAccepted: z.boolean().refine((val) => val === true, {
    message: "You must accept the terms and conditions",
  }),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type LoginFormValues = z.infer<typeof loginSchema>;
type RegisterFormValues = z.infer<typeof registerSchema>;

export default function AuthPage() {
  const [activeTab, setActiveTab] = useState<string>("login");
  const [forgotPassword, setForgotPassword] = useState(false);
  const [, navigate] = useLocation();
  const {
    user,
    isLoading,
    loginMutation,
    registerMutation,
    resetPasswordMutation,
  } = useAuth();

  const loginForm = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
      rememberMe: false,
    },
  });

  const registerForm = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
      role: "student",
      termsAccepted: false,
    },
  });

  const forgotPasswordForm = useForm<{ email: string }>({
    resolver: zodResolver(z.object({
      email: z.string().email("Please enter a valid email address"),
    })),
    defaultValues: {
      email: "",
    },
  });

  // Redirect if user is already logged in
  if (user) {
    navigate("/");
    return null;
  }

  const onLoginSubmit = async (data: LoginFormValues) => {
    loginMutation.mutate({
      email: data.email,
      password: data.password,
    });
  };

  const onRegisterSubmit = async (data: RegisterFormValues) => {
    const { confirmPassword, termsAccepted, ...registrationData } = data;
    registerMutation.mutate(registrationData);
  };

  const onForgotPasswordSubmit = async (data: { email: string }) => {
    resetPasswordMutation.mutate({ email: data.email });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-6xl flex flex-col lg:flex-row rounded-xl overflow-hidden shadow-lg">
        {/* Left side - Auth forms */}
        <div className="w-full lg:w-1/2 bg-white p-8">
          <div className="mb-6 text-center">
            <h1 className="text-3xl font-bold text-primary font-poppins">Tadrees.com</h1>
            <p className="text-neutral-600 mt-2">Peer-to-Peer Tutoring Platform</p>
          </div>

          {forgotPassword ? (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Reset Password</CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setForgotPassword(false)}
                  >
                    Back to Login
                  </Button>
                </div>
                <CardDescription>
                  Enter your email address and we'll send you a link to reset your password.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...forgotPasswordForm}>
                  <form onSubmit={forgotPasswordForm.handleSubmit(onForgotPasswordSubmit)} className="space-y-4">
                    <FormField
                      control={forgotPasswordForm.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email Address</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="your@email.com"
                              type="email"
                              {...field}
                              disabled={resetPasswordMutation.isPending}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <Button
                      type="submit"
                      className="w-full"
                      disabled={resetPasswordMutation.isPending}
                    >
                      {resetPasswordMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Sending...
                        </>
                      ) : (
                        "Send Reset Link"
                      )}
                    </Button>
                  </form>
                </Form>
              </CardContent>
            </Card>
          ) : (
            <Tabs defaultValue="login" value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger value="login">Log In</TabsTrigger>
                <TabsTrigger value="signup">Sign Up</TabsTrigger>
              </TabsList>

              <TabsContent value="login">
                <Card>
                  <CardHeader>
                    <CardTitle>Welcome back</CardTitle>
                    <CardDescription>
                      Log in to your account to access your dashboard and book tutoring sessions.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Form {...loginForm}>
                      <form onSubmit={loginForm.handleSubmit(onLoginSubmit)} className="space-y-4">
                        <FormField
                          control={loginForm.control}
                          name="email"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Email Address</FormLabel>
                              <FormControl>
                                <div className="relative">
                                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                  <Input
                                    placeholder="your@email.com"
                                    className="pl-10"
                                    type="email"
                                    {...field}
                                    disabled={loginMutation.isPending}
                                  />
                                </div>
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={loginForm.control}
                          name="password"
                          render={({ field }) => (
                            <FormItem>
                              <div className="flex justify-between items-center">
                                <FormLabel>Password</FormLabel>
                                <Button
                                  variant="link"
                                  className="p-0 h-auto text-sm font-normal"
                                  type="button"
                                  onClick={() => setForgotPassword(true)}
                                >
                                  Forgot Password?
                                </Button>
                              </div>
                              <FormControl>
                                <div className="relative">
                                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                  <Input
                                    placeholder="••••••••"
                                    className="pl-10"
                                    type="password"
                                    {...field}
                                    disabled={loginMutation.isPending}
                                  />
                                </div>
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={loginForm.control}
                          name="rememberMe"
                          render={({ field }) => (
                            <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                              <FormControl>
                                <Checkbox
                                  checked={field.value}
                                  onCheckedChange={field.onChange}
                                  disabled={loginMutation.isPending}
                                />
                              </FormControl>
                              <div className="space-y-1 leading-none">
                                <FormLabel>Remember me for 30 days</FormLabel>
                              </div>
                            </FormItem>
                          )}
                        />
                        <Button
                          type="submit"
                          className="w-full"
                          disabled={loginMutation.isPending}
                        >
                          {loginMutation.isPending ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Logging in...
                            </>
                          ) : (
                            "Log In"
                          )}
                        </Button>
                      </form>
                    </Form>
                  </CardContent>
                  <CardFooter className="flex flex-col">
                    <Separator className="my-4" />
                    <div className="grid grid-cols-2 gap-4 w-full">
                      <Button variant="outline">
                        <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                          <path
                            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                            fill="#4285F4"
                          />
                          <path
                            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                            fill="#34A853"
                          />
                          <path
                            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                            fill="#FBBC05"
                          />
                          <path
                            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                            fill="#EA4335"
                          />
                          <path d="M1 1h22v22H1z" fill="none" />
                        </svg>
                        Google
                      </Button>
                      <Button variant="outline">
                        <svg className="w-5 h-5 mr-2 text-[#1877F2]" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M9.5 3h5v5h-5V3zm0 6h5v5h-5V9zm-6-6h5v5h-5V3zm0 6h5v5h-5V9zm0 6h5v5h-5v-5zm6 0h5v5h-5v-5zm6-12h5v5h-5V3zm0 6h5v5h-5V9zm0 6h5v5h-5v-5z" />
                        </svg>
                        Facebook
                      </Button>
                    </div>
                    <div className="mt-6 text-center">
                      <p className="text-sm text-muted-foreground">
                        Don't have an account?{" "}
                        <Button
                          variant="link"
                          className="p-0 h-auto text-sm font-normal"
                          onClick={() => setActiveTab("signup")}
                        >
                          Sign up now
                        </Button>
                      </p>
                    </div>
                  </CardFooter>
                </Card>
              </TabsContent>

              <TabsContent value="signup">
                <Card>
                  <CardHeader>
                    <CardTitle>Create an account</CardTitle>
                    <CardDescription>
                      Join Tadrees to find the perfect tutor or share your expertise with students.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Form {...registerForm}>
                      <form onSubmit={registerForm.handleSubmit(onRegisterSubmit)} className="space-y-4">
                        <FormField
                          control={registerForm.control}
                          name="name"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Full Name</FormLabel>
                              <FormControl>
                                <Input
                                  placeholder="Enter your full name"
                                  {...field}
                                  disabled={registerMutation.isPending}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={registerForm.control}
                          name="email"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Email Address</FormLabel>
                              <FormControl>
                                <div className="relative">
                                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                  <Input
                                    placeholder="your@email.com"
                                    className="pl-10"
                                    type="email"
                                    {...field}
                                    disabled={registerMutation.isPending}
                                  />
                                </div>
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <FormField
                            control={registerForm.control}
                            name="password"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>Password</FormLabel>
                                <FormControl>
                                  <div className="relative">
                                    <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                    <Input
                                      placeholder="••••••••"
                                      className="pl-10"
                                      type="password"
                                      {...field}
                                      disabled={registerMutation.isPending}
                                    />
                                  </div>
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                          <FormField
                            control={registerForm.control}
                            name="confirmPassword"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>Confirm Password</FormLabel>
                                <FormControl>
                                  <div className="relative">
                                    <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                    <Input
                                      placeholder="••••••••"
                                      className="pl-10"
                                      type="password"
                                      {...field}
                                      disabled={registerMutation.isPending}
                                    />
                                  </div>
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        </div>
                        <FormField
                          control={registerForm.control}
                          name="role"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>I want to</FormLabel>
                              <Select
                                onValueChange={field.onChange}
                                defaultValue={field.value}
                                disabled={registerMutation.isPending}
                              >
                                <FormControl>
                                  <SelectTrigger>
                                    <SelectValue placeholder="Select your role" />
                                  </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                  <SelectItem value="student">
                                    <div className="flex items-center">
                                      <BookOpen className="h-4 w-4 mr-2" />
                                      Find a tutor (I'm a student)
                                    </div>
                                  </SelectItem>
                                  <SelectItem value="tutor">
                                    <div className="flex items-center">
                                      <School className="h-4 w-4 mr-2" />
                                      Become a tutor (I'm a teacher)
                                    </div>
                                  </SelectItem>
                                </SelectContent>
                              </Select>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={registerForm.control}
                          name="termsAccepted"
                          render={({ field }) => (
                            <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                              <FormControl>
                                <Checkbox
                                  checked={field.value}
                                  onCheckedChange={field.onChange}
                                  disabled={registerMutation.isPending}
                                />
                              </FormControl>
                              <div className="space-y-1 leading-none">
                                <FormLabel>
                                  I agree to the{" "}
                                  <a href="#" className="text-primary underline">
                                    Terms of Service
                                  </a>{" "}
                                  and{" "}
                                  <a href="#" className="text-primary underline">
                                    Privacy Policy
                                  </a>
                                </FormLabel>
                                <FormMessage />
                              </div>
                            </FormItem>
                          )}
                        />
                        <Alert variant="default" className="bg-primary/10 text-primary border-primary/20">
                          <AlertCircle className="h-4 w-4" />
                          <AlertDescription>
                            Password must be at least 8 characters with a number and a special character
                          </AlertDescription>
                        </Alert>
                        <Button
                          type="submit"
                          className="w-full"
                          disabled={registerMutation.isPending}
                        >
                          {registerMutation.isPending ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Creating Account...
                            </>
                          ) : (
                            "Create Account"
                          )}
                        </Button>
                      </form>
                    </Form>
                  </CardContent>
                  <CardFooter className="flex justify-center">
                    <p className="text-sm text-muted-foreground">
                      Already have an account?{" "}
                      <Button
                        variant="link"
                        className="p-0 h-auto text-sm font-normal"
                        onClick={() => setActiveTab("login")}
                      >
                        Log in
                      </Button>
                    </p>
                  </CardFooter>
                </Card>
              </TabsContent>
            </Tabs>
          )}
        </div>

        {/* Right side - Hero section */}
        <div className="hidden lg:block w-1/2 bg-primary p-12 text-white">
          <div className="h-full flex flex-col justify-center">
            <h2 className="text-4xl font-bold font-poppins mb-6">Connect With Expert Tutors</h2>
            <p className="text-lg mb-8">
              Tadrees helps students find the perfect tutor for their learning journey. Access quality education on your schedule.
            </p>
            <div className="space-y-6">
              <div className="flex items-start">
                <div className="bg-white/10 p-2 rounded-full mr-4">
                  <School className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-medium text-lg">Expert Tutors</h3>
                  <p className="text-white/80">Connect with experienced tutors across various subjects.</p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="bg-white/10 p-2 rounded-full mr-4">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-6 w-6"
                  >
                    <rect width="18" height="18" x="3" y="4" rx="2" ry="2"></rect>
                    <line x1="16" x2="16" y1="2" y2="6"></line>
                    <line x1="8" x2="8" y1="2" y2="6"></line>
                    <line x1="3" x2="21" y1="10" y2="10"></line>
                    <path d="M8 14h.01"></path>
                    <path d="M12 14h.01"></path>
                    <path d="M16 14h.01"></path>
                    <path d="M8 18h.01"></path>
                    <path d="M12 18h.01"></path>
                    <path d="M16 18h.01"></path>
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium text-lg">Flexible Scheduling</h3>
                  <p className="text-white/80">Book sessions that fit your schedule with Calendly integration.</p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="bg-white/10 p-2 rounded-full mr-4">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-6 w-6"
                  >
                    <path d="M12 2v20"></path>
                    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium text-lg">Secure Payments</h3>
                  <p className="text-white/80">Pay securely for sessions online with our integrated payment system.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
