import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/hooks/use-auth";
import { ProtectedRoute } from "@/lib/protected-route";
import { Toaster } from "@/components/ui/toaster";

import NotFound from "@/pages/not-found";
import HomePage from "@/pages/home-page";
import AuthPage from "@/pages/auth-page";
import TutorListPage from "@/pages/tutor-list-page";
import TutorProfilePage from "@/pages/tutor-profile-page";
import CheckoutPage from "@/pages/checkout-page";
import BecomeTutorPage from "@/pages/become-tutor-page";
import AccountSettingsPage from "@/pages/account-settings-page";
import MyBookingsPage from "@/pages/my-bookings-page";
import DashboardPage from "@/pages/dashboard-page";
import HowItWorksPage from "@/pages/how-it-works-page";

function Router() {
  return (
    <Switch>
      <Route path="/" component={HomePage} />
      <Route path="/auth" component={AuthPage} />
      <Route path="/tutors" component={TutorListPage} />
      <Route path="/tutor/:id" component={TutorProfilePage} />
      <Route path="/become-tutor" component={BecomeTutorPage} />
      <Route path="/how-it-works" component={HowItWorksPage} />
      <ProtectedRoute path="/dashboard" component={DashboardPage} />
      <ProtectedRoute path="/account-settings" component={AccountSettingsPage} />
      <ProtectedRoute path="/my-bookings" component={MyBookingsPage} />
      <ProtectedRoute path="/checkout/:sessionId" component={CheckoutPage} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router />
        <Toaster />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
