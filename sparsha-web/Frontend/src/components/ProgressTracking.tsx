import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, Calendar, Camera, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";

interface ProgressData {
  overall_improvement: number;
  days_tracked: number;
  check_ins: number;
  recent_analyses: Array<{
    id: string;
    date: string;
    disease: string;
    severity: string;
    confidence: number;
    image: string;
    timestamp: string;
  }>;
  improvements: Array<{
    metric: string;
    improvement: number;
  }>;
}

const ProgressTracking = () => {
  const [progressData, setProgressData] = useState<ProgressData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/progress")
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setProgressData(data);
        }
      })
      .catch((err) => {
        console.error("Error fetching progress:", err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleAddCheckIn = () => {
    // Scroll to analysis section
    const el = document.getElementById("analysis");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  const improvement = progressData?.overall_improvement || 0;
  const daysTracked = progressData?.days_tracked || 0;
  const checkIns = progressData?.check_ins || 0;
  const recentAnalyses = progressData?.recent_analyses || [];
  const improvements = progressData?.improvements || [];

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
                {loading ? (
                  <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent" />
                  </div>
                ) : (
                  <>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Overall Improvement</span>
                        <span className="text-2xl font-bold text-secondary">
                          {improvement.toFixed(0)}%
                        </span>
                      </div>
                      <div className="w-full bg-accent rounded-full h-3">
                        <div
                          className="bg-gradient-primary h-3 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(100, improvement)}%` }}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 rounded-lg bg-accent">
                        <div className="text-2xl font-bold text-primary">{daysTracked}</div>
                        <div className="text-sm text-muted-foreground">Days Tracked</div>
                      </div>
                      <div className="p-4 rounded-lg bg-accent">
                        <div className="text-2xl font-bold text-primary">{checkIns}</div>
                        <div className="text-sm text-muted-foreground">Check-ins</div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      {improvements.map((imp, index) => (
                        <div
                          key={index}
                          className="flex items-center gap-3 p-3 rounded-lg bg-background border border-border"
                        >
                          <CheckCircle className="h-5 w-5 text-secondary" />
                          <div className="flex-1">
                            <p className="text-sm font-medium">{imp.metric}</p>
                            <p className="text-xs text-muted-foreground">
                              {imp.improvement.toFixed(0)}% improvement
                            </p>
                          </div>
                        </div>
                      ))}
                      {improvements.length === 0 && (
                        <div className="flex items-center gap-3 p-3 rounded-lg bg-background border border-border">
                          <TrendingUp className="h-5 w-5 text-primary" />
                          <div className="flex-1">
                            <p className="text-sm font-medium">Healing On Track</p>
                            <p className="text-xs text-muted-foreground">
                              Continue monitoring your progress
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                )}
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
                {loading ? (
                  <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent" />
                  </div>
                ) : (
                  <>
                    <div className="space-y-3">
                      {recentAnalyses.length > 0 ? (
                        recentAnalyses.map((analysis) => (
                          <div
                            key={analysis.id}
                            className="p-4 rounded-lg bg-accent space-y-2"
                          >
                            <div className="flex justify-between items-center">
                              <span className="font-medium">{analysis.date}</span>
                              <span
                                className={`text-xs px-2 py-1 rounded-full ${
                                  analysis.severity === "Mild" ||
                                  analysis.severity === "Low"
                                    ? "bg-secondary/20 text-secondary"
                                    : "bg-primary/20 text-primary"
                                }`}
                              >
                                {analysis.severity}
                              </span>
                            </div>
                            <p className="text-sm text-muted-foreground">
                              {analysis.disease} - {analysis.confidence.toFixed(0)}% confidence
                            </p>
                            {analysis.image && (
                              <div className="flex gap-2">
                                <img
                                  src={analysis.image}
                                  alt={analysis.disease}
                                  className="w-16 h-16 rounded bg-gradient-card border border-border object-cover"
                                  onError={(e) => {
                                    (e.target as HTMLImageElement).style.display = "none";
                                  }}
                                />
                              </div>
                            )}
                          </div>
                        ))
                      ) : (
                        <div className="p-4 rounded-lg bg-accent text-center text-muted-foreground">
                          <p>No analyses yet. Upload an image to start tracking!</p>
                        </div>
                      )}
                    </div>

                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={handleAddCheckIn}
                    >
                      <Camera className="mr-2 h-4 w-4" />
                      Add New Check-in
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProgressTracking;
