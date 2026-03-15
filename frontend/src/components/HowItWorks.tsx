import { Upload, Scan, FileText, UserCheck } from "lucide-react";

const steps = [
  {
    icon: Upload,
    title: "Upload Image",
    description: "Take or upload a clear photo of the affected skin area",
    step: "01",
  },
  {
    icon: Scan,
    title: "AI Analysis",
    description: "Our AI analyzes the image and detects potential conditions",
    step: "02",
  },
  {
    icon: FileText,
    title: "Get Results",
    description: "Receive detailed diagnosis, severity level, and treatment plan",
    step: "03",
  },
  {
    icon: UserCheck,
    title: "Consult Doctor",
    description: "Connect with recommended specialists for professional care",
    step: "04",
  },
];

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="py-24 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            How Sparsh Works
          </h2>
          <p className="text-xl text-muted-foreground">
            Simple, fast, and accurate skin health analysis in four easy steps
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={index} className="relative">
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-16 left-[60%] w-full h-0.5 bg-gradient-to-r from-primary to-secondary" />
                )}
                
                <div className="text-center space-y-4 relative z-10">
                  <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-primary shadow-glow mx-auto">
                    <Icon className="h-12 w-12 text-primary-foreground" />
                  </div>
                  
                  <div className="absolute top-0 right-0 text-6xl font-bold text-accent opacity-20">
                    {step.step}
                  </div>
                  
                  <h3 className="text-2xl font-semibold">{step.title}</h3>
                  <p className="text-muted-foreground">{step.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
