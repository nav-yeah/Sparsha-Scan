import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, Calendar, Camera, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

const ProgressTracking = () => {
  return (
    <section className="py-24 bg-gradient-card">
      <div className="container mx-auto px-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Track Your Healing Journey
            </h2>
            <p className="text-xl text-muted-foreground">
              Monitor improvements over time with visual comparisons and trend analysis
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <Card className="border-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  Progress Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Overall Improvement</span>
                    <span className="text-2xl font-bold text-secondary">78%</span>
                  </div>
                  <div className="w-full bg-accent rounded-full h-3">
                    <div className="bg-gradient-primary h-3 rounded-full" style={{ width: '78%' }} />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-accent">
                    <div className="text-2xl font-bold text-primary">12</div>
                    <div className="text-sm text-muted-foreground">Days Tracked</div>
                  </div>
                  <div className="p-4 rounded-lg bg-accent">
                    <div className="text-2xl font-bold text-primary">6</div>
                    <div className="text-sm text-muted-foreground">Check-ins</div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-background border border-border">
                    <CheckCircle className="h-5 w-5 text-secondary" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Redness Reduced</p>
                      <p className="text-xs text-muted-foreground">65% improvement</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-background border border-border">
                    <CheckCircle className="h-5 w-5 text-secondary" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Inflammation Down</p>
                      <p className="text-xs text-muted-foreground">82% improvement</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-background border border-border">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Healing On Track</p>
                      <p className="text-xs text-muted-foreground">Expected recovery: 5 days</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-primary" />
                  Recent Check-ins
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  {[
                    { date: "Today", status: "Significant improvement", severity: "Mild" },
                    { date: "3 days ago", status: "Slight improvement", severity: "Moderate" },
                    { date: "6 days ago", status: "Initial scan", severity: "Moderate" },
                  ].map((checkin, index) => (
                    <div key={index} className="p-4 rounded-lg bg-accent space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{checkin.date}</span>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          checkin.severity === "Mild" 
                            ? "bg-secondary/20 text-secondary" 
                            : "bg-primary/20 text-primary"
                        }`}>
                          {checkin.severity}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">{checkin.status}</p>
                      <div className="flex gap-2">
                        <div className="w-16 h-16 rounded bg-gradient-card border border-border" />
                        <div className="w-16 h-16 rounded bg-gradient-card border border-border" />
                      </div>
                    </div>
                  ))}
                </div>

                <Button variant="outline" className="w-full">
                  <Camera className="mr-2 h-4 w-4" />
                  Add New Check-in
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProgressTracking;
