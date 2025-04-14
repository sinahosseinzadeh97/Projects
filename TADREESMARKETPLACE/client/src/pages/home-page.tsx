import { useAuth } from "@/hooks/use-auth";
import Navbar from "@/components/layout/navbar";
import Footer from "@/components/layout/footer";
import HeroSection from "@/components/home/hero-section";
import FeaturedSubjects from "@/components/home/featured-subjects";
import HowItWorks from "@/components/home/how-it-works";
import TopTutors from "@/components/home/top-tutors";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <HeroSection />
        <FeaturedSubjects />
        <HowItWorks />
        <TopTutors />
      </main>
      <Footer />
    </div>
  );
}
