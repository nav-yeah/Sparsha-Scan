import { Card, CardContent } from "@/components/ui/card";
import { Scan, Activity, Brain, Stethoscope, TrendingUp, Shield } from "lucide-react";

const features = [
  {
    icon: Scan,
    title: "AI Disease Detection",
    description: "Upload an image and let our advanced CNN models identify skin conditions with medical-grade accuracy.",
  },
  {
    icon: Activity,
    title: "Severity Assessment",
    description: "Get instant severity grading - mild, moderate, or severe - to understand the urgency of your condition.",
  },
  {
    icon: Brain,
    title: "Explainable AI",
    description: "See exactly which areas influenced the diagnosis with Grad-CAM heatmap visualizations for transparency.",
  },
  {
    icon: Stethoscope,
    title: "Treatment Guidance",
    description: "Receive medically-informed treatment suggestions tailored to your detected condition and severity.",
  },
  {
    icon: TrendingUp,
    title: "Progress Tracking",
    description: "Monitor your skin health journey with visual comparisons and trend analysis over time.",
  },
  {
    icon: Shield,
    title: "Doctor Recommendations",
    description: "Connect with qualified dermatologists based on your condition, location, and urgency level.",
  },
];

const Features = () => {
  return (
    <section id="features" className="py-24 bg-gradient-card">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Comprehensive Skin Health Solutions
          </h2>
          <p className="text-xl text-muted-foreground">
            Everything you need for early detection, accurate diagnosis, and effective treatment guidance
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card
                key={index}
                className="border-2 hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
              >
                <CardContent className="p-6 space-y-4">
                  <div className="w-12 h-12 rounded-lg bg-accent flex items-center justify-center">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Features;
