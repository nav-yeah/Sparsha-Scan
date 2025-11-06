import Header from "@/components/Header";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import HowItWorks from "@/components/HowItWorks";
import AnalysisUpload from "@/components/AnalysisUpload";
import DoctorRecommendations from "@/components/DoctorRecommendations";
import ProgressTracking from "@/components/ProgressTracking";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Header />
      <Hero />
      <Features />
      <HowItWorks />
      <AnalysisUpload />
      <ProgressTracking />
      <DoctorRecommendations />
      <Footer />
    </div>
  );
};

export default Index;
