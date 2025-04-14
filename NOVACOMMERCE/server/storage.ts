import { 
  users, type User, type InsertUser,
  categories, type Category, type InsertCategory,
  products, type Product, type InsertProduct,
  orders, type Order, type InsertOrder,
  orderItems, type OrderItem, type InsertOrderItem,
  carts, type Cart, type InsertCart,
  cartItems, type CartItem, type InsertCartItem,
  wishlists, type Wishlist, type InsertWishlist,
  reviews, type Review, type InsertReview,
  subscribers, type Subscriber, type InsertSubscriber,
  ProductWithCategory, OrderWithItems, CartWithItems
} from "@shared/schema";

export interface IStorage {
  // User methods
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  getUserByEmail(email: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // Category methods
  getAllCategories(): Promise<Category[]>;
  getCategory(id: number): Promise<Category | undefined>;
  getCategoryBySlug(slug: string): Promise<Category | undefined>;
  createCategory(category: InsertCategory): Promise<Category>;
  updateCategory(id: number, category: Partial<InsertCategory>): Promise<Category>;
  deleteCategory(id: number): Promise<boolean>;
  
  // Product methods
  getAllProducts(): Promise<Product[]>;
  getFeaturedProducts(limit?: number): Promise<Product[]>;
  getNewProducts(limit?: number): Promise<Product[]>;
  getProductsByCategory(categoryId: number): Promise<Product[]>;
  getProduct(id: number): Promise<Product | undefined>;
  getProductBySlug(slug: string): Promise<Product | undefined>;
  getProductWithCategory(id: number): Promise<ProductWithCategory | undefined>;
  createProduct(product: InsertProduct): Promise<Product>;
  updateProduct(id: number, product: Partial<InsertProduct>): Promise<Product>;
  deleteProduct(id: number): Promise<boolean>;
  
  // Order methods
  getAllOrders(): Promise<Order[]>;
  getOrdersByUser(userId: number): Promise<Order[]>;
  getOrder(id: number): Promise<Order | undefined>;
  getOrderWithItems(id: number): Promise<OrderWithItems | undefined>;
  createOrder(order: InsertOrder): Promise<Order>;
  createOrderItem(orderItem: InsertOrderItem): Promise<OrderItem>;
  updateOrderStatus(id: number, status: string): Promise<Order>;
  
  // Cart methods
  getCart(id: number): Promise<Cart | undefined>;
  getCartByUser(userId: number): Promise<Cart | undefined>;
  getCartBySession(sessionId: string): Promise<Cart | undefined>;
  getCartWithItems(id: number): Promise<CartWithItems | undefined>;
  createCart(cart: InsertCart): Promise<Cart>;
  addCartItem(cartItem: InsertCartItem): Promise<CartItem>;
  updateCartItemQuantity(id: number, quantity: number): Promise<CartItem>;
  removeCartItem(id: number): Promise<boolean>;
  clearCart(cartId: number): Promise<boolean>;
  
  // Wishlist methods
  getWishlistByUser(userId: number): Promise<Wishlist[]>;
  addToWishlist(wishlist: InsertWishlist): Promise<Wishlist>;
  removeFromWishlist(userId: number, productId: number): Promise<boolean>;
  
  // Review methods
  getReviewsByProduct(productId: number): Promise<Review[]>;
  getReviewByUser(userId: number, productId: number): Promise<Review | undefined>;
  createReview(review: InsertReview): Promise<Review>;
  updateProductRating(productId: number): Promise<void>;
  
  // Newsletter methods
  subscribeToNewsletter(email: string): Promise<Subscriber>;
  getAllSubscribers(): Promise<Subscriber[]>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private categories: Map<number, Category>;
  private products: Map<number, Product>;
  private orders: Map<number, Order>;
  private orderItems: Map<number, OrderItem>;
  private carts: Map<number, Cart>;
  private cartItems: Map<number, CartItem>;
  private wishlists: Map<number, Wishlist>;
  private reviews: Map<number, Review>;
  private subscribers: Map<number, Subscriber>;
  
  private userIdCounter: number;
  private categoryIdCounter: number;
  private productIdCounter: number;
  private orderIdCounter: number;
  private orderItemIdCounter: number;
  private cartIdCounter: number;
  private cartItemIdCounter: number;
  private wishlistIdCounter: number;
  private reviewIdCounter: number;
  private subscriberIdCounter: number;

  constructor() {
    this.users = new Map();
    this.categories = new Map();
    this.products = new Map();
    this.orders = new Map();
    this.orderItems = new Map();
    this.carts = new Map();
    this.cartItems = new Map();
    this.wishlists = new Map();
    this.reviews = new Map();
    this.subscribers = new Map();
    
    this.userIdCounter = 1;
    this.categoryIdCounter = 1;
    this.productIdCounter = 1;
    this.orderIdCounter = 1;
    this.orderItemIdCounter = 1;
    this.cartIdCounter = 1;
    this.cartItemIdCounter = 1;
    this.wishlistIdCounter = 1;
    this.reviewIdCounter = 1;
    this.subscriberIdCounter = 1;
    
    // Initialize with sample data
    this.initializeData();
  }

  // Initialize with demo data
  private initializeData() {
    // Create admin user
    this.createUser({
      username: "admin",
      email: "admin@novacart.com",
      password: "$2b$10$8WrfN7S4Bo0jK.d5pXq1eu4/pYa/Dn3kvUOCx1iT42KJPUI0mVKDW", // "password123"
      firstName: "Admin",
      lastName: "User",
      isAdmin: true
    });
    
    // Create regular user
    this.createUser({
      username: "user",
      email: "user@example.com",
      password: "$2b$10$8WrfN7S4Bo0jK.d5pXq1eu4/pYa/Dn3kvUOCx1iT42KJPUI0mVKDW", // "password123"
      firstName: "John",
      lastName: "Doe",
      isAdmin: false
    });
    
    // Create categories
    const electronics = this.createCategory({
      name: "Electronics",
      slug: "electronics",
      description: "Latest electronic devices and gadgets",
      imageUrl: "https://images.unsplash.com/photo-1546868871-7041f2a55e12"
    });
    
    const clothing = this.createCategory({
      name: "Clothing",
      slug: "clothing",
      description: "Fashion and apparel for all styles",
      imageUrl: "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3"
    });
    
    const homeKitchen = this.createCategory({
      name: "Home & Kitchen",
      slug: "home-kitchen",
      description: "Everything for your home and kitchen",
      imageUrl: "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace"
    });
    
    const beauty = this.createCategory({
      name: "Beauty",
      slug: "beauty",
      description: "Beauty products and cosmetics",
      imageUrl: "https://images.unsplash.com/photo-1541643600914-78b084683601"
    });
    
    // Create products
    this.createProduct({
      name: "Wireless Headphones",
      slug: "wireless-headphones",
      description: "Premium Sound Quality",
      price: 89.99,
      categoryId: electronics.id,
      imageUrl: "https://images.unsplash.com/photo-1585155770447-2f66e2a397b5",
      stock: 50,
      rating: 4.5,
      reviewCount: 42,
      isFeatured: true,
      isNew: false
    });
    
    this.createProduct({
      name: "SmartWatch Series 5",
      slug: "smartwatch-series-5",
      description: "Water Resistant, Health Tracking",
      price: 199.99,
      categoryId: electronics.id,
      imageUrl: "https://images.unsplash.com/photo-1532667449560-72a95c8d381b",
      stock: 35,
      rating: 5.0,
      reviewCount: 129,
      isFeatured: true,
      isNew: true
    });
    
    this.createProduct({
      name: "Portable Bluetooth Speaker",
      slug: "portable-bluetooth-speaker",
      description: "Waterproof, 20hr Battery",
      price: 59.99,
      compareAtPrice: 79.99,
      categoryId: electronics.id,
      imageUrl: "https://images.unsplash.com/photo-1608156639585-b3a032ef9689",
      stock: 40,
      rating: 4.0,
      reviewCount: 67,
      isFeatured: true,
      isNew: false
    });
    
    this.createProduct({
      name: "Smart Home Camera",
      slug: "smart-home-camera",
      description: "HD Video, Motion Detection",
      price: 129.99,
      categoryId: electronics.id,
      imageUrl: "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb",
      stock: 25,
      rating: 3.5,
      reviewCount: 35,
      isFeatured: true,
      isNew: false
    });
    
    this.createProduct({
      name: "Smart Water Bottle",
      slug: "smart-water-bottle",
      description: "Tracks Hydration, LED Reminder",
      price: 45.99,
      categoryId: homeKitchen.id,
      imageUrl: "https://images.unsplash.com/photo-1625772452859-1c03d5bf1137",
      stock: 30,
      rating: 4.0,
      reviewCount: 12,
      isFeatured: false,
      isNew: true
    });
    
    this.createProduct({
      name: "Smart Fitness Scale",
      slug: "smart-fitness-scale",
      description: "Body Composition Analysis",
      price: 79.99,
      categoryId: homeKitchen.id,
      imageUrl: "https://images.unsplash.com/photo-1606813907291-d86efa9b94db",
      stock: 20,
      rating: 4.5,
      reviewCount: 8,
      isFeatured: false,
      isNew: true
    });
    
    this.createProduct({
      name: "Wireless Earbuds Pro",
      slug: "wireless-earbuds-pro",
      description: "Noise Cancellation, 36hr Battery",
      price: 149.99,
      categoryId: electronics.id,
      imageUrl: "https://images.unsplash.com/photo-1608156639585-b3a032ef9689",
      stock: 45,
      rating: 5.0,
      reviewCount: 23,
      isFeatured: false,
      isNew: true
    });
    
    this.createProduct({
      name: "Foldable Laptop Stand",
      slug: "foldable-laptop-stand",
      description: "Adjustable Height, Aluminum",
      price: 35.99,
      categoryId: homeKitchen.id,
      imageUrl: "https://images.unsplash.com/photo-1593642632823-8f785ba67e45",
      stock: 60,
      rating: 3.5,
      reviewCount: 19,
      isFeatured: false,
      isNew: true
    });
  }

  // User methods
  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username.toLowerCase() === username.toLowerCase()
    );
  }

  async getUserByEmail(email: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.email.toLowerCase() === email.toLowerCase()
    );
  }

  async createUser(user: InsertUser): Promise<User> {
    const id = this.userIdCounter++;
    const newUser: User = { ...user, id };
    this.users.set(id, newUser);
    return newUser;
  }

  // Category methods
  async getAllCategories(): Promise<Category[]> {
    return Array.from(this.categories.values());
  }

  async getCategory(id: number): Promise<Category | undefined> {
    return this.categories.get(id);
  }

  async getCategoryBySlug(slug: string): Promise<Category | undefined> {
    return Array.from(this.categories.values()).find(
      (category) => category.slug === slug
    );
  }

  async createCategory(category: InsertCategory): Promise<Category> {
    const id = this.categoryIdCounter++;
    const newCategory: Category = { ...category, id };
    this.categories.set(id, newCategory);
    return newCategory;
  }

  async updateCategory(id: number, category: Partial<InsertCategory>): Promise<Category> {
    const existingCategory = this.categories.get(id);
    if (!existingCategory) {
      throw new Error(`Category with ID ${id} not found`);
    }
    
    const updatedCategory = { ...existingCategory, ...category };
    this.categories.set(id, updatedCategory);
    return updatedCategory;
  }

  async deleteCategory(id: number): Promise<boolean> {
    return this.categories.delete(id);
  }

  // Product methods
  async getAllProducts(): Promise<Product[]> {
    return Array.from(this.products.values());
  }

  async getFeaturedProducts(limit?: number): Promise<Product[]> {
    const featuredProducts = Array.from(this.products.values()).filter(
      (product) => product.isFeatured
    );
    
    return limit ? featuredProducts.slice(0, limit) : featuredProducts;
  }

  async getNewProducts(limit?: number): Promise<Product[]> {
    const newProducts = Array.from(this.products.values()).filter(
      (product) => product.isNew
    );
    
    return limit ? newProducts.slice(0, limit) : newProducts;
  }

  async getProductsByCategory(categoryId: number): Promise<Product[]> {
    console.log(`Getting products for category ID: ${categoryId} (type: ${typeof categoryId})`);
    const allProducts = Array.from(this.products.values());
    console.log('All products with categoryId:', allProducts.map(p => ({ id: p.id, name: p.name, categoryId: p.categoryId })));
    
    const filteredProducts = allProducts.filter(product => {
      return product.categoryId === categoryId;
    });
    
    console.log(`Found ${filteredProducts.length} products for category ${categoryId}`);
    return filteredProducts;
  }

  async getProduct(id: number): Promise<Product | undefined> {
    return this.products.get(id);
  }

  async getProductBySlug(slug: string): Promise<Product | undefined> {
    return Array.from(this.products.values()).find(
      (product) => product.slug === slug
    );
  }

  async getProductWithCategory(id: number): Promise<ProductWithCategory | undefined> {
    const product = this.products.get(id);
    if (!product) return undefined;
    
    const category = this.categories.get(product.categoryId);
    if (!category) return undefined;
    
    return { ...product, category };
  }

  async createProduct(product: InsertProduct): Promise<Product> {
    const id = this.productIdCounter++;
    const newProduct: Product = { ...product, id };
    this.products.set(id, newProduct);
    return newProduct;
  }

  async updateProduct(id: number, product: Partial<InsertProduct>): Promise<Product> {
    const existingProduct = this.products.get(id);
    if (!existingProduct) {
      throw new Error(`Product with ID ${id} not found`);
    }
    
    const updatedProduct = { ...existingProduct, ...product };
    this.products.set(id, updatedProduct);
    return updatedProduct;
  }

  async deleteProduct(id: number): Promise<boolean> {
    return this.products.delete(id);
  }

  // Order methods
  async getAllOrders(): Promise<Order[]> {
    return Array.from(this.orders.values());
  }

  async getOrdersByUser(userId: number): Promise<Order[]> {
    return Array.from(this.orders.values()).filter(
      (order) => order.userId === userId
    );
  }

  async getOrder(id: number): Promise<Order | undefined> {
    return this.orders.get(id);
  }

  async getOrderWithItems(id: number): Promise<OrderWithItems | undefined> {
    const order = this.orders.get(id);
    if (!order) return undefined;
    
    const orderItemsList = Array.from(this.orderItems.values())
      .filter((item) => item.orderId === id);
    
    const items = await Promise.all(
      orderItemsList.map(async (item) => {
        const product = this.products.get(item.productId);
        if (!product) throw new Error(`Product with ID ${item.productId} not found`);
        return { ...item, product };
      })
    );
    
    return { ...order, items };
  }

  async createOrder(order: InsertOrder): Promise<Order> {
    const id = this.orderIdCounter++;
    const now = new Date();
    const newOrder: Order = { 
      ...order, 
      id, 
      createdAt: now 
    };
    this.orders.set(id, newOrder);
    return newOrder;
  }

  async createOrderItem(orderItem: InsertOrderItem): Promise<OrderItem> {
    const id = this.orderItemIdCounter++;
    const newOrderItem: OrderItem = { ...orderItem, id };
    this.orderItems.set(id, newOrderItem);
    return newOrderItem;
  }

  async updateOrderStatus(id: number, status: string): Promise<Order> {
    const order = this.orders.get(id);
    if (!order) {
      throw new Error(`Order with ID ${id} not found`);
    }
    
    const updatedOrder = { ...order, status: status as any };
    this.orders.set(id, updatedOrder);
    return updatedOrder;
  }

  // Cart methods
  async getCart(id: number): Promise<Cart | undefined> {
    return this.carts.get(id);
  }

  async getCartByUser(userId: number): Promise<Cart | undefined> {
    return Array.from(this.carts.values()).find(
      (cart) => cart.userId === userId
    );
  }

  async getCartBySession(sessionId: string): Promise<Cart | undefined> {
    return Array.from(this.carts.values()).find(
      (cart) => cart.sessionId === sessionId
    );
  }

  async getCartWithItems(id: number): Promise<CartWithItems | undefined> {
    const cart = this.carts.get(id);
    if (!cart) return undefined;
    
    const cartItemsList = Array.from(this.cartItems.values())
      .filter((item) => item.cartId === id);
    
    const items = await Promise.all(
      cartItemsList.map(async (item) => {
        const product = this.products.get(item.productId);
        if (!product) throw new Error(`Product with ID ${item.productId} not found`);
        return { ...item, product };
      })
    );
    
    return { ...cart, items };
  }

  async createCart(cart: InsertCart): Promise<Cart> {
    const id = this.cartIdCounter++;
    const now = new Date();
    const newCart: Cart = { ...cart, id, createdAt: now };
    this.carts.set(id, newCart);
    return newCart;
  }

  async addCartItem(cartItem: InsertCartItem): Promise<CartItem> {
    // Check if item already exists
    const existingItem = Array.from(this.cartItems.values()).find(
      (item) => item.cartId === cartItem.cartId && item.productId === cartItem.productId
    );
    
    if (existingItem) {
      return this.updateCartItemQuantity(existingItem.id, existingItem.quantity + cartItem.quantity);
    }
    
    const id = this.cartItemIdCounter++;
    const newCartItem: CartItem = { ...cartItem, id };
    this.cartItems.set(id, newCartItem);
    return newCartItem;
  }

  async updateCartItemQuantity(id: number, quantity: number): Promise<CartItem> {
    const cartItem = this.cartItems.get(id);
    if (!cartItem) {
      throw new Error(`Cart item with ID ${id} not found`);
    }
    
    const updatedCartItem = { ...cartItem, quantity };
    this.cartItems.set(id, updatedCartItem);
    return updatedCartItem;
  }

  async removeCartItem(id: number): Promise<boolean> {
    return this.cartItems.delete(id);
  }

  async clearCart(cartId: number): Promise<boolean> {
    const cartItemIds = Array.from(this.cartItems.values())
      .filter((item) => item.cartId === cartId)
      .map((item) => item.id);
    
    cartItemIds.forEach((id) => this.cartItems.delete(id));
    return true;
  }

  // Wishlist methods
  async getWishlistByUser(userId: number): Promise<Wishlist[]> {
    return Array.from(this.wishlists.values()).filter(
      (wishlist) => wishlist.userId === userId
    );
  }

  async addToWishlist(wishlist: InsertWishlist): Promise<Wishlist> {
    // Check if already exists
    const existing = Array.from(this.wishlists.values()).find(
      (item) => item.userId === wishlist.userId && item.productId === wishlist.productId
    );
    
    if (existing) {
      return existing;
    }
    
    const id = this.wishlistIdCounter++;
    const newWishlist: Wishlist = { ...wishlist, id };
    this.wishlists.set(id, newWishlist);
    return newWishlist;
  }

  async removeFromWishlist(userId: number, productId: number): Promise<boolean> {
    const wishlist = Array.from(this.wishlists.values()).find(
      (item) => item.userId === userId && item.productId === productId
    );
    
    if (!wishlist) return false;
    return this.wishlists.delete(wishlist.id);
  }

  // Review methods
  async getReviewsByProduct(productId: number): Promise<Review[]> {
    return Array.from(this.reviews.values()).filter(
      (review) => review.productId === productId
    );
  }

  async getReviewByUser(userId: number, productId: number): Promise<Review | undefined> {
    return Array.from(this.reviews.values()).find(
      (review) => review.userId === userId && review.productId === productId
    );
  }

  async createReview(review: InsertReview): Promise<Review> {
    const id = this.reviewIdCounter++;
    const now = new Date();
    const newReview: Review = { ...review, id, createdAt: now };
    this.reviews.set(id, newReview);
    
    // Update product rating
    await this.updateProductRating(review.productId);
    
    return newReview;
  }

  async updateProductRating(productId: number): Promise<void> {
    const product = this.products.get(productId);
    if (!product) return;
    
    const reviews = await this.getReviewsByProduct(productId);
    const reviewCount = reviews.length;
    
    if (reviewCount === 0) {
      product.rating = 0;
      product.reviewCount = 0;
      this.products.set(productId, product);
      return;
    }
    
    const totalRating = reviews.reduce((sum, review) => sum + review.rating, 0);
    const averageRating = totalRating / reviewCount;
    
    product.rating = averageRating;
    product.reviewCount = reviewCount;
    this.products.set(productId, product);
  }

  // Newsletter methods
  async subscribeToNewsletter(email: string): Promise<Subscriber> {
    // Check if already subscribed
    const existing = Array.from(this.subscribers.values()).find(
      (sub) => sub.email.toLowerCase() === email.toLowerCase()
    );
    
    if (existing) {
      return existing;
    }
    
    const id = this.subscriberIdCounter++;
    const now = new Date();
    const newSubscriber: Subscriber = { id, email, createdAt: now };
    this.subscribers.set(id, newSubscriber);
    return newSubscriber;
  }

  async getAllSubscribers(): Promise<Subscriber[]> {
    return Array.from(this.subscribers.values());
  }
}

// Create a storage factory
const createStorage = (): IStorage => {
  const dbUrl = process.env.DATABASE_URL || '';
  
  // Use in-memory storage if DATABASE_URL is 'memory'
  if (dbUrl === 'memory') {
    console.log('Using in-memory storage');
    return new MemStorage();
  } else {
    // For PostgreSQL storage or any other DB implementation
    console.log('Using in-memory storage (fallback)');
    return new MemStorage();
  }
};

// Export the storage instance
export const storage = createStorage();
