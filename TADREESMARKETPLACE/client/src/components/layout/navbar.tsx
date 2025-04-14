import { useState } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Menu, User, LogOut, Book, Calendar, Settings } from "lucide-react";
import { Loader2 } from "lucide-react";

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [location, navigate] = useLocation();
  const { user, logoutMutation } = useAuth();

  const handleLogout = () => {
    logoutMutation.mutate();
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  const navLinks = [
    { href: "/tutors", label: "Find Tutors" },
    { href: "/how-it-works", label: "How It Works" },
    { href: user?.role === "tutor" ? "/dashboard" : "/become-tutor", label: user?.role === "tutor" ? "Tutor Dashboard" : "Become a Tutor" },
  ];

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <a href="/" className="flex items-center" onClick={(e) => { e.preventDefault(); navigate("/"); }}>
            <span className="text-primary font-poppins font-bold text-2xl">Tadrees.com</span>
          </a>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-neutral-dark hover:text-primary font-medium"
                onClick={(e) => {
                  e.preventDefault();
                  navigate(link.href);
                }}
              >
                {link.label}
              </a>
            ))}
            
            {/* User Menu or Login/Register Buttons */}
            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center space-x-2 hover:bg-transparent">
                    <span className="text-neutral-dark font-medium">{user.name}</span>
                    <div className="w-8 h-8 rounded-full overflow-hidden">
                      <img
                        src={user.profilePicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=3F51B5&color=fff`}
                        alt="Profile"
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem onClick={() => navigate("/dashboard")}>
                    <User className="mr-2 h-4 w-4" />
                    Dashboard
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate("/my-bookings")}>
                    <Calendar className="mr-2 h-4 w-4" />
                    My Bookings
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate("/account-settings")}>
                    <Settings className="mr-2 h-4 w-4" />
                    Account Settings
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} disabled={logoutMutation.isPending}>
                    {logoutMutation.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Logging out...
                      </>
                    ) : (
                      <>
                        <LogOut className="mr-2 h-4 w-4" />
                        Log Out
                      </>
                    )}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="flex items-center space-x-4">
                <Button
                  variant="ghost"
                  className="text-primary font-medium"
                  onClick={() => navigate("/auth")}
                >
                  Log In
                </Button>
                <Button
                  className="bg-primary text-white font-medium hover:bg-primary/90"
                  onClick={() => {
                    navigate("/auth");
                    // Could pass a query param to activate the signup tab
                  }}
                >
                  Sign Up
                </Button>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Sheet open={isMenuOpen} onOpenChange={setIsMenuOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon">
                  <Menu className="h-6 w-6" />
                  <span className="sr-only">Toggle menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="right">
                <SheetHeader className="mb-6">
                  <SheetTitle className="text-left">Tadrees.com</SheetTitle>
                </SheetHeader>
                <div className="flex flex-col space-y-4">
                  {navLinks.map((link) => (
                    <a
                      key={link.href}
                      href={link.href}
                      className="text-neutral-dark hover:text-primary font-medium py-2"
                      onClick={(e) => {
                        e.preventDefault();
                        navigate(link.href);
                        closeMenu();
                      }}
                    >
                      {link.label}
                    </a>
                  ))}
                  
                  {/* User Menu or Login/Register Buttons */}
                  {user ? (
                    <>
                      <div className="py-2 flex items-center">
                        <div className="w-8 h-8 rounded-full overflow-hidden mr-3">
                          <img
                            src={user.profilePicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=3F51B5&color=fff`}
                            alt="Profile"
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <span className="font-medium">{user.name}</span>
                      </div>
                      <a
                        href="/dashboard"
                        className="text-neutral-dark hover:text-primary font-medium py-2 flex items-center"
                        onClick={(e) => {
                          e.preventDefault();
                          navigate("/dashboard");
                          closeMenu();
                        }}
                      >
                        <User className="mr-2 h-4 w-4" />
                        Dashboard
                      </a>
                      <a
                        href="/my-bookings"
                        className="text-neutral-dark hover:text-primary font-medium py-2 flex items-center"
                        onClick={(e) => {
                          e.preventDefault();
                          navigate("/my-bookings");
                          closeMenu();
                        }}
                      >
                        <Calendar className="mr-2 h-4 w-4" />
                        My Bookings
                      </a>
                      <a
                        href="/account-settings"
                        className="text-neutral-dark hover:text-primary font-medium py-2 flex items-center"
                        onClick={(e) => {
                          e.preventDefault();
                          navigate("/account-settings");
                          closeMenu();
                        }}
                      >
                        <Settings className="mr-2 h-4 w-4" />
                        Account Settings
                      </a>
                      <Button
                        variant="ghost"
                        className="text-red-500 hover:text-red-600 hover:bg-red-50 justify-start p-2 font-medium"
                        onClick={() => {
                          handleLogout();
                          closeMenu();
                        }}
                        disabled={logoutMutation.isPending}
                      >
                        {logoutMutation.isPending ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Logging out...
                          </>
                        ) : (
                          <>
                            <LogOut className="mr-2 h-4 w-4" />
                            Log Out
                          </>
                        )}
                      </Button>
                    </>
                  ) : (
                    <div className="flex flex-col space-y-2 pt-2">
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => {
                          navigate("/auth");
                          closeMenu();
                        }}
                      >
                        Log In
                      </Button>
                      <Button
                        className="w-full"
                        onClick={() => {
                          navigate("/auth");
                          closeMenu();
                        }}
                      >
                        Sign Up
                      </Button>
                    </div>
                  )}
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </nav>
  );
}
