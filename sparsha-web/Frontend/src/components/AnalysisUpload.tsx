import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, Image as ImageIcon, AlertCircle, CheckCircle, Scan } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

// Component to display structured treatment advice
const TreatmentAdviceDisplay = ({ advice }: { advice: any }) => {
  const [activeTab, setActiveTab] = useState("overview");
  
  // Handle both JSON object and string (for backward compatibility)
  let adviceData = advice;
  if (typeof advice === 'string') {
    try {
      adviceData = JSON.parse(advice);
    } catch {
      // If it's not JSON, return fallback display
      return (
        <div className="p-4 rounded-lg border border-border">
          <p className="text-sm text-muted-foreground">{advice}</p>
        </div>
      );
    }
  }

  return (
    <div className="w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 p-4 bg-gradient-to-r from-primary/10 to-secondary/10 rounded-t-lg border-b-2 border-primary/20">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🤖</span>
          <div>
            <p className="font-bold text-lg text-primary">AI-Powered Treatment Advice</p>
            <p className="text-xs text-muted-foreground">Comprehensive guidance powered by Gemini AI</p>
          </div>
        </div>
        <Badge variant="secondary" className="text-sm px-3 py-1">
          Powered by Gemini AI
        </Badge>
      </div>

      {/* Tabs Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4 h-12 mb-4">
          <TabsTrigger value="overview" className="text-sm">Overview</TabsTrigger>
          <TabsTrigger value="treatment" className="text-sm">Treatment</TabsTrigger>
          <TabsTrigger value="doctor" className="text-sm">When to See Doctor</TabsTrigger>
          <TabsTrigger value="guidelines" className="text-sm">Guidelines</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          {adviceData.about && (
            <Card>
              <CardContent className="p-6">
                <h3 className="font-bold text-lg text-foreground mb-3">About This Condition</h3>
                <div className="space-y-3">
                  <div>
                    <p className="font-medium text-foreground mb-1">What is it?</p>
                    <p className="text-muted-foreground leading-relaxed">{adviceData.about.description}</p>
                  </div>
                  <div>
                    <p className="font-medium text-foreground mb-1">How common is it?</p>
                    <p className="text-muted-foreground leading-relaxed">{adviceData.about.commonality}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Treatment Options Tab */}
        <TabsContent value="treatment" className="space-y-4">
          {adviceData.treatment_options && (
            <div className="grid lg:grid-cols-2 gap-4">
              {adviceData.treatment_options.over_the_counter && adviceData.treatment_options.over_the_counter.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Over-the-Counter</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {adviceData.treatment_options.over_the_counter.map((item: string, i: number) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-primary mt-1">•</span>
                          <span className="text-sm text-muted-foreground flex-1">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
              
              {adviceData.treatment_options.prescription && adviceData.treatment_options.prescription.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Prescription Treatments</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {adviceData.treatment_options.prescription.map((item: string, i: number) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-primary mt-1">•</span>
                          <span className="text-sm text-muted-foreground flex-1">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
              
              {adviceData.treatment_options.home_care && adviceData.treatment_options.home_care.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Home Care Tips</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {adviceData.treatment_options.home_care.map((item: string, i: number) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-primary mt-1">•</span>
                          <span className="text-sm text-muted-foreground flex-1">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
              
              {adviceData.treatment_options.lifestyle && adviceData.treatment_options.lifestyle.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Lifestyle Changes</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {adviceData.treatment_options.lifestyle.map((item: string, i: number) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-primary mt-1">•</span>
                          <span className="text-sm text-muted-foreground flex-1">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </TabsContent>

        {/* When to See Doctor Tab */}
        <TabsContent value="doctor" className="space-y-4">
          {adviceData.when_to_see_doctor && (
            <Card>
              <CardContent className="p-6">
                <h3 className="font-bold text-lg text-foreground mb-4">When to See a Doctor</h3>
                {adviceData.when_to_see_doctor.warning_signs && adviceData.when_to_see_doctor.warning_signs.length > 0 && (
                  <div className="mb-4">
                    <p className="font-semibold text-foreground mb-3">Warning Signs:</p>
                    <div className="grid md:grid-cols-2 gap-3">
                      {adviceData.when_to_see_doctor.warning_signs.map((sign: string, i: number) => (
                        <div key={i} className="flex items-start gap-2 p-3 bg-red-50 border border-red-100 rounded-lg">
                          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-red-900">{sign}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {adviceData.when_to_see_doctor.urgency && (
                  <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                    <p className="font-medium text-orange-900 mb-1">Urgency:</p>
                    <p className="text-sm text-orange-800">{adviceData.when_to_see_doctor.urgency}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Guidelines Tab (Do's and Don'ts) */}
        <TabsContent value="guidelines" className="space-y-4">
          {adviceData.dos_and_donts && (
            <div className="grid lg:grid-cols-2 gap-6">
              {adviceData.dos_and_donts.dos && adviceData.dos_and_donts.dos.length > 0 && (
                <Card className="border-green-200 bg-green-50/50">
                  <CardHeader>
                    <CardTitle className="text-base text-green-800 flex items-center gap-2">
                      <CheckCircle className="h-5 w-5" />
                      Do's
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3">
                      {adviceData.dos_and_donts.dos.map((item: string, i: number) => (
                        <li key={i} className="flex items-start gap-3">
                          <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-green-900 flex-1 leading-relaxed">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
              
              {adviceData.dos_and_donts.donts && adviceData.dos_and_donts.donts.length > 0 && (
                <Card className="border-red-200 bg-red-50/50">
                  <CardHeader>
                    <CardTitle className="text-base text-red-800 flex items-center gap-2">
                      <AlertCircle className="h-5 w-5" />
                      Don'ts
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3">
                      {adviceData.dos_and_donts.donts.map((item: string, i: number) => (
                        <li key={i} className="flex items-start gap-3">
                          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-red-900 flex-1 leading-relaxed">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Disclaimer */}
      <div className="mt-6 p-4 bg-yellow-50 border-2 border-yellow-200 rounded-lg">
        <p className="text-sm text-yellow-900">
          <strong>⚠️ Disclaimer:</strong> This is educational information only. Always consult a dermatologist for proper diagnosis and treatment.
        </p>
      </div>
    </div>
  );
};

const AnalysisUpload = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const { toast } = useToast();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      handleImageUpload(file);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleImageUpload(file);
    }
  };

  const handleImageUpload = (file: File) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      setUploadedImage(reader.result as string);
      setSelectedFile(file);
      performAnalysis(file);
    };
    reader.readAsDataURL(file);
  };

  const performAnalysis = async (file: File) => {
    setAnalyzing(true);
    setAnalysisResult(null);
    try {
      const fd = new FormData();
      fd.append("image", file);

      const res = await fetch("/api/analyze", {
        method: "POST",
        body: fd,
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || "Analysis failed");
      }

      setAnalysisResult(data.analysis);
      toast({
        title: "Analysis Complete",
        description: "Your skin analysis results are ready.",
      });
    } catch (err: any) {
      console.error(err);
      toast({
        title: "Analysis Error",
        description: err?.message || "Unable to analyze image",
      });
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <section id="analysis" className="py-24 bg-gradient-card">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Try Skin Analysis
          </h2>
          <p className="text-xl text-muted-foreground">
            Upload an image to see our AI-powered analysis in action
          </p>
        </div>

        {/* Upload and Quick Results Section */}
        <div className="max-w-7xl mx-auto grid lg:grid-cols-3 gap-6 mb-8">
          {/* Upload Section - Takes 1 column */}
          <Card className="border-2 lg:col-span-1">
            <CardHeader>
              <CardTitle>Upload Image</CardTitle>
            </CardHeader>
            <CardContent>
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${
                  isDragging
                    ? "border-primary bg-accent"
                    : "border-border hover:border-primary"
                }`}
              >
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileInput}
                  className="hidden"
                  id="file-upload"
                />
                
                {uploadedImage ? (
                  <div className="space-y-4">
                    <img
                      src={uploadedImage}
                      alt="Uploaded"
                      className="w-full h-48 object-cover rounded-lg"
                    />
                    <Button
                      variant="outline"
                      onClick={() => document.getElementById('file-upload')?.click()}
                      className="w-full"
                      size="sm"
                    >
                      <Upload className="mr-2 h-4 w-4" />
                      Change Image
                    </Button>
                  </div>
                ) : (
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <ImageIcon className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
                    <p className="text-base font-medium mb-2">
                      Drop image or click to upload
                    </p>
                    <p className="text-xs text-muted-foreground">
                      JPG, PNG, WEBP (Max 10MB)
                    </p>
                  </label>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Quick Results Section - Takes 2 columns */}
          <Card className="border-2 lg:col-span-2">
            <CardHeader>
              <CardTitle>Analysis Results</CardTitle>
            </CardHeader>
            <CardContent>
              {analyzing ? (
                <div className="flex flex-col items-center justify-center h-64 space-y-4">
                  <div className="animate-spin rounded-full h-16 w-16 border-4 border-primary border-t-transparent" />
                  <p className="text-muted-foreground">Analyzing image...</p>
                </div>
              ) : uploadedImage ? (
                <div className="space-y-4">
                  {analysisResult ? (
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="flex items-start gap-3 p-4 rounded-lg bg-green-50 border border-green-200">
                        <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <p className="font-semibold mb-1 text-green-900">Detection: {analysisResult.disease}</p>
                          <p className="text-sm text-green-700">
                            Confidence: {analysisResult.confidence}%
                          </p>
                          {analysisResult.method && (
                            <p className="text-xs text-green-600 mt-1">
                              Method: {analysisResult.method === "ml_model" ? "AI Model" : "Fallback"}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="flex items-start gap-3 p-4 rounded-lg bg-orange-50 border border-orange-200">
                        <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <p className="font-semibold mb-1 text-orange-900">Severity: {analysisResult.severity}</p>
                          <p className="text-sm text-orange-700">
                            Consult dermatologist
                          </p>
                          {analysisResult.confidence_level && (
                            <p className="text-xs text-orange-600 mt-1">
                              Level: {analysisResult.confidence_level}
                            </p>
                          )}
                          {analysisResult.recommend_urgent_care && (
                            <div className="mt-2 p-2 bg-red-100 border border-red-300 rounded text-xs text-red-900 font-medium">
                              ⚠️ Urgent care recommended
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-4 rounded-lg border border-border text-center">
                      <p className="text-sm text-muted-foreground">Analysis result will appear here.</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-center space-y-4">
                  <Scan className="h-16 w-16 text-muted-foreground" />
                  <p className="text-muted-foreground">
                    Upload an image to see analysis results
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Full-Width Treatment Advice Section */}
        {analysisResult && analysisResult.treatment_advice && (
          <div className="max-w-7xl mx-auto">
            <Card className="border-2">
              <CardContent className="p-6">
                <TreatmentAdviceDisplay advice={analysisResult.treatment_advice} />
              </CardContent>
            </Card>
          </div>
        )}

        {/* Fallback Treatment Suggestions */}
        {analysisResult && !analysisResult.treatment_advice && analysisResult.suggestions && (
          <div className="max-w-7xl mx-auto">
            <Card className="border-2">
              <CardHeader>
                <CardTitle>Treatment Suggestions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  <ul className="space-y-2">
                    {analysisResult.suggestions.slice(0, Math.ceil(analysisResult.suggestions.length / 2)).map((s: string, i: number) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-primary mt-1">•</span>
                        <span className="text-sm text-muted-foreground">{s}</span>
                      </li>
                    ))}
                  </ul>
                  <ul className="space-y-2">
                    {analysisResult.suggestions.slice(Math.ceil(analysisResult.suggestions.length / 2)).map((s: string, i: number) => (
                      <li key={i + Math.ceil(analysisResult.suggestions.length / 2)} className="flex items-start gap-2">
                        <span className="text-primary mt-1">•</span>
                        <span className="text-sm text-muted-foreground">{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <p className="text-xs text-muted-foreground mt-4 italic text-center">
                  Note: AI-powered treatment advice is not available. Please consult a dermatologist.
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Action Button */}
        {analysisResult && (
          <div className="max-w-7xl mx-auto mt-6">
            <Button 
              className="w-full" 
              size="lg"
              onClick={() => {
                const el = document.getElementById('doctors');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Find Dermatologists Near You
            </Button>
          </div>
        )}

        <div className="mt-8 text-center text-sm text-muted-foreground max-w-2xl mx-auto">
          <p>
            <strong>Note:</strong> This is a demonstration interface. In production, 
            the system uses trained CNN models for accurate disease detection and severity assessment.
          </p>
        </div>
      </div>
    </section>
  );
};

export default AnalysisUpload;
