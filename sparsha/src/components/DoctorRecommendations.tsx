import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MapPin, Star, Video, Calendar } from "lucide-react";
import doctorImage from "@/assets/doctor-consultation.jpg";

const doctors = [
  {
    name: "Dr. Sarah Johnson",
    specialty: "Clinical Dermatology",
    rating: 4.9,
    reviews: 324,
    location: "Mumbai, Maharashtra",
    availability: "Available Today",
    teleconsult: true,
  },
  {
    name: "Dr. Rajesh Kumar",
    specialty: "Pediatric Dermatology",
    rating: 4.8,
    reviews: 256,
    location: "Bangalore, Karnataka",
    availability: "Next Available: Tomorrow",
    teleconsult: true,
  },
  {
    name: "Dr. Priya Sharma",
    specialty: "Cosmetic Dermatology",
    rating: 4.9,
    reviews: 412,
    location: "Delhi, NCR",
    availability: "Available This Week",
    teleconsult: false,
  },
];

const DoctorRecommendations = () => {
  return (
    <section id="doctors" className="py-24 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Connect With Expert Dermatologists
          </h2>
          <p className="text-xl text-muted-foreground">
            Get personalized care from qualified specialists recommended based on your condition
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {doctors.map((doctor, index) => (
            <Card key={index} className="border-2 hover:border-primary/50 transition-all duration-300 hover:shadow-lg">
              <CardHeader>
                <div className="w-full h-48 bg-gradient-card rounded-lg mb-4 overflow-hidden">
                  <img 
                    src={doctorImage} 
                    alt={doctor.name}
                    className="w-full h-full object-cover opacity-60"
                  />
                </div>
                <CardTitle className="text-xl">{doctor.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{doctor.specialty}</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 fill-primary text-primary" />
                    <span className="font-semibold">{doctor.rating}</span>
                    <span className="text-sm text-muted-foreground">
                      ({doctor.reviews} reviews)
                    </span>
                  </div>
                  {doctor.teleconsult && (
                    <Badge variant="secondary" className="gap-1">
                      <Video className="h-3 w-3" />
                      Teleconsult
                    </Badge>
                  )}
                </div>

                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <MapPin className="h-4 w-4" />
                  {doctor.location}
                </div>

                <div className="flex items-center gap-2 text-sm">
                  <Calendar className="h-4 w-4 text-primary" />
                  <span className="font-medium">{doctor.availability}</span>
                </div>

                <Button className="w-full">
                  Book Consultation
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="text-center">
          <Button variant="outline" size="lg">
            View All Dermatologists
          </Button>
        </div>
      </div>
    </section>
  );
};

export default DoctorRecommendations;
