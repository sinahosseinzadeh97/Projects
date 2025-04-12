import type { Express, Request, Response } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { setupAuth } from "./auth";
import { z } from "zod";
import Stripe from "stripe";
import { insertBookingSchema } from "@shared/schema";
import { loadMockData } from "./mock-data";

// Initialize Stripe with the secret key
const stripeSecretKey = process.env.STRIPE_SECRET_KEY || "sk_test_dummy_key";
const stripe = new Stripe(stripeSecretKey, {
  apiVersion: "2025-03-31.basil",
});

export async function registerRoutes(app: Express): Promise<Server> {
  // Set up authentication routes
  setupAuth(app);

  // Load mock data for development
  if (process.env.NODE_ENV !== "production") {
    await loadMockData();
  }

  // User
  app.post("/api/user/become-tutor", async (req, res) => {
    if (!req.isAuthenticated()) {
      return res.status(401).json({ message: "You must be logged in to become a tutor" });
    }

    try {
      const tutorSchema = z.object({
        expertise: z.string().min(1, "Please select your area of expertise"),
        experience: z.string().min(1, "Years of experience is required"),
        education: z.string().min(3, "Education information is required"),
        hourlyRate: z.string().min(1, "Hourly rate is required"),
        bio: z.string().min(30, "Bio must be at least 30 characters").max(500, "Bio must not exceed 500 characters"),
      });
      
      const tutorData = tutorSchema.parse(req.body);
      
      // Update user role to tutor
      await storage.updateUser(req.user!.id, { role: "tutor" });
      
      // Create tutor profile
      const tutor = await storage.createTutor({
        userId: req.user!.id,
        headline: `${tutorData.expertise} Tutor`,
        shortBio: tutorData.bio,
        hourlyRate: parseFloat(tutorData.hourlyRate),
        subjects: [tutorData.expertise],
        availability: { days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], hours: "9AM-5PM" },
        education: { degree: tutorData.education },
        experience: { years: parseInt(tutorData.experience) },
      });
      
      res.status(201).json({
        message: "Tutor profile created successfully",
        tutor
      });
    } catch (error) {
      console.error("Error becoming a tutor:", error);
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: "Invalid tutor data", errors: error.errors });
      }
      res.status(500).json({ message: "Error creating tutor profile" });
    }
  });

  // Tutors
  app.get("/api/tutors", async (req, res) => {
    try {
      const { subject, priceMin, priceMax, availability, search, page, limit, sort } = req.query;
      
      const filters = {
        subject: subject as string | undefined,
        priceMin: priceMin ? parseFloat(priceMin as string) : undefined,
        priceMax: priceMax ? parseFloat(priceMax as string) : undefined,
        availability: availability 
          ? Array.isArray(availability)
            ? availability as string[]
            : [availability as string]
          : undefined,
        search: search as string | undefined,
        page: page ? parseInt(page as string, 10) : 1,
        limit: limit ? parseInt(limit as string, 10) : 10,
        sort: sort as string | undefined,
      };
      
      const tutors = await storage.getTutors(filters);
      res.json(tutors);
    } catch (error) {
      console.error("Error fetching tutors:", error);
      res.status(500).json({ message: "Error fetching tutors" });
    }
  });

  app.get("/api/tutors/top", async (req, res) => {
    try {
      const limit = req.query.limit ? parseInt(req.query.limit as string, 10) : 3;
      const topTutors = await storage.getTopTutors(limit);
      res.json(topTutors);
    } catch (error) {
      console.error("Error fetching top tutors:", error);
      res.status(500).json({ message: "Error fetching top tutors" });
    }
  });

  app.get("/api/tutors/similar/:id", async (req, res) => {
    try {
      const tutorId = parseInt(req.params.id, 10);
      const limit = req.query.limit ? parseInt(req.query.limit as string, 10) : 3;
      
      const similarTutors = await storage.getSimilarTutors(tutorId, limit);
      res.json(similarTutors);
    } catch (error) {
      console.error("Error fetching similar tutors:", error);
      res.status(500).json({ message: "Error fetching similar tutors" });
    }
  });

  app.get("/api/tutors/:id", async (req, res) => {
    try {
      const tutorId = parseInt(req.params.id, 10);
      const tutor = await storage.getTutor(tutorId);
      
      if (!tutor) {
        return res.status(404).json({ message: "Tutor not found" });
      }
      
      // Get reviews for this tutor
      const reviews = await storage.getReviews(tutorId);
      
      // Return tutor with reviews
      res.json({
        ...tutor,
        reviews: reviews.slice(0, 3), // Return just the 3 most recent reviews
      });
    } catch (error) {
      console.error("Error fetching tutor:", error);
      res.status(500).json({ message: "Error fetching tutor" });
    }
  });

  // Reviews
  app.get("/api/tutors/:id/reviews", async (req, res) => {
    try {
      const tutorId = parseInt(req.params.id, 10);
      const reviews = await storage.getReviews(tutorId);
      res.json(reviews);
    } catch (error) {
      console.error("Error fetching reviews:", error);
      res.status(500).json({ message: "Error fetching reviews" });
    }
  });

  app.post("/api/reviews", async (req, res) => {
    if (!req.isAuthenticated()) {
      return res.status(401).json({ message: "You must be logged in to create a review" });
    }

    try {
      const reviewSchema = z.object({
        tutorId: z.number(),
        rating: z.number().min(1).max(5),
        comment: z.string().min(1),
      });
      
      const { tutorId, rating, comment } = reviewSchema.parse(req.body);
      
      // Check if tutor exists
      const tutor = await storage.getTutor(tutorId);
      if (!tutor) {
        return res.status(404).json({ message: "Tutor not found" });
      }
      
      // Create the review
      const review = await storage.createReview({
        tutorId,
        studentId: req.user!.id,
        rating,
        comment,
      });
      
      res.status(201).json(review);
    } catch (error) {
      console.error("Error creating review:", error);
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: "Invalid review data", errors: error.errors });
      }
      res.status(500).json({ message: "Error creating review" });
    }
  });

  // Bookings
  app.get("/api/bookings", async (req, res) => {
    if (!req.isAuthenticated()) {
      return res.status(401).json({ message: "You must be logged in to view bookings" });
    }

    try {
      const userId = req.user!.id;
      const role = req.user!.role;
      
      let bookings;
      if (role === "student") {
        bookings = await storage.getBookingsForStudent(userId);
      } else if (role === "tutor") {
        // Get tutor record for this user
        const tutor = await storage.getTutorByUserId(userId);
        if (!tutor) {
          return res.status(404).json({ message: "Tutor profile not found" });
        }
        bookings = await storage.getBookingsForTutor(tutor.id);
      } else {
        return res.status(403).json({ message: "Unauthorized role" });
      }
      
      res.json(bookings);
    } catch (error) {
      console.error("Error fetching bookings:", error);
      res.status(500).json({ message: "Error fetching bookings" });
    }
  });

  app.get("/api/bookings/:id", async (req, res) => {
    if (!req.isAuthenticated()) {
      return res.status(401).json({ message: "You must be logged in to view booking details" });
    }

    try {
      const bookingId = parseInt(req.params.id, 10);
      const booking = await storage.getBooking(bookingId);
      
      if (!booking) {
        return res.status(404).json({ message: "Booking not found" });
      }
      
      // Check if the user has permission to view this booking
      const userId = req.user!.id;
      const role = req.user!.role;
      
      if (role === "student" && booking.studentId !== userId) {
        return res.status(403).json({ message: "Unauthorized" });
      }
      
      if (role === "tutor") {
        const tutor = await storage.getTutorByUserId(userId);
        if (!tutor || tutor.id !== booking.tutorId) {
          return res.status(403).json({ message: "Unauthorized" });
        }
      }
      
      res.json(booking);
    } catch (error) {
      console.error("Error fetching booking:", error);
      res.status(500).json({ message: "Error fetching booking" });
    }
  });

  app.post("/api/bookings", async (req, res) => {
    if (!req.isAuthenticated()) {
      return res.status(401).json({ message: "You must be logged in to create a booking" });
    }

    try {
      const bookingData = insertBookingSchema.parse({
        ...req.body,
        studentId: req.user!.id,
      });
      
      // Check if tutor exists
      const tutor = await storage.getTutor(bookingData.tutorId);
      if (!tutor) {
        return res.status(404).json({ message: "Tutor not found" });
      }
      
      // Create the booking
      const booking = await storage.createBooking(bookingData);
      
      res.status(201).json(booking);
    } catch (error) {
      console.error("Error creating booking:", error);
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: "Invalid booking data", errors: error.errors });
      }
      res.status(500).json({ message: "Error creating booking" });
    }
  });

  // Stripe payment
  app.post("/api/create-payment-intent", async (req, res) => {
    if (!req.isAuthenticated()) {
      return res.status(401).json({ message: "You must be logged in to make a payment" });
    }

    try {
      const { sessionId, amount } = req.body;
      
      if (!sessionId || !amount) {
        return res.status(400).json({ message: "Missing required payment details" });
      }
      
      // In a real app, fetch booking details by sessionId
      // For MVP, we'll use the provided amount
      
      // Create a PaymentIntent with the order amount and currency
      const paymentIntent = await stripe.paymentIntents.create({
        amount: Math.round(amount * 100), // convert to cents
        currency: "usd",
        metadata: {
          sessionId: sessionId.toString(),
          userId: req.user!.id.toString()
        },
      });
      
      // Update booking with payment intent ID
      if (sessionId) {
        await storage.updatePaymentIntentId(parseInt(sessionId), paymentIntent.id);
      }
      
      res.json({
        clientSecret: paymentIntent.client_secret,
      });
    } catch (error) {
      console.error("Error creating payment intent:", error);
      res.status(500).json({ message: "Error processing payment" });
    }
  });

  // Sessions (Bookings) - For checkout page
  app.get("/api/sessions/:id", async (req, res) => {
    if (!req.isAuthenticated()) {
      return res.status(401).json({ message: "You must be logged in to view session details" });
    }

    try {
      const sessionId = parseInt(req.params.id, 10);
      const booking = await storage.getBooking(sessionId);
      
      if (!booking) {
        return res.status(404).json({ message: "Session not found" });
      }
      
      // Format the session data for the checkout page
      const sessionData = {
        id: booking.id,
        tutorId: booking.tutorId,
        tutor: booking.tutor,
        subject: booking.subject,
        date: booking.date.toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        }),
        time: booking.date.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit'
        }),
        duration: booking.duration,
        price: booking.price,
      };
      
      res.json(sessionData);
    } catch (error) {
      console.error("Error fetching session:", error);
      res.status(500).json({ message: "Error fetching session details" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
