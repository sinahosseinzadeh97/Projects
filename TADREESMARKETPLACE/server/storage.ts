import { users, tutors, reviews, bookings, User, Tutor, Review, Booking, InsertUser, InsertTutor, InsertReview, InsertBooking, TutorWithUser, ReviewWithUser, BookingWithTutor } from "@shared/schema";
import session from "express-session";
import createMemoryStore from "memorystore";
import { log } from "./vite";

const MemoryStore = createMemoryStore(session);

// modify the interface with any CRUD methods
// you might need
export interface IStorage {
  // Session store
  sessionStore: session.SessionStore;

  // User methods
  getUser(id: number): Promise<User | undefined>;
  getUserByEmail(email: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  updateUser(id: number, user: Partial<User>): Promise<User>;
  
  // Tutor methods
  getTutor(id: number): Promise<TutorWithUser | undefined>;
  getTutorByUserId(userId: number): Promise<TutorWithUser | undefined>;
  getTutors(filters?: {
    subject?: string;
    priceMin?: number;
    priceMax?: number;
    availability?: string[];
    search?: string;
    page?: number;
    limit?: number;
    sort?: string;
  }): Promise<{ items: TutorWithUser[]; total: number; totalPages: number }>;
  getTopTutors(limit?: number): Promise<TutorWithUser[]>;
  getSimilarTutors(tutorId: number, limit?: number): Promise<TutorWithUser[]>;
  createTutor(tutor: InsertTutor): Promise<TutorWithUser>;
  updateTutor(id: number, tutor: Partial<Tutor>): Promise<TutorWithUser>;
  
  // Review methods
  getReviews(tutorId: number): Promise<ReviewWithUser[]>;
  createReview(review: InsertReview): Promise<Review>;
  
  // Booking methods
  getBooking(id: number): Promise<BookingWithTutor | undefined>;
  getBookingsForStudent(studentId: number): Promise<BookingWithTutor[]>;
  getBookingsForTutor(tutorId: number): Promise<BookingWithTutor[]>;
  createBooking(booking: InsertBooking): Promise<Booking>;
  updateBooking(id: number, booking: Partial<Booking>): Promise<Booking>;
  updatePaymentIntentId(bookingId: number, paymentIntentId: string): Promise<Booking>;
  
  // Stripe methods
  updateStripeCustomerId(userId: number, stripeCustomerId: string): Promise<User>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private tutors: Map<number, Tutor>;
  private reviews: Map<number, Review>;
  private bookings: Map<number, Booking>;
  sessionStore: session.SessionStore;
  userIdCounter: number;
  tutorIdCounter: number;
  reviewIdCounter: number;
  bookingIdCounter: number;

  constructor() {
    this.users = new Map();
    this.tutors = new Map();
    this.reviews = new Map();
    this.bookings = new Map();
    this.userIdCounter = 1;
    this.tutorIdCounter = 1;
    this.reviewIdCounter = 1;
    this.bookingIdCounter = 1;
    this.sessionStore = new MemoryStore({
      checkPeriod: 86400000, // prune expired entries every 24h
    });
  }

  // User methods
  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByEmail(email: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.email.toLowerCase() === email.toLowerCase(),
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.userIdCounter++;
    const now = new Date();
    const user: User = { 
      ...insertUser, 
      id, 
      createdAt: now, 
      updatedAt: now,
      profilePicture: null,
      bio: null,
      stripeCustomerId: null
    };
    this.users.set(id, user);
    return user;
  }

  async updateUser(id: number, userData: Partial<User>): Promise<User> {
    const user = await this.getUser(id);
    if (!user) {
      throw new Error(`User with ID ${id} not found`);
    }
    
    const updatedUser = { 
      ...user, 
      ...userData, 
      updatedAt: new Date() 
    };
    this.users.set(id, updatedUser);
    return updatedUser;
  }

  // Tutor methods
  async getTutor(id: number): Promise<TutorWithUser | undefined> {
    const tutor = this.tutors.get(id);
    if (!tutor) return undefined;
    
    const user = await this.getUser(tutor.userId);
    if (!user) return undefined;
    
    return { ...tutor, user };
  }

  async getTutorByUserId(userId: number): Promise<TutorWithUser | undefined> {
    const tutor = Array.from(this.tutors.values()).find(t => t.userId === userId);
    if (!tutor) return undefined;
    
    const user = await this.getUser(tutor.userId);
    if (!user) return undefined;
    
    return { ...tutor, user };
  }

  async getTutors(filters: {
    subject?: string;
    priceMin?: number;
    priceMax?: number;
    availability?: string[];
    search?: string;
    page?: number;
    limit?: number;
    sort?: string;
  } = {}): Promise<{ items: TutorWithUser[]; total: number; totalPages: number }> {
    let tutors = Array.from(this.tutors.values());
    
    // Apply filters
    if (filters.subject) {
      tutors = tutors.filter(tutor => 
        tutor.subjects.some(s => s.toLowerCase().includes(filters.subject!.toLowerCase()))
      );
    }
    
    if (filters.priceMin !== undefined) {
      tutors = tutors.filter(tutor => tutor.hourlyRate >= filters.priceMin!);
    }
    
    if (filters.priceMax !== undefined) {
      tutors = tutors.filter(tutor => tutor.hourlyRate <= filters.priceMax!);
    }
    
    if (filters.availability && filters.availability.length > 0) {
      tutors = tutors.filter(tutor => {
        const tutorAvailability = JSON.stringify(tutor.availability).toLowerCase();
        return filters.availability!.some(a => 
          tutorAvailability.includes(a.toLowerCase())
        );
      });
    }
    
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      const matchingTutors: Tutor[] = [];
      
      for (const tutor of tutors) {
        const user = this.users.get(tutor.userId);
        if (!user) continue;
        
        // Check if search term matches name or subjects
        if (
          user.name.toLowerCase().includes(searchLower) ||
          tutor.headline.toLowerCase().includes(searchLower) ||
          tutor.subjects.some(s => s.toLowerCase().includes(searchLower))
        ) {
          matchingTutors.push(tutor);
        }
      }
      
      tutors = matchingTutors;
    }
    
    // Apply sorting
    if (filters.sort) {
      switch (filters.sort) {
        case 'price-low':
          tutors.sort((a, b) => a.hourlyRate - b.hourlyRate);
          break;
        case 'price-high':
          tutors.sort((a, b) => b.hourlyRate - a.hourlyRate);
          break;
        case 'rating':
          tutors.sort((a, b) => b.rating - a.rating);
          break;
        default: // relevance or any other value
          // For relevance, we prioritize higher ratings
          tutors.sort((a, b) => b.rating - a.rating);
          break;
      }
    }
    
    // Get total before pagination
    const total = tutors.length;
    
    // Apply pagination
    const page = filters.page || 1;
    const limit = filters.limit || 10;
    const skip = (page - 1) * limit;
    tutors = tutors.slice(skip, skip + limit);
    
    // Get users for tutors
    const tutorsWithUsers: TutorWithUser[] = await Promise.all(
      tutors.map(async (tutor) => {
        const user = await this.getUser(tutor.userId);
        if (!user) throw new Error(`User with ID ${tutor.userId} not found`);
        return { ...tutor, user };
      })
    );
    
    return {
      items: tutorsWithUsers,
      total,
      totalPages: Math.ceil(total / limit),
    };
  }

