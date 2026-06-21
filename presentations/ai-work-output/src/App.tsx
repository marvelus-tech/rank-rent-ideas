import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Header from "./components/layout/Header";
import Hero from "./components/sections/Hero";
import Problem from "./components/sections/Problem";
import Features from "./components/sections/Features";
import ROI from "./components/sections/ROI";
import Testimonials from "./components/sections/Testimonials";
import CTA from "./components/sections/CTA";
import Footer from "./components/layout/Footer";
import NoiseOverlay from "./components/ui/NoiseOverlay";

function App() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="relative min-h-screen bg-navy-950 text-white overflow-x-hidden">
      <NoiseOverlay />
      
      {/* Animated background gradient */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div 
          className="absolute top-0 left-1/4 w-96 h-96 bg-gold-500/10 rounded-full blur-3xl"
          style={{ transform: `translateY(${scrollY * 0.3}px)` }}
        />
        <div 
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-navy-700/30 rounded-full blur-3xl"
          style={{ transform: `translateY(${scrollY * -0.2}px)` }}
        />
      </div>

      <div className="relative z-10">
        <Header />
        <main>
          <Hero />
          <Problem />
          <Features />
          <ROI />
          <Testimonials />
          <CTA />
        </main>
        <Footer />
      </div>
    </div>
  );
}

export default App;