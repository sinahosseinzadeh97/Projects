export interface AvailabilityType {
  day: string;
  time: string;
}

export interface Tutor {
  id: string;
  name: string;
  profilePicture?: string;
  headline: string;
  bio: string;
  shortBio?: string;
  subjects: string[];
  hourlyRate: number;
  rating: number;
  reviewCount: number;
  availability: AvailabilityType[];
  calendlyUrl?: string;
  education?: { degree: string; institution: string; year: string }[];
  certifications?: { name: string; issuer: string; year: string }[];
  experience?: { position: string; company: string; period: string; description?: string }[];
  experienceLevels?: string[];
  reviews?: { userName: string; userPicture?: string; rating: number; comment: string; date: string }[];
}

export interface TutorsResponse {
  tutors: Tutor[];
  total: number;
  page: number;
  perPage: number;
  totalPages: number;
} 