  async getTopTutors(limit: number = 3): Promise<TutorWithUser[]> {
    const tutors = Array.from(this.tutors.values())
      .sort((a, b) => b.rating - a.rating)
      .slice(0, limit);
    
    return Promise.all(
      tutors.map(async (tutor) => {
        const user = await this.getUser(tutor.userId);
        if (!user) throw new Error(`User with ID ${tutor.userId} not found`);
        return { ...tutor, user };
      })
    );
  }

  async getSimilarTutors(tutorId: number, limit: number = 3): Promise<TutorWithUser[]> {
    const tutor = await this.getTutor(tutorId);
    if (!tutor) throw new Error(`Tutor with ID ${tutorId} not found`);
    
    const tutorSubjects = tutor.subjects;
    
    // Find tutors with similar subjects
    let similarTutors = Array.from(this.tutors.values())
      .filter(t => t.id !== tutorId) // Exclude the original tutor
      .map(t => {
        // Calculate similarity score based on common subjects
        const commonSubjects = t.subjects.filter(subject => 
          tutorSubjects.includes(subject)
        ).length;
        
        return { tutor: t, similarity: commonSubjects };
      })
      .filter(item => item.similarity > 0) // Must have at least one subject in common
      .sort((a, b) => {
        // Sort by similarity first, then by rating
        if (b.similarity !== a.similarity) {
          return b.similarity - a.similarity;
        }
        return b.tutor.rating - a.tutor.rating;
      })
      .slice(0, limit)
      .map(item => item.tutor);
    
    // If we don't have enough similar tutors, add some high-rated tutors
    if (similarTutors.length < limit) {
      const additionalTutors = Array.from(this.tutors.values())
        .filter(t => 
          t.id !== tutorId && // Not the original tutor
          !similarTutors.some(st => st.id === t.id) // Not already in the similar tutors list
        )
        .sort((a, b) => b.rating - a.rating)
        .slice(0, limit - similarTutors.length);
      
      similarTutors = [...similarTutors, ...additionalTutors];
    }
    
    return Promise.all(
      similarTutors.map(async (tutor) => {
        const user = await this.getUser(tutor.userId);
        if (!user) throw new Error(`User with ID ${tutor.userId} not found`);
        return { ...tutor, user };
      })
    );
  }

  async createTutor(insertTutor: InsertTutor): Promise<TutorWithUser> {
    const id = this.tutorIdCounter++;
    const now = new Date();
    const tutor: Tutor = {
      ...insertTutor,
      id,
      rating: 0,
      reviewCount: 0,
      createdAt: now,
      updatedAt: now
    };
    this.tutors.set(id, tutor);
    
    const user = await this.getUser(tutor.userId);
    if (!user) throw new Error(`User with ID ${tutor.userId} not found`);
    
    return { ...tutor, user };
  }

