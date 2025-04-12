import { useLocation } from "wouter";
import { Card, CardContent } from "@/components/ui/card";

const subjects = [
  { name: "Mathematics", icon: "functions" },
  { name: "Physics", icon: "science" },
  { name: "Chemistry", icon: "biotech" },
  { name: "Programming", icon: "code" },
  { name: "Languages", icon: "language" },
  { name: "History", icon: "history_edu" },
];

export default function FeaturedSubjects() {
  const [, navigate] = useLocation();

  const handleClick = (subject: string) => {
    navigate(`/tutors?subject=${subject.toLowerCase()}`);
  };

  return (
    <section className="py-16 bg-white">
      <div className="container mx-auto px-4">
        <h2 className="font-poppins font-semibold text-3xl text-center mb-12">Popular Subjects</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {subjects.map((subject, index) => (
            <Card 
              key={index}
              className="bg-neutral-50 hover:bg-primary hover:text-white text-neutral-900 transition duration-300 cursor-pointer border-none shadow-sm hover:shadow-md"
              onClick={() => handleClick(subject.name)}
            >
              <CardContent className="p-6 flex flex-col items-center justify-center text-center">
                <span className="material-icons text-4xl mb-2">{subject.icon}</span>
                <h3 className="font-medium">{subject.name}</h3>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
