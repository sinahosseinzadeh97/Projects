import { ReactNode } from 'react';
import { useLocation, useRoute } from 'wouter';
import { useAuth } from '@/lib/auth';
import AdminNav from '../admin/AdminNav';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface AdminLayoutProps {
  children: ReactNode;
}

const AdminLayout = ({ children }: AdminLayoutProps) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [, navigate] = useLocation();
  const [isAdminRoute] = useRoute('/admin*');
  
  // Wait for auth to load
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  
  // Redirect if not authenticated or not admin
  if (!isAuthenticated || !user?.isAdmin) {
    if (isAdminRoute) {
      navigate('/login');
      return null;
    }
    
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="destructive">
          <AlertTitle>Access Denied</AlertTitle>
          <AlertDescription>
            You don't have permission to access the admin area.
          </AlertDescription>
        </Alert>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      <AdminNav />
      <main className="flex-1 p-4 md:p-8 bg-gray-50">
        {children}
      </main>
    </div>
  );
};

export default AdminLayout;