  async updateTutor(id: number, tutorData: Partial<Tutor>): Promise<TutorWithUser> {
    const tutor = this.tutors.get(id);
    if (!tutor) {
      throw new Error(`Tutor with ID ${id} not found`);
    }
    
    const updatedTutor = { 
      ...tutor, 
      ...tutorData, 
      updatedAt: new Date() 
    };
    this.tutors.set(id, updatedTutor);
    
    const user = await this.getUser(updatedTutor.userId);
    if (!user) throw new Error(`User with ID ${updatedTutor.userId} not found`);
    
    return { ...updatedTutor, user };
  }

  // Review methods
  async getReviews(tutorId: number): Promise<ReviewWithUser[]> {
    const tutorReviews = Array.from(this.reviews.values())
      .filter(review => review.tutorId === tutorId)
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
    
    return Promise.all(
      tutorReviews.map(async (review) => {
        const user = await this.getUser(review.studentId);
        if (!user) throw new Error(`User with ID ${review.studentId} not found`);
        return { ...review, user };
      })
    );
  }

  async createReview(insertReview: InsertReview): Promise<Review> {
    const id = this.reviewIdCounter++;
    const now = new Date();
    const review: Review = {
      ...insertReview,
      id,
      createdAt: now
    };
    this.reviews.set(id, review);
    
    // Update tutor rating and review count
    const tutor = this.tutors.get(review.tutorId);
    if (tutor) {
      const tutorReviews = Array.from(this.reviews.values())
        .filter(r => r.tutorId === tutor.id);
      
      const totalRating = tutorReviews.reduce((sum, r) => sum + r.rating, 0);
      const newRating = totalRating / tutorReviews.length;
      
      const updatedTutor = { 
        ...tutor, 
        rating: newRating, 
        reviewCount: tutorReviews.length,
        updatedAt: now 
      };
      this.tutors.set(tutor.id, updatedTutor);
    }
    
    return review;
  }

  // Booking methods
  async getBooking(id: number): Promise<BookingWithTutor | undefined> {
    const booking = this.bookings.get(id);
    if (!booking) return undefined;
    
    const tutor = await this.getTutor(booking.tutorId);
    if (!tutor) return undefined;
    
    return { ...booking, tutor };
  }

  async getBookingsForStudent(studentId: number): Promise<BookingWithTutor[]> {
    const studentBookings = Array.from(this.bookings.values())
      .filter(booking => booking.studentId === studentId)
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
    
    return Promise.all(
      studentBookings.map(async (booking) => {
        const tutor = await this.getTutor(booking.tutorId);
        if (!tutor) throw new Error(`Tutor with ID ${booking.tutorId} not found`);
        return { ...booking, tutor };
      })
    );
  }

  async getBookingsForTutor(tutorId: number): Promise<BookingWithTutor[]> {
    const tutorBookings = Array.from(this.bookings.values())
      .filter(booking => booking.tutorId === tutorId)
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
    
    return Promise.all(
      tutorBookings.map(async (booking) => {
        const tutor = await this.getTutor(booking.tutorId);
        if (!tutor) throw new Error(`Tutor with ID ${booking.tutorId} not found`);
        return { ...booking, tutor };
      })
    );
  }

  async createBooking(insertBooking: InsertBooking): Promise<Booking> {
    const id = this.bookingIdCounter++;
    const now = new Date();
    const booking: Booking = {
      ...insertBooking,
      id,
      status: 'pending',
      paymentIntentId: null,
      createdAt: now,
      updatedAt: now
    };
    this.bookings.set(id, booking);
    return booking;
  }

  async updateBooking(id: number, bookingData: Partial<Booking>): Promise<Booking> {
    const booking = this.bookings.get(id);
    if (!booking) {
      throw new Error(`Booking with ID ${id} not found`);
    }
    
    const updatedBooking = { 
      ...booking, 
      ...bookingData, 
      updatedAt: new Date() 
    };
    this.bookings.set(id, updatedBooking);
    
    return updatedBooking;
  }

  async updatePaymentIntentId(bookingId: number, paymentIntentId: string): Promise<Booking> {
    const booking = this.bookings.get(bookingId);
    if (!booking) {
      throw new Error(`Booking with ID ${bookingId} not found`);
    }
    
    const updatedBooking = { 
      ...booking, 
      paymentIntentId,
      updatedAt: new Date() 
    };
    this.bookings.set(bookingId, updatedBooking);
    
    return updatedBooking;
  }

  // Stripe methods
  async updateStripeCustomerId(userId: number, stripeCustomerId: string): Promise<User> {
    const user = await this.getUser(userId);
    if (!user) {
      throw new Error(`User with ID ${userId} not found`);
    }
    
    const updatedUser = { 
      ...user, 
      stripeCustomerId,
      updatedAt: new Date() 
    };
    this.users.set(userId, updatedUser);
    
    return updatedUser;
  }
}

export const storage = new MemStorage();
