import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { MapPin, Star, Video, Calendar, Search, Loader2 } from "lucide-react";
import doctorImage from "@/assets/doctor-consultation.jpg";
import { useToast } from "@/hooks/use-toast";

import { useEffect, useState } from "react";

const DoctorRecommendations = () => {
  const [doctors, setDoctors] = useState<any[]>([]);
  const [location, setLocation] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [userLocation, setUserLocation] = useState<string>("");
  const { toast } = useToast();

  // Get user's location on component mount
  useEffect(() => {
    // Try to get user's location from browser geolocation
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          // Reverse geocoding - convert coordinates to location name
          // For now, we'll just use a generic message
          setUserLocation("Your location");
          toast({
            title: "Location detected",
            description: "You can search for nearby doctors",
          });
        },
        (error) => {
          console.log("Geolocation error:", error);
          // User denied location or error occurred
        }
      );
    }
  }, [toast]);

  // Fetch doctors when location changes
  const fetchDoctors = async (searchLocation?: string) => {
    setLoading(true);
    try {
      const loc = searchLocation || location || userLocation;
      const url = loc ? `/api/doctors?location=${encodeURIComponent(loc)}` : "/api/doctors";
      
      const res = await fetch(url);
      const data = await res.json();
      
      if (data && data.success && Array.isArray(data.doctors)) {
        setDoctors(data.doctors);
        if (data.source === "google_places" && data.location_used) {
          toast({
            title: "Doctors found",
            description: `Found ${data.doctors.length} dermatologists near ${data.location_used}`,
          });
        }
      } else {
        throw new Error("Invalid response from server");
      }
    } catch (err: any) {
      console.error("Error fetching doctors:", err);
      toast({
        title: "Error",
        description: err?.message || "Could not fetch doctors. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch on mount
  useEffect(() => {
    fetchDoctors();
  }, []);

  const handleSearch = () => {
    if (location.trim()) {
      fetchDoctors(location);
    } else {
      toast({
        title: "Location required",
        description: "Please enter a location to search for doctors",
        variant: "destructive",
      });
    }
  };

  const handleUseMyLocation = () => {
    if (navigator.geolocation) {
      setLoading(true);
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          // Use coordinates to search (Google Places API accepts lat,lng)
          const locString = `${latitude},${longitude}`;
          await fetchDoctors(locString);
          setLocation(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
        },
        (error) => {
          console.error("Geolocation error:", error);
          toast({
            title: "Location error",
            description: "Could not get your location. Please enter manually.",
            variant: "destructive",
          });
          setLoading(false);
        }
      );
    } else {
      toast({
        title: "Not supported",
        description: "Geolocation is not supported by your browser",
        variant: "destructive",
      });
    }
  };
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

        {/* Location Search */}
        <div className="max-w-2xl mx-auto mb-8">
          <Card className="border-2">
            <CardContent className="p-6">
              <div className="flex gap-2">
                <div className="flex-1">
                  <Input
                    type="text"
                    placeholder="Enter city or address (e.g., Bangalore, Karnataka)"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleSearch();
                      }
                    }}
                    className="w-full"
                  />
                </div>
                <Button onClick={handleSearch} disabled={loading}>
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4 mr-2" />
                  )}
                  Search
                </Button>
                <Button variant="outline" onClick={handleUseMyLocation} disabled={loading}>
                  <MapPin className="h-4 w-4 mr-2" />
                  Use My Location
                </Button>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                Enter your location to find nearby dermatologists
              </p>
            </CardContent>
          </Card>
        </div>

        {loading && doctors.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
            <p className="ml-4 text-muted-foreground">Searching for doctors...</p>
          </div>
        ) : doctors.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground mb-4">No doctors found. Try searching with a different location.</p>
            <Button onClick={() => fetchDoctors()}>Retry</Button>
          </div>
        ) : (
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
        )}

        {doctors.length > 0 && (
          <div className="text-center">
            <Button variant="outline" size="lg" onClick={() => fetchDoctors(location)}>
              Refresh Results
            </Button>
          </div>
        )}
      </div>
    </section>
  );
};

export default DoctorRecommendations;
