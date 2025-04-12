import { Search, CalendarCheck, GraduationCap } from "lucide-react";

export default function HowItWorks() {
  return (
    <section className="py-16 bg-neutral-50">
      <div className="container mx-auto px-4">
        <h2 className="font-poppins font-semibold text-3xl text-center mb-12">How Tadrees Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-lg p-8 text-center shadow-sm hover:shadow-md transition-shadow duration-200">
            <div className="bg-primary-light bg-opacity-20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
              <Search className="text-primary text-3xl" />
            </div>
            <h3 className="font-poppins font-semibold text-xl mb-4">1. Find a Tutor</h3>
            <p className="text-neutral-700">
              Browse our extensive list of qualified tutors by subject, skill level, or availability.
            </p>
          </div>
          
          <div className="bg-white rounded-lg p-8 text-center shadow-sm hover:shadow-md transition-shadow duration-200">
            <div className="bg-primary-light bg-opacity-20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
              <CalendarCheck className="text-primary text-3xl" />
            </div>
            <h3 className="font-poppins font-semibold text-xl mb-4">2. Book a Session</h3>
            <p className="text-neutral-700">
              Select a convenient time slot from your tutor's availability and make a secure payment.
            </p>
          </div>
          
          <div className="bg-white rounded-lg p-8 text-center shadow-sm hover:shadow-md transition-shadow duration-200">
            <div className="bg-primary-light bg-opacity-20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
              <GraduationCap className="text-primary text-3xl" />
            </div>
            <h3 className="font-poppins font-semibold text-xl mb-4">3. Start Learning</h3>
            <p className="text-neutral-700">
              Connect with your tutor virtually for personalized instruction tailored to your needs.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
