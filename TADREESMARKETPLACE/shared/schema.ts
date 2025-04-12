import { pgTable, text, serial, integer, boolean, timestamp, jsonb, doublePrecision } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Users table
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
  password: text("password").notNull(),
  role: text("role", { enum: ["student", "tutor", "admin"] }).notNull().default("student"),
  profilePicture: text("profile_picture"),
  bio: text("bio"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
  stripeCustomerId: text("stripe_customer_id"),
});

export const insertUserSchema = createInsertSchema(users).pick({
  name: true,
  email: true,
  password: true,
  role: true,
});

// Tutors table - extends user with tutor-specific information
export const tutors = pgTable("tutors", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().references(() => users.id),
  headline: text("headline").notNull(),
  shortBio: text("short_bio").notNull(),
  hourlyRate: doublePrecision("hourly_rate").notNull(),
  calendlyUrl: text("calendly_url"),
  subjects: text("subjects").array(),
  availability: jsonb("availability").notNull(),
  education: jsonb("education").notNull(),
  experience: jsonb("experience").notNull(),
  certifications: jsonb("certifications"),
  rating: doublePrecision("rating").default(0),
  reviewCount: integer("review_count").default(0),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertTutorSchema = createInsertSchema(tutors).omit({
  id: true,
  rating: true,
  reviewCount: true,
  createdAt: true,
  updatedAt: true,
});

// Reviews table
export const reviews = pgTable("reviews", {
  id: serial("id").primaryKey(),
  tutorId: integer("tutor_id").notNull().references(() => tutors.id),
  studentId: integer("student_id").notNull().references(() => users.id),
  rating: integer("rating").notNull(),
  comment: text("comment").notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertReviewSchema = createInsertSchema(reviews).omit({
  id: true,
  createdAt: true,
});

// Bookings table
export const bookings = pgTable("bookings", {
  id: serial("id").primaryKey(),
  tutorId: integer("tutor_id").notNull().references(() => tutors.id),
  studentId: integer("student_id").notNull().references(() => users.id),
  subject: text("subject").notNull(),
  date: timestamp("date").notNull(),
  duration: integer("duration").notNull(), // in minutes
  price: doublePrecision("price").notNull(),
  status: text("status", { enum: ["pending", "confirmed", "cancelled", "completed"] }).notNull().default("pending"),
  paymentIntentId: text("payment_intent_id"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertBookingSchema = createInsertSchema(bookings).omit({
  id: true,
  status: true,
  paymentIntentId: true,
  createdAt: true,
  updatedAt: true,
});

// Types
export type User = typeof users.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;

export type Tutor = typeof tutors.$inferSelect;
export type InsertTutor = z.infer<typeof insertTutorSchema>;

export type Review = typeof reviews.$inferSelect;
export type InsertReview = z.infer<typeof insertReviewSchema>;

export type Booking = typeof bookings.$inferSelect;
export type InsertBooking = z.infer<typeof insertBookingSchema>;

// Extended types for API responses
export type TutorWithUser = Tutor & {
  user: User;
};

export type ReviewWithUser = Review & {
  user: User;
};

export type BookingWithTutor = Booking & {
  tutor: TutorWithUser;
};

export type BookingWithStudentAndTutor = Booking & {
  student: User;
  tutor: TutorWithUser;
};
