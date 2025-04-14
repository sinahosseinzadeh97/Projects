import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiRequest } from './queryClient';
import { useAuth } from './auth';
import { useToast } from "@/hooks/use-toast";
import { v4 as uuidv4 } from 'uuid';

interface CartItem {
  id: number;
  cartId: number;
  productId: number;
  quantity: number;
  product: {
    id: number;
    name: string;
    price: number;
    imageUrl?: string;
  };
}

interface Cart {
  id: number;
  userId?: number;
  sessionId?: string;
  items: CartItem[];
}

interface CartContextType {
  cart: Cart | null;
  isLoading: boolean;
  addToCart: (productId: number, quantity: number) => Promise<void>;
  removeFromCart: (itemId: number) => Promise<void>;
  updateQuantity: (itemId: number, quantity: number) => Promise<void>;
  clearCart: () => Promise<void>;
  getCartTotal: () => number;
  getCartItemsCount: () => number;
}

const CartContext = createContext<CartContextType>({
  cart: null,
  isLoading: true,
  addToCart: async () => {},
  removeFromCart: async () => {},
  updateQuantity: async () => {},
  clearCart: async () => {},
  getCartTotal: () => 0,
  getCartItemsCount: () => 0,
});

export const useCart = () => useContext(CartContext);

interface CartProviderProps {
  children: ReactNode;
}

export const CartProvider = ({ children }: CartProviderProps) => {
  const [cart, setCart] = useState<Cart | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();

  // Get or create a session ID for guest users
  const getSessionId = () => {
    let sessionId = localStorage.getItem('cartSessionId');
    if (!sessionId) {
      sessionId = uuidv4();
      localStorage.setItem('cartSessionId', sessionId);
    }
    return sessionId;
  };

  const fetchCart = async () => {
    try {
      setIsLoading(true);
      
      // First, try to get or create a cart
      let response;
      
      if (isAuthenticated && user) {
        // For logged in users
        response = await apiRequest('POST', '/api/cart', { userId: user.id });
      } else {
        // For guest users using session ID
        const sessionId = getSessionId();
        response = await apiRequest('POST', '/api/cart', { sessionId });
      }
      
      const cartData = await response.json();
      setCart(cartData);
    } catch (error) {
      console.error('Error fetching cart:', error);
      toast({
        title: "Error",
        description: "Could not load your shopping cart",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, [isAuthenticated, user]);

  const addToCart = async (productId: number, quantity: number) => {
    try {
      if (!cart) {
        await fetchCart();
        if (!cart) throw new Error("Cart couldn't be created");
      }
      
      const response = await apiRequest('POST', `/api/cart/${cart.id}/items`, {
        productId,
        quantity
      });
      
      const updatedCart = await response.json();
      setCart(updatedCart);
      
      toast({
        title: "Added to cart",
        description: "Item has been added to your cart",
      });
    } catch (error) {
      console.error('Error adding to cart:', error);
      toast({
        title: "Error",
        description: "Could not add item to cart",
        variant: "destructive",
      });
    }
  };

  const removeFromCart = async (itemId: number) => {
    try {
      await apiRequest('DELETE', `/api/cart/items/${itemId}`);
      
      // Update cart state by removing the item
      if (cart) {
        const updatedItems = cart.items.filter(item => item.id !== itemId);
        setCart({ ...cart, items: updatedItems });
      }
      
      toast({
        title: "Removed from cart",
        description: "Item has been removed from your cart",
      });
    } catch (error) {
      console.error('Error removing from cart:', error);
      toast({
        title: "Error",
        description: "Could not remove item from cart",
        variant: "destructive",
      });
    }
  };

  const updateQuantity = async (itemId: number, quantity: number) => {
    try {
      if (quantity < 1) {
        await removeFromCart(itemId);
        return;
      }
      
      const response = await apiRequest('PUT', `/api/cart/items/${itemId}`, { quantity });
      const updatedCart = await response.json();
      setCart(updatedCart);
    } catch (error) {
      console.error('Error updating quantity:', error);
      toast({
        title: "Error",
        description: "Could not update item quantity",
        variant: "destructive",
      });
    }
  };

  const clearCart = async () => {
    try {
      if (!cart) return;
      
      await apiRequest('DELETE', `/api/cart/${cart.id}/clear`);
      setCart({ ...cart, items: [] });
      
      toast({
        title: "Cart cleared",
        description: "All items have been removed from your cart",
      });
    } catch (error) {
      console.error('Error clearing cart:', error);
      toast({
        title: "Error",
        description: "Could not clear your cart",
        variant: "destructive",
      });
    }
  };

  const getCartTotal = () => {
    if (!cart || !cart.items.length) return 0;
    return cart.items.reduce((total, item) => total + (item.product.price * item.quantity), 0);
  };

  const getCartItemsCount = () => {
    if (!cart || !cart.items.length) return 0;
    return cart.items.reduce((count, item) => count + item.quantity, 0);
  };

  const value = {
    cart,
    isLoading,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    getCartTotal,
    getCartItemsCount,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};
