import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, Image as ImageIcon, AlertCircle, CheckCircle, Scan } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const AnalysisUpload = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
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
      simulateAnalysis();
    };
    reader.readAsDataURL(file);
  };

  const simulateAnalysis = () => {
    setAnalyzing(true);
    setTimeout(() => {
      setAnalyzing(false);
      toast({
        title: "Analysis Complete",
        description: "Your skin analysis results are ready. This is a demo interface.",
      });
    }, 2000);
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

        <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8">
          <Card className="border-2">
            <CardHeader>
              <CardTitle>Upload Image</CardTitle>
            </CardHeader>
            <CardContent>
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-12 text-center transition-all duration-300 ${
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
                    >
                      <Upload className="mr-2 h-4 w-4" />
                      Upload Different Image
                    </Button>
                  </div>
                ) : (
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <ImageIcon className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
                    <p className="text-lg font-medium mb-2">
                      Drop your image here or click to upload
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Supports: JPG, PNG, WEBP (Max 10MB)
                    </p>
                  </label>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="border-2">
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
                <div className="space-y-6">
                  <div className="flex items-start gap-3 p-4 rounded-lg bg-accent">
                    <CheckCircle className="h-5 w-5 text-secondary flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold mb-1">Detection: Eczema (Demo)</p>
                      <p className="text-sm text-muted-foreground">
                        Confidence: 94%
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-4 rounded-lg bg-accent">
                    <AlertCircle className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold mb-1">Severity: Moderate</p>
                      <p className="text-sm text-muted-foreground">
                        Recommended: Consult dermatologist
                      </p>
                    </div>
                  </div>

                  <div className="p-4 rounded-lg border border-border">
                    <p className="font-semibold mb-2">Treatment Suggestions:</p>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Apply moisturizer regularly</li>
                      <li>• Avoid irritants and allergens</li>
                      <li>• Consider OTC hydrocortisone</li>
                      <li>• Schedule consultation if worsens</li>
                    </ul>
                  </div>

                  <Button className="w-full" variant="default">
                    Find Dermatologists Near You
                  </Button>
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
