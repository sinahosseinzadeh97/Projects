import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { apiRequest } from "@/lib/queryClient";
import Navbar from "@/components/layout/navbar";
import Footer from "@/components/layout/footer";
import TutorFilters from "@/components/tutors/tutor-filters";
import TutorCard from "@/components/tutors/tutor-card";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { Pagination, PaginationContent, PaginationEllipsis, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination";

// Define types for the tutor and tutors response
interface AvailabilityType {
  day: string;
  time: string;
}

interface Tutor {
  id: number;
  user: {
    name: string;
    profilePicture: string | null;
  };
  headline: string;
  shortBio: string;
  hourlyRate: number;
  subjects: string[];
  rating: number;
  reviewCount: number;
  availability: AvailabilityType[];
}

interface TutorsResponse {
  items: Tutor[];
  total: number;
  totalPages: number;
}

export default function TutorListPage() {
  const [, navigate] = useLocation();
  const [searchTerm, setSearchTerm] = useState("");
  const [subject, setSubject] = useState<string>("");
  const [priceRange, setPriceRange] = useState<{ min: string; max: string }>({ min: "", max: "" });
  const [availability, setAvailability] = useState<string[]>([]);
  const [sort, setSort] = useState("relevance");
  const [currentPage, setCurrentPage] = useState(1);
  
  // Fetch tutors with filters
  const { data: tutors, isLoading, error } = useQuery<TutorsResponse>({
    queryKey: ["/api/tutors", { subject, priceMin: priceRange.min, priceMax: priceRange.max, availability, sort, page: currentPage, search: searchTerm }],
    queryFn: async () => {
      const params = new URLSearchParams();
      
      if (subject) params.append("subject", subject);
      if (priceRange.min) params.append("priceMin", priceRange.min);
      if (priceRange.max) params.append("priceMax", priceRange.max);
      if (availability.length > 0) {
        availability.forEach(day => params.append("availability", day));
      }
      if (sort) params.append("sort", sort);
      if (currentPage) params.append("page", currentPage.toString());
      if (searchTerm) params.append("search", searchTerm);
      
      const queryString = params.toString();
      const url = `/api/tutors${queryString ? `?${queryString}` : ''}`;
      
      const response = await apiRequest("GET", url);
      return response.json();
    }
  });

  const handleFilter = (filters: { 
    searchTerm?: string, 
    subject?: string, 
    priceRange: { min?: string; max?: string }, 
    availability?: string[] 
  }) => {
    setSearchTerm(filters.searchTerm || "");
    setSubject(filters.subject === "all" ? "" : (filters.subject || ""));
    setPriceRange({ 
      min: filters.priceRange.min || "", 
      max: filters.priceRange.max || "" 
    });
    setAvailability(filters.availability || []);
    setCurrentPage(1);
  };

  const handleReset = () => {
    setSearchTerm("");
    setSubject("");  // Empty for API query but select will show "all"
    setPriceRange({ min: "", max: "" });
    setAvailability([]);
    setCurrentPage(1);
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSort(e.target.value);
  };

  const handleTutorClick = (tutorId: number) => {
    navigate(`/tutor/${tutorId}`);
  };

  const totalPages = tutors?.totalPages || 1;

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row gap-6">
            {/* Filters sidebar */}
            <div className="w-full md:w-1/4">
              <TutorFilters
                onFilter={handleFilter}
                onReset={handleReset}
                initialValues={{
                  searchTerm,
                  subject,
                  priceRange,
                  availability,
                }}
              />
            </div>

            {/* Tutor listings */}
            <div className="w-full md:w-3/4">
              <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
                <div className="flex justify-between items-center">
                  <h2 className="font-poppins font-semibold text-2xl">
                    {isLoading ? "Loading tutors..." : `Tutors (${tutors?.total || 0})`}
                  </h2>
                  <div className="flex items-center">
                    <label className="text-neutral-dark mr-2 text-sm">Sort by:</label>
                    <select
                      className="border border-neutral-200 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                      value={sort}
                      onChange={handleSortChange}
                    >
                      <option value="relevance">Relevance</option>
                      <option value="price-low">Price: Low to High</option>
                      <option value="price-high">Price: High to Low</option>
                      <option value="rating">Rating</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Tutor list */}
              {isLoading ? (
                <div className="flex justify-center items-center h-64">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : error ? (
                <div className="bg-red-50 text-red-500 p-4 rounded-lg text-center">
                  Error loading tutors. Please try again.
                </div>
              ) : tutors?.items.length === 0 ? (
                <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                  <h3 className="text-xl font-medium mb-2">No tutors found</h3>
                  <p className="text-neutral-600 mb-4">Try adjusting your filters to find available tutors.</p>
                  <Button onClick={handleReset}>Reset Filters</Button>
                </div>
              ) : (
                <div className="space-y-6">
                  {tutors?.items.map((tutor: Tutor) => (
                    <TutorCard
                      key={tutor.id}
                      tutor={{
                        id: tutor.id,
                        name: tutor.user.name,
                        profilePicture: tutor.user.profilePicture || undefined,
                        headline: tutor.headline,
                        bio: tutor.shortBio,
                        subjects: tutor.subjects,
                        hourlyRate: tutor.hourlyRate,
                        rating: tutor.rating,
                        reviewCount: tutor.reviewCount,
                        availability: tutor.availability,
                      }}
                      onClick={() => handleTutorClick(tutor.id)}
                    />
                  ))}

                  {/* Pagination */}
                  {totalPages > 1 && (
                    <Pagination className="mt-8">
                      <PaginationContent>
                        <PaginationItem>
                          <PaginationPrevious
                            href="#"
                            onClick={(e) => {
                              e.preventDefault();
                              if (currentPage > 1) setCurrentPage(currentPage - 1);
                            }}
                            className={currentPage === 1 ? "pointer-events-none opacity-50" : ""}
                          />
                        </PaginationItem>
                        
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                          const pageNum = i + 1;
                          return (
                            <PaginationItem key={pageNum}>
                              <PaginationLink
                                href="#"
                                onClick={(e) => {
                                  e.preventDefault();
                                  setCurrentPage(pageNum);
                                }}
                                isActive={currentPage === pageNum}
                              >
                                {pageNum}
                              </PaginationLink>
                            </PaginationItem>
                          );
                        })}
                        
                        {totalPages > 5 && (
                          <>
                            <PaginationItem>
                              <PaginationEllipsis />
                            </PaginationItem>
                            <PaginationItem>
                              <PaginationLink
                                href="#"
                                onClick={(e) => {
                                  e.preventDefault();
                                  setCurrentPage(totalPages);
                                }}
                                isActive={currentPage === totalPages}
                              >
                                {totalPages}
                              </PaginationLink>
                            </PaginationItem>
                          </>
                        )}
                        
                        <PaginationItem>
                          <PaginationNext
                            href="#"
                            onClick={(e) => {
                              e.preventDefault();
                              if (currentPage < totalPages) setCurrentPage(currentPage + 1);
                            }}
                            className={currentPage === totalPages ? "pointer-events-none opacity-50" : ""}
                          />
                        </PaginationItem>
                      </PaginationContent>
                    </Pagination>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
