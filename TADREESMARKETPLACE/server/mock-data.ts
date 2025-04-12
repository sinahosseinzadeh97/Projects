import { storage } from "./storage";
import { scrypt, randomBytes } from "crypto";
import { promisify } from "util";
import { log } from "./vite";

const scryptAsync = promisify(scrypt);

async function hashPassword(password: string) {
  const salt = randomBytes(16).toString("hex");
  const buf = (await scryptAsync(password, salt, 64)) as Buffer;
  return `${buf.toString("hex")}.${salt}`;
}

export async function loadMockData() {
  // Check if data is already loaded
  const existingUsers = Array.from(storage.users.values());
  if (existingUsers.length > 0) {
    return;
  }

  log("Loading mock data for development", "mock-data");

  // Create users
  const studentUser = await storage.createUser({
    name: "John Student",
    email: "student@example.com",
    password: await hashPassword("password123"),
    role: "student",
  });

  const tutor1User = await storage.createUser({
    name: "Emily Rodriguez",
    email: "emily@example.com",
    password: await hashPassword("password123"),
    role: "tutor",
  });

  const tutor2User = await storage.createUser({
    name: "David Kim",
    email: "david@example.com",
    password: await hashPassword("password123"),
    role: "tutor",
  });

  const tutor3User = await storage.createUser({
    name: "Sophia Martinez",
    email: "sophia@example.com",
    password: await hashPassword("password123"),
    role: "tutor",
  });

  const tutor4User = await storage.createUser({
    name: "Ahmed Hassan",
    email: "ahmed@example.com",
    password: await hashPassword("password123"),
    role: "tutor",
  });

  // Create tutor profiles
  const tutor1 = await storage.createTutor({
    userId: tutor1User.id,
    headline: "Physics & Mathematics",
    shortBio: "PhD in Physics with 6+ years of teaching experience.",
    hourlyRate: 38,
    calendlyUrl: "https://calendly.com/emily-rodriguez",
    subjects: ["Physics", "Calculus", "Mechanics", "Quantum Physics"],
    availability: [
      { day: "Weekdays", time: "3:00 PM - 8:00 PM (EST)" },
      { day: "Weekends", time: "10:00 AM - 4:00 PM (EST)" }
    ],
    education: [
      { degree: "PhD in Physics", institution: "Stanford University", year: "2018" },
      { degree: "MSc in Physics", institution: "University of California, Berkeley", year: "2014" }
    ],
    experience: [
      { position: "Physics Instructor", company: "Science Academy", period: "2018-Present" },
      { position: "Teaching Assistant", company: "Stanford University", period: "2015-2018" }
    ],
    certifications: [
      { name: "Certified Physics Educator", issuer: "American Association of Physics Teachers", year: "2019" }
    ]
  });

  const tutor2 = await storage.createTutor({
    userId: tutor2User.id,
    headline: "Computer Science & Programming",
    shortBio: "Software engineer with experience at top tech companies.",
    hourlyRate: 50,
    calendlyUrl: "https://calendly.com/david-kim",
    subjects: ["Python", "JavaScript", "Data Structures", "Web Development"],
    availability: [
      { day: "Evenings", time: "6:00 PM - 10:00 PM (EST)" },
      { day: "Weekends", time: "9:00 AM - 5:00 PM (EST)" }
    ],
    education: [
      { degree: "MSc in Computer Science", institution: "MIT", year: "2017" },
      { degree: "BSc in Software Engineering", institution: "University of Washington", year: "2015" }
    ],
    experience: [
      { position: "Senior Software Engineer", company: "Tech Giants Inc.", period: "2018-Present" },
      { position: "Full Stack Developer", company: "Startup Heroes", period: "2015-2018" }
    ],
    certifications: [
      { name: "AWS Certified Developer", issuer: "Amazon Web Services", year: "2020" },
      { name: "Google Cloud Professional", issuer: "Google", year: "2019" }
    ]
  });

  const tutor3 = await storage.createTutor({
    userId: tutor3User.id,
    headline: "Spanish & English",
    shortBio: "Bilingual language teacher with 10+ years of experience.",
    hourlyRate: 42,
    calendlyUrl: "https://calendly.com/sophia-martinez",
    subjects: ["Spanish", "English", "Conversation", "Grammar"],
    availability: [
      { day: "Weekdays", time: "9:00 AM - 3:00 PM (EST)" }
    ],
    education: [
      { degree: "MA in Linguistics", institution: "New York University", year: "2010" },
      { degree: "BA in Spanish Literature", institution: "University of Barcelona", year: "2008" }
    ],
    experience: [
      { position: "Language Instructor", company: "Global Language Center", period: "2012-Present" },
      { position: "ESL Teacher", company: "International School of Languages", period: "2010-2012" }
    ],
    certifications: [
      { name: "TEFL Certification", issuer: "International TEFL Academy", year: "2010" },
      { name: "Spanish Teaching Certificate", issuer: "Instituto Cervantes", year: "2009" }
    ]
  });

  const tutor4 = await storage.createTutor({
    userId: tutor4User.id,
    headline: "Business & Economics",
    shortBio: "MBA graduate with background in finance and economics.",
    hourlyRate: 45,
    calendlyUrl: "https://calendly.com/ahmed-hassan",
    subjects: ["Economics", "Finance", "Marketing", "Business Strategy"],
    availability: [
      { day: "Weekdays", time: "10:00 AM - 6:00 PM (EST)" },
      { day: "Evenings", time: "7:00 PM - 9:00 PM (EST)" }
    ],
    education: [
      { degree: "MBA", institution: "Harvard Business School", year: "2016" },
      { degree: "BSc in Economics", institution: "London School of Economics", year: "2014" }
    ],
    experience: [
      { position: "Business Consultant", company: "Strategic Partners Inc.", period: "2017-Present" },
      { position: "Financial Analyst", company: "Global Bank Corp", period: "2014-2017" }
    ],
    certifications: [
      { name: "CFA Level 3", issuer: "CFA Institute", year: "2018" },
      { name: "Project Management Professional", issuer: "PMI", year: "2017" }
    ]
  });

  // Add reviews
  await storage.createReview({
    tutorId: tutor1.id,
    studentId: studentUser.id,
    rating: 5,
    comment: "Emily is an exceptional tutor! She helped me understand concepts in quantum physics that I had been struggling with for weeks. Her explanations are clear and she's patient with questions. Highly recommend!"
  });

  await storage.createReview({
    tutorId: tutor2.id,
    studentId: studentUser.id,
    rating: 5,
    comment: "David is amazing! He helped me build my first web application and explained complex programming concepts in a way that was easy to understand. Worth every penny!"
  });

  // Create bookings
  const futureDate = new Date();
  futureDate.setDate(futureDate.getDate() + 7);
  futureDate.setHours(14, 0, 0, 0);

  const pastDate = new Date();
  pastDate.setDate(pastDate.getDate() - 10);
  pastDate.setHours(15, 0, 0, 0);

  await storage.createBooking({
    tutorId: tutor1.id,
    studentId: studentUser.id,
    subject: "Quantum Physics",
    date: futureDate,
    duration: 60,
    price: 38
  });

  const pastBooking = await storage.createBooking({
    tutorId: tutor2.id,
    studentId: studentUser.id,
    subject: "JavaScript Basics",
    date: pastDate,
    duration: 90,
    price: 75
  });

  await storage.updateBooking(pastBooking.id, { status: "completed" });

  log("Mock data loaded successfully", "mock-data");
}
