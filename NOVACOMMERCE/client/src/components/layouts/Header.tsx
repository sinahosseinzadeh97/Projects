import { useState, useEffect } from 'react';
import { Link, useRoute, useLocation } from 'wouter';
import { useAuth } from '@/lib/auth';
import { useCart } from '@/lib/cartStore';
import { useQuery } from '@tanstack/react-query';
import { 
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetClose,
} from "@/components/ui/sheet";
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const Header = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();
  const { getCartItemsCount } = useCart();
  const [isHomeRoute] = useRoute('/');
  const [, navigate] = useLocation();
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch categories for navigation
  const { data: categories } = useQuery({
    queryKey: ['/api/categories'],
  });

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Handle search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/products?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!user) return 'U';
    if (user.firstName && user.lastName) {
      return `${user.firstName[0]}${user.lastName[0]}`;
    }
    return user.username.substring(0, 2).toUpperCase();
  };

  return (
    <header className={`bg-white sticky top-0 z-50 ${isScrolled ? 'shadow-md' : 'shadow-sm'}`}>
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-4">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="text-2xl font-bold text-primary-600">
              Nova<span className="text-gray-800">Cart</span>
            </Link>
          </div>

          {/* Search - Hidden on mobile, visible on larger screens */}
          <div className="hidden md:flex w-full max-w-md mx-4">
            <form onSubmit={handleSearch} className="relative w-full">
              <input 
                type="text" 
                placeholder="Search products..." 
                className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button 
                type="submit"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-primary-600"
              >
                <i className="fas fa-search"></i>
              </button>
            </form>
          </div>

          {/* Navigation Icons */}
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="text-gray-600 hover:text-primary-600">
                    <Avatar className="h-8 w-8 bg-primary-100 text-primary-700">
                      <AvatarFallback>{getUserInitials()}</AvatarFallback>
                    </Avatar>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem>
                    <Link href="/account">My Account</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Link href="/account?tab=orders">My Orders</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Link href="/account?tab=wishlist">My Wishlist</Link>
                  </DropdownMenuItem>
                  {user?.isAdmin && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem>
                        <Link href="/admin">Admin Dashboard</Link>
                      </DropdownMenuItem>
                    </>
                  )}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={logout}>
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Link href="/login" className="text-gray-600 hover:text-primary-600">
                <i className="fas fa-user"></i>
              </Link>
            )}
            
            <Link href="/account?tab=wishlist" className="text-gray-600 hover:text-primary-600">
              <i className="fas fa-heart"></i>
            </Link>
            
            <Link href="/cart" className="text-gray-600 hover:text-primary-600 relative">
              <i className="fas fa-shopping-cart"></i>
              {getCartItemsCount() > 0 && (
                <span className="absolute -top-2 -right-2 bg-primary-600 text-white text-xs w-5 h-5 flex items-center justify-center rounded-full">
                  {getCartItemsCount()}
                </span>
              )}
            </Link>
            
            <Sheet>
              <SheetTrigger asChild>
                <button className="md:hidden text-gray-600 hover:text-primary-600">
                  <i className="fas fa-bars"></i>
                </button>
              </SheetTrigger>
              <SheetContent side="left">
                <div className="py-4">
                  <form onSubmit={handleSearch} className="mb-6">
                    <div className="relative w-full">
                      <input 
                        type="text" 
                        placeholder="Search products..." 
                        className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                      <button 
                        type="submit"
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-primary-600"
                      >
                        <i className="fas fa-search"></i>
                      </button>
                    </div>
                  </form>
                  
                  <div className="space-y-4">
                    <SheetClose asChild>
                      <Link href="/" className="block px-2 py-2 hover:text-primary-600">
                        Home
                      </Link>
                    </SheetClose>
                    
                    <SheetClose asChild>
                      <Link href="/products" className="block px-2 py-2 hover:text-primary-600">
                        All Products
                      </Link>
                    </SheetClose>
                    
                    {categories?.map(category => (
                      <SheetClose key={category.id} asChild>
                        <Link 
                          href={`/products/category/${category.id}`} 
                          className="block px-2 py-2 hover:text-primary-600"
                        >
                          {category.name}
                        </Link>
                      </SheetClose>
                    ))}
                    
                    <SheetClose asChild>
                      <Link href="/about" className="block px-2 py-2 hover:text-primary-600">
                        About
                      </Link>
                    </SheetClose>
                    
                    <SheetClose asChild>
                      <Link href="/cart" className="block px-2 py-2 hover:text-primary-600">
                        Cart
                      </Link>
                    </SheetClose>
                    
                    {isAuthenticated ? (
                      <>
                        <SheetClose asChild>
                          <Link href="/account" className="block px-2 py-2 hover:text-primary-600">
                            My Account
                          </Link>
                        </SheetClose>
                        
                        {user?.isAdmin && (
                          <SheetClose asChild>
                            <Link href="/admin" className="block px-2 py-2 hover:text-primary-600">
                              Admin Dashboard
                            </Link>
                          </SheetClose>
                        )}
                        
                        <Button variant="outline" className="w-full" onClick={logout}>
                          Logout
                        </Button>
                      </>
                    ) : (
                      <div className="flex gap-2">
                        <SheetClose asChild>
                          <Button asChild variant="outline" className="flex-1">
                            <Link href="/login">Login</Link>
                          </Button>
                        </SheetClose>
                        
                        <SheetClose asChild>
                          <Button asChild className="flex-1">
                            <Link href="/register">Register</Link>
                          </Button>
                        </SheetClose>
                      </div>
                    )}
                  </div>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      
        {/* Mobile Search - Only visible on mobile */}
        <div className="md:hidden pb-4">
          <form onSubmit={handleSearch}>
            <div className="relative w-full">
              <input 
                type="text" 
                placeholder="Search products..." 
                className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button 
                type="submit"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-primary-600"
              >
                <i className="fas fa-search"></i>
              </button>
            </div>
          </form>
        </div>

        {/* Category Navigation */}
        <nav className="hidden md:flex items-center py-2 overflow-x-auto whitespace-nowrap">
          <Link href="/products" className="px-4 py-2 text-sm font-medium hover:text-primary-600">
            All Products
          </Link>
          
          {categories?.map(category => (
            <Link 
              key={category.id} 
              href={`/products/category/${category.id}`}
              className="px-4 py-2 text-sm font-medium hover:text-primary-600"
            >
              {category.name}
            </Link>
          ))}
          
          <Link href="/about" className="px-4 py-2 text-sm font-medium hover:text-primary-600">
            About
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
