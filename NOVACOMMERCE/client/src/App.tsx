import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { AuthProvider } from "./lib/auth";
import { CartProvider } from "./lib/cartStore";

// Layouts
import Header from "./components/layouts/Header";
import Footer from "./components/layouts/Footer";
import AdminLayout from "./components/layouts/AdminLayout";

// Pages
import Home from "./pages/Home";
import Products from "./pages/Products";
import ProductDetail from "./pages/ProductDetail";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import UserAccount from "./pages/UserAccount";
import NotFound from "./pages/not-found";
import About from "./pages/About";

// Admin Pages
import AdminDashboard from "./pages/Admin/Dashboard";
import AdminProducts from "./pages/Admin/Products";
import AdminOrders from "./pages/Admin/Orders";
import AdminContent from "./pages/Admin/Content";

function Router() {
  return (
    <Switch>
      {/* Public Routes */}
      <Route path="/" component={Home} />
      <Route path="/products" component={Products} />
      <Route path="/products/category/:categoryId" component={(params) => {
        console.log("Route params:", params);
        return <Products />;
      }} />
      <Route path="/product/:slug" component={ProductDetail} />
      <Route path="/cart" component={Cart} />
      <Route path="/checkout" component={Checkout} />
      <Route path="/login" component={Login} />
      <Route path="/register" component={Register} />
      <Route path="/account" component={UserAccount} />
      <Route path="/about" component={About} />
      
      {/* Admin Routes */}
      <Route path="/admin" component={() => <AdminLayout><AdminDashboard /></AdminLayout>} />
      <Route path="/admin/products" component={() => <AdminLayout><AdminProducts /></AdminLayout>} />
      <Route path="/admin/orders" component={() => <AdminLayout><AdminOrders /></AdminLayout>} />
      <Route path="/admin/content" component={() => <AdminLayout><AdminContent /></AdminLayout>} />
      
      {/* Fallback to 404 */}
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <CartProvider>
          <div className="flex flex-col min-h-screen">
            <Header />
            <main className="flex-1">
              <Router />
            </main>
            <Footer />
          </div>
          <Toaster />
        </CartProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
