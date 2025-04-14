import type { Express, Request, Response } from "express";
import { createServer, type Server } from "http";
import { z } from "zod";
import { storage } from "./storage";
import { 
  insertUserSchema, 
  insertProductSchema,
  insertCategorySchema,
  insertOrderSchema, 
  insertCartSchema, 
  insertCartItemSchema,
  insertReviewSchema,
  insertSubscriberSchema,
} from "@shared/schema";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import Stripe from "stripe";

// JWT secret key
const JWT_SECRET = process.env.JWT_SECRET || "novacart-secret-key";

// Stripe setup
if (!process.env.STRIPE_SECRET_KEY) {
  console.warn('Missing STRIPE_SECRET_KEY - payment functionality will be limited');
}

const stripe = process.env.STRIPE_SECRET_KEY 
  ? new Stripe(process.env.STRIPE_SECRET_KEY, { apiVersion: "2023-10-16" })
  : undefined;

// Auth middleware
const authenticateToken = (req: Request, res: Response, next: Function) => {
  // Get token from Authorization header
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) return res.status(401).json({ message: "Authentication required" });

  try {
    const user = jwt.verify(token, JWT_SECRET);
    req.user = user;
    next();
  } catch (error) {
    return res.status(403).json({ message: "Invalid or expired token" });
  }
};

// Admin middleware
const isAdmin = (req: Request, res: Response, next: Function) => {
  if (!req.user || !req.user.isAdmin) {
    return res.status(403).json({ message: "Admin access required" });
  }
  next();
};

// Generate JWT token
const generateToken = (user: any) => {
  // Remove password from token payload
  const { password, ...userWithoutPassword } = user;
  return jwt.sign(userWithoutPassword, JWT_SECRET, { expiresIn: '24h' });
};

// Extend Request type to include user
declare global {
  namespace Express {
    interface Request {
      user?: any;
    }
  }
}

