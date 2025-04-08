import React from "react";
import Navbar from "@/components/layout/navbar";
import Footer from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";
import { CheckCircle, Users, CalendarClock, CreditCard, BookOpen, Award } from "lucide-react";

export default function HowItWorksPage() {
  const [, navigate] = useLocation();
  
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow bg-gray-50">
        <div className="container mx-auto px-4 py-12">
          {/* Hero section */}
          <div className="text-center mb-16">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">How Tadrees.com Works</h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-2">
              Our peer-to-peer tutoring platform connects students with qualified tutors for personalized learning experiences.
            </p>
            <p className="text-sm text-gray-500">
              Created by SinaMohammadhHosseinZadeh
            </p>
          </div>
          
          {/* Steps section */}
          <div className="max-w-4xl mx-auto mb-16">
            <h2 className="text-2xl font-bold text-center mb-10">Simple Steps to Start Learning</h2>
            
            <div className="grid gap-8 md:grid-cols-3">
              {/* Step 1 */}
              <div className="bg-white p-6 rounded-lg shadow-sm text-center">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Users className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">1. Find a Tutor</h3>
                <p className="text-gray-600">
                  Browse our marketplace of qualified tutors and find the perfect match for your learning needs.
                </p>
              </div>
              
              {/* Step 2 */}
              <div className="bg-white p-6 rounded-lg shadow-sm text-center">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CalendarClock className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">2. Book a Session</h3>
                <p className="text-gray-600">
                  Schedule a tutoring session at a time that works for you, with flexible options.
                </p>
              </div>
              
              {/* Step 3 */}
              <div className="bg-white p-6 rounded-lg shadow-sm text-center">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <BookOpen className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">3. Start Learning</h3>
                <p className="text-gray-600">
                  Connect with your tutor and enjoy personalized instruction tailored to your goals.
                </p>
              </div>
            </div>
          </div>
          
          {/* Features section */}
          <div className="max-w-4xl mx-auto mb-16">
            <h2 className="text-2xl font-bold text-center mb-10">Platform Features</h2>
            
            <div className="space-y-8">
              <div className="flex flex-col md:flex-row items-start bg-white p-6 rounded-lg shadow-sm">
                <div className="flex-shrink-0 mr-6 mb-4 md:mb-0">
                  <Award className="h-12 w-12 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Qualified Tutors</h3>
                  <p className="text-gray-600">
                    Our tutors are experienced professionals and subject matter experts who undergo a thorough vetting process.
                  </p>
                  <ul className="mt-4 space-y-2">
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                      <span>Verified credentials and expertise</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                      <span>Reviewed by students</span>
                    </li>
                  </ul>
                </div>
              </div>
              
              <div className="flex flex-col md:flex-row items-start bg-white p-6 rounded-lg shadow-sm">
                <div className="flex-shrink-0 mr-6 mb-4 md:mb-0">
                  <CalendarClock className="h-12 w-12 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Flexible Scheduling</h3>
                  <p className="text-gray-600">
                    Book sessions at your convenience with our easy-to-use scheduling system.
                  </p>
                  <ul className="mt-4 space-y-2">
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                      <span>24/7 booking availability</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                      <span>Easy rescheduling options</span>
                    </li>
                  </ul>
                </div>
              </div>
              
              <div className="flex flex-col md:flex-row items-start bg-white p-6 rounded-lg shadow-sm">
                <div className="flex-shrink-0 mr-6 mb-4 md:mb-0">
                  <CreditCard className="h-12 w-12 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Secure Payments</h3>
                  <p className="text-gray-600">
                    Our platform ensures secure payment processing for all tutoring sessions.
                  </p>
                  <ul className="mt-4 space-y-2">
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                      <span>Transparent pricing with no hidden fees</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                      <span>Payment only released after session completion</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          
          {/* CTA section */}
          <div className="bg-primary text-white rounded-lg p-10 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to Start Learning?</h2>
            <p className="text-xl mb-6 max-w-3xl mx-auto">
              Join thousands of students who have improved their skills and achieved their goals with Tadrees.com.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Button 
                className="bg-white text-primary hover:bg-gray-100"
                size="lg"
                onClick={() => navigate("/tutors")}
              >
                Find a Tutor
              </Button>
              <Button 
                variant="outline" 
                className="bg-transparent border-white text-white hover:bg-white/10"
                size="lg"
                onClick={() => navigate("/become-tutor")}
              >
                Become a Tutor
              </Button>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
} 