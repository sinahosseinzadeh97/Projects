import { Link, useRoute } from 'wouter';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/lib/auth';

const AdminNav = () => {
  const [isDashboardActive] = useRoute('/admin');
  const [isProductsActive] = useRoute('/admin/products');
  const [isOrdersActive] = useRoute('/admin/orders');
  const [isContentActive] = useRoute('/admin/content');
  const { user, logout } = useAuth();

  return (
    <div className="bg-gray-800 text-white w-full md:w-64 flex-shrink-0">
      <div className="p-4 flex flex-col h-full">
        <div className="flex items-center justify-between mb-8">
          <Link href="/admin" className="text-xl font-bold">
            Admin Dashboard
          </Link>
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden text-white"
            asChild
          >
            <Link href="/">
              <i className="fas fa-times"></i>
            </Link>
          </Button>
        </div>
        
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-4 p-2 rounded bg-gray-700/50">
            <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center uppercase font-bold">
              {user?.username.charAt(0) || 'A'}
            </div>
            <div>
              <div className="font-medium">{user?.username || 'Admin'}</div>
              <div className="text-xs text-gray-400">Administrator</div>
            </div>
          </div>
        </div>
        
        <nav className="space-y-2 flex-1">
          <Link 
            href="/admin" 
            className={`flex items-center gap-3 px-4 py-3 rounded-lg ${isDashboardActive ? 'bg-primary-600' : 'hover:bg-gray-700'}`}
          >
            <i className="fas fa-tachometer-alt"></i>
            <span>Dashboard</span>
          </Link>
          
          <Link 
            href="/admin/products" 
            className={`flex items-center gap-3 px-4 py-3 rounded-lg ${isProductsActive ? 'bg-primary-600' : 'hover:bg-gray-700'}`}
          >
            <i className="fas fa-box"></i>
            <span>Products</span>
          </Link>
          
          <Link 
            href="/admin/orders" 
            className={`flex items-center gap-3 px-4 py-3 rounded-lg ${isOrdersActive ? 'bg-primary-600' : 'hover:bg-gray-700'}`}
          >
            <i className="fas fa-shopping-cart"></i>
            <span>Orders</span>
          </Link>
          
          <Link 
            href="/admin/content" 
            className={`flex items-center gap-3 px-4 py-3 rounded-lg ${isContentActive ? 'bg-primary-600' : 'hover:bg-gray-700'}`}
          >
            <i className="fas fa-edit"></i>
            <span>Content</span>
          </Link>
        </nav>
        
        <div className="mt-auto pt-6 space-y-2">
          <Link 
            href="/" 
            className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-700"
          >
            <i className="fas fa-home"></i>
            <span>View Store</span>
          </Link>
          
          <button 
            onClick={logout}
            className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-700 w-full text-left"
          >
            <i className="fas fa-sign-out-alt"></i>
            <span>Logout</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminNav;