export async function registerRoutes(app: Express): Promise<Server> {

  // Public API endpoints
  
  // Auth routes
  app.post("/api/auth/register", async (req, res) => {
    try {
      const userData = insertUserSchema.parse(req.body);
      
      // Check if user already exists
      const existingUser = await storage.getUserByUsername(userData.username);
      if (existingUser) {
        return res.status(400).json({ message: "Username already exists" });
      }
      
      const existingEmail = await storage.getUserByEmail(userData.email);
      if (existingEmail) {
        return res.status(400).json({ message: "Email already exists" });
      }
      
      // Hash password
      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash(userData.password, salt);
      
      // Create user with hashed password
      const user = await storage.createUser({
        ...userData,
        password: hashedPassword
      });
      
      // Generate JWT token
      const token = generateToken(user);
      
      res.status(201).json({ 
        user: { 
          id: user.id,
          username: user.username,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          isAdmin: user.isAdmin
        }, 
        token 
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: error.errors });
      }
      res.status(500).json({ message: "Error creating user" });
    }
  });

  app.post("/api/auth/login", async (req, res) => {
    try {
      const { username, password } = req.body;
      
      // Validate request body
      if (!username || !password) {
        return res.status(400).json({ message: "Username and password are required" });
      }
      
      // Find user
      const user = await storage.getUserByUsername(username);
      if (!user) {
        return res.status(401).json({ message: "Invalid credentials" });
      }
      
      // Verify password
      const validPassword = await bcrypt.compare(password, user.password);
      if (!validPassword) {
        return res.status(401).json({ message: "Invalid credentials" });
      }
      
      // Generate JWT token
      const token = generateToken(user);
      
      res.json({ 
        user: { 
          id: user.id,
          username: user.username,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          isAdmin: user.isAdmin
        }, 
        token 
      });
    } catch (error) {
      res.status(500).json({ message: "Error logging in" });
    }
  });

  // Category routes
  app.get("/api/categories", async (req, res) => {
    try {
      const categories = await storage.getAllCategories();
      res.json(categories);
    } catch (error) {
      res.status(500).json({ message: "Error fetching categories" });
    }
  });

  app.get("/api/categories/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const category = await storage.getCategory(id);
      
      if (!category) {
        return res.status(404).json({ message: "Category not found" });
      }
      
      res.json(category);
    } catch (error) {
      res.status(500).json({ message: "Error fetching category" });
    }
  });

  app.get("/api/categories/:id/products", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      console.log(`Fetching products for category ID: ${id}`);
      const products = await storage.getProductsByCategory(id);
      console.log(`Found ${products.length} products for category ID: ${id}`);
      console.log('Products:', products);
      res.json(products);
    } catch (error) {
      console.error("Error fetching products by category:", error);
      res.status(500).json({ message: "Error fetching products" });
    }
  });

  // Product routes
  app.get("/api/products", async (req, res) => {
    try {
      const products = await storage.getAllProducts();
      console.log('All products from API:', products.map(p => ({ id: p.id, name: p.name, categoryId: p.categoryId })));
      res.json(products);
    } catch (error) {
      res.status(500).json({ message: "Error fetching products" });
    }
  });

  app.get("/api/products/featured", async (req, res) => {
    try {
      const limit = req.query.limit ? parseInt(req.query.limit as string) : undefined;
      const products = await storage.getFeaturedProducts(limit);
      res.json(products);
    } catch (error) {
      res.status(500).json({ message: "Error fetching featured products" });
    }
  });

  app.get("/api/products/new", async (req, res) => {
    try {
      const limit = req.query.limit ? parseInt(req.query.limit as string) : undefined;
      const products = await storage.getNewProducts(limit);
      res.json(products);
    } catch (error) {
      res.status(500).json({ message: "Error fetching new products" });
    }
  });

  app.get("/api/products/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const product = await storage.getProductWithCategory(id);
      
      if (!product) {
        return res.status(404).json({ message: "Product not found" });
      }
      
      res.json(product);
    } catch (error) {
      res.status(500).json({ message: "Error fetching product" });
    }
  });

  app.get("/api/products/slug/:slug", async (req, res) => {
    try {
      const slug = req.params.slug;
      const product = await storage.getProductBySlug(slug);
      
      if (!product) {
        return res.status(404).json({ message: "Product not found" });
      }
      
      const productWithCategory = await storage.getProductWithCategory(product.id);
      res.json(productWithCategory);
    } catch (error) {
      res.status(500).json({ message: "Error fetching product" });
    }
  });

  // Cart routes
  app.post("/api/cart", async (req, res) => {
    try {
      const cartData = insertCartSchema.parse(req.body);
      
      // Check if user/session already has a cart
      let cart;
      if (cartData.userId) {
        cart = await storage.getCartByUser(cartData.userId);
      } else if (cartData.sessionId) {
        cart = await storage.getCartBySession(cartData.sessionId);
      }
      
      if (cart) {
        const cartWithItems = await storage.getCartWithItems(cart.id);
        return res.json(cartWithItems);
      }
      
      // Create new cart
      const newCart = await storage.createCart(cartData);
      const cartWithItems = await storage.getCartWithItems(newCart.id);
      res.status(201).json(cartWithItems);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: error.errors });
      }
      res.status(500).json({ message: "Error creating cart" });
    }
  });

  app.get("/api/cart/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const cart = await storage.getCartWithItems(id);
      
      if (!cart) {
        return res.status(404).json({ message: "Cart not found" });
      }
      
      res.json(cart);
    } catch (error) {
      res.status(500).json({ message: "Error fetching cart" });
    }
  });

  app.post("/api/cart/:id/items", async (req, res) => {
    try {
      const cartId = parseInt(req.params.id);
      const cart = await storage.getCart(cartId);
      
      if (!cart) {
        return res.status(404).json({ message: "Cart not found" });
      }
      
      const cartItemData = insertCartItemSchema.parse({
        ...req.body,
        cartId
      });
      
      const cartItem = await storage.addCartItem(cartItemData);
      const updatedCart = await storage.getCartWithItems(cartId);
      
      res.status(201).json(updatedCart);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: error.errors });
      }
      res.status(500).json({ message: "Error adding item to cart" });
    }
  });

  app.put("/api/cart/items/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const { quantity } = req.body;
      
      if (typeof quantity !== 'number' || quantity < 1) {
        return res.status(400).json({ message: "Quantity must be a positive number" });
      }
      
      const cartItem = await storage.updateCartItemQuantity(id, quantity);
      
      // Get the updated cart
      const cart = await storage.getCartWithItems(cartItem.cartId);
      res.json(cart);
    } catch (error) {
      res.status(500).json({ message: "Error updating cart item" });
    }
  });

  app.delete("/api/cart/items/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const success = await storage.removeCartItem(id);
      
      if (!success) {
        return res.status(404).json({ message: "Cart item not found" });
      }
      
      res.json({ message: "Item removed from cart" });
    } catch (error) {
      res.status(500).json({ message: "Error removing item from cart" });
    }
  });

  app.delete("/api/cart/:id/clear", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const success = await storage.clearCart(id);
      
      if (!success) {
        return res.status(404).json({ message: "Cart not found" });
      }
      
      res.json({ message: "Cart cleared" });
    } catch (error) {
      res.status(500).json({ message: "Error clearing cart" });
    }
  });

  // Review routes
  app.get("/api/products/:id/reviews", async (req, res) => {
    try {
      const productId = parseInt(req.params.id);
      const reviews = await storage.getReviewsByProduct(productId);
      res.json(reviews);
    } catch (error) {
      res.status(500).json({ message: "Error fetching reviews" });
    }
  });

  app.post("/api/reviews", authenticateToken, async (req, res) => {
    try {
      const reviewData = insertReviewSchema.parse({
        ...req.body,
        userId: req.user.id
      });
      
      // Check if user already reviewed this product
      const existingReview = await storage.getReviewByUser(req.user.id, reviewData.productId);
      if (existingReview) {
        return res.status(400).json({ message: "You have already reviewed this product" });
      }
      
      const review = await storage.createReview(reviewData);
      res.status(201).json(review);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: error.errors });
      }
      res.status(500).json({ message: "Error creating review" });
    }
  });

  // Newsletter subscription
  app.post("/api/newsletter/subscribe", async (req, res) => {
    try {
      const { email } = req.body;
      
      if (!email || typeof email !== 'string') {
        return res.status(400).json({ message: "Valid email is required" });
      }
      
      // Validate email format
      const emailSchema = z.string().email();
      const validatedEmail = emailSchema.parse(email);
      
      const subscriber = await storage.subscribeToNewsletter(validatedEmail);
      res.status(201).json({ message: "Successfully subscribed to newsletter" });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: "Invalid email format" });
      }
      res.status(500).json({ message: "Error subscribing to newsletter" });
    }
  });

  // Stripe payment intent
  app.post("/api/payment/create-intent", authenticateToken, async (req, res) => {
    try {
      if (!stripe) {
        return res.status(500).json({ 
          message: "Stripe is not configured. Please set the STRIPE_SECRET_KEY environment variable."
        });
      }

      const { amount } = req.body;
      
      if (typeof amount !== 'number' || amount <= 0) {
        return res.status(400).json({ message: "Valid amount is required" });
      }
      
      const paymentIntent = await stripe.paymentIntents.create({
        amount: Math.round(amount * 100), // convert to cents
        currency: "usd",
        metadata: {
          userId: req.user.id.toString()
        }
      });
      
      res.json({ clientSecret: paymentIntent.client_secret });
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  // Order routes
  app.post("/api/orders", authenticateToken, async (req, res) => {
    try {
      // Include user ID from token
      const orderData = insertOrderSchema.parse({
        ...req.body,
        userId: req.user.id
      });
      
      const order = await storage.createOrder(orderData);
      
      // Create order items
      if (req.body.items && Array.isArray(req.body.items)) {
        for (const item of req.body.items) {
          await storage.createOrderItem({
            orderId: order.id,
            productId: item.productId,
            quantity: item.quantity,
            price: item.price
          });
        }
      }
      
      const orderWithItems = await storage.getOrderWithItems(order.id);
      res.status(201).json(orderWithItems);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: error.errors });
      }
      res.status(500).json({ message: "Error creating order" });
    }
  });

  app.get("/api/orders/user", authenticateToken, async (req, res) => {
    try {
      const orders = await storage.getOrdersByUser(req.user.id);
      
      // Get all orders with items
      const ordersWithItems = await Promise.all(
        orders.map(order => storage.getOrderWithItems(order.id))
      );
      
      res.json(ordersWithItems);
    } catch (error) {
      res.status(500).json({ message: "Error fetching orders" });
    }
  });

  app.get("/api/orders/:id", authenticateToken, async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const order = await storage.getOrderWithItems(id);
      
      if (!order) {
        return res.status(404).json({ message: "Order not found" });
      }
      
      // Check if order belongs to user or user is admin
      if (order.userId !== req.user.id && !req.user.isAdmin) {
        return res.status(403).json({ message: "Unauthorized" });
      }
      
      res.json(order);
    } catch (error) {
      res.status(500).json({ message: "Error fetching order" });
    }
  });

  // Wishlist routes
  app.get("/api/wishlist", authenticateToken, async (req, res) => {
    try {
      const wishlists = await storage.getWishlistByUser(req.user.id);
      
      // Get product details for each wishlist item
      const wishlistWithProducts = await Promise.all(
        wishlists.map(async (item) => {
          const product = await storage.getProduct(item.productId);
          return { ...item, product };
        })
      );
      
      res.json(wishlistWithProducts);
    } catch (error) {
      res.status(500).json({ message: "Error fetching wishlist" });
    }
  });

  app.post("/api/wishlist", authenticateToken, async (req, res) => {
    try {
      const { productId } = req.body;
      
      if (typeof productId !== 'number') {
        return res.status(400).json({ message: "Valid product ID is required" });
      }
      
      // Check if product exists
      const product = await storage.getProduct(productId);
      if (!product) {
        return res.status(404).json({ message: "Product not found" });
      }
      
      const wishlist = await storage.addToWishlist({
        userId: req.user.id,
        productId
      });
      
      res.status(201).json({ message: "Product added to wishlist" });
    } catch (error) {
      res.status(500).json({ message: "Error adding to wishlist" });
    }
  });

  app.delete("/api/wishlist/:productId", authenticateToken, async (req, res) => {
    try {
      const productId = parseInt(req.params.productId);
      const success = await storage.removeFromWishlist(req.user.id, productId);
      
      if (!success) {
        return res.status(404).json({ message: "Product not found in wishlist" });
      }
      
      res.json({ message: "Product removed from wishlist" });
    } catch (error) {
      res.status(500).json({ message: "Error removing from wishlist" });
    }
  });

  // Admin routes
  
  // Admin - Categories
  app.post("/api/admin/categories", authenticateToken, isAdmin, async (req, res) => {
    try {
      const categoryData = insertCategorySchema.parse(req.body);
      const category = await storage.createCategory(categoryData);
      res.status(201).json(category);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: error.errors });
      }
      res.status(500).json({ message: "Error creating category" });
    }
  });

  app.put("/api/admin/categories/:id", authenticateToken, isAdmin, async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const categoryData = insertCategorySchema.partial().parse(req.body);
      const category = await storage.updateCategory(id, categoryData);
      res.json(category);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: error.errors });
      }
      res.status(500).json({ message: "Error updating category" });
    }
  });

  app.delete("/api/admin/categories/:id", authenticateToken, isAdmin, async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const success = await storage.deleteCategory(id);
      
      if (!success) {
        return res.status(404).json({ message: "Category not found" });
      }
      
      res.json({ message: "Category deleted" });
    } catch (error) {
      res.status(500).json({ message: "Error deleting category" });
    }
  });

  // Admin - Products
  app.post("/api/admin/products", authenticateToken, isAdmin, async (req, res) => {
    try {
      const productData = insertProductSchema.parse(req.body);
      const product = await storage.createProduct(productData);
      res.status(201).json(product);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: error.errors });
      }
      res.status(500).json({ message: "Error creating product" });
    }
  });

  app.put("/api/admin/products/:id", authenticateToken, isAdmin, async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const productData = insertProductSchema.partial().parse(req.body);
      const product = await storage.updateProduct(id, productData);
      res.json(product);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: error.errors });
      }
      res.status(500).json({ message: "Error updating product" });
    }
  });

  app.delete("/api/admin/products/:id", authenticateToken, isAdmin, async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const success = await storage.deleteProduct(id);
      
      if (!success) {
        return res.status(404).json({ message: "Product not found" });
      }
      
      res.json({ message: "Product deleted" });
    } catch (error) {
      res.status(500).json({ message: "Error deleting product" });
    }
  });

  // Admin - Orders
  app.get("/api/admin/orders", authenticateToken, isAdmin, async (req, res) => {
    try {
      const orders = await storage.getAllOrders();
      
      // Get orders with items
      const ordersWithItems = await Promise.all(
        orders.map(order => storage.getOrderWithItems(order.id))
      );
      
      res.json(ordersWithItems);
    } catch (error) {
      res.status(500).json({ message: "Error fetching orders" });
    }
  });

  app.put("/api/admin/orders/:id/status", authenticateToken, isAdmin, async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const { status } = req.body;
      
      if (!status || typeof status !== 'string') {
        return res.status(400).json({ message: "Valid status is required" });
      }
      
      // Validate status
      if (!['pending', 'processing', 'shipped', 'delivered', 'cancelled'].includes(status)) {
        return res.status(400).json({ message: "Invalid status" });
      }
      
      const order = await storage.updateOrderStatus(id, status);
      res.json(order);
    } catch (error) {
      res.status(500).json({ message: "Error updating order status" });
    }
  });

  // Admin - Newsletter
  app.get("/api/admin/subscribers", authenticateToken, isAdmin, async (req, res) => {
    try {
      const subscribers = await storage.getAllSubscribers();
      res.json(subscribers);
    } catch (error) {
      res.status(500).json({ message: "Error fetching subscribers" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
