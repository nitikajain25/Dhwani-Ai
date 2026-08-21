import React, { useState, useEffect, useRef } from 'react';
import gsap from 'gsap';

import BackgroundArtwork from './components/BackgroundArtwork';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import VoiceInputSection from './components/VoiceInputSection';
import ResponseQueueSection from './components/ResponseQueueSection';
import LatencyDashboard from './components/LatencyDashboard';
import Footer from './components/Footer';

export default function DhwaniAI() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const heroRef = useRef(null);
  const voiceRef = useRef(null);
  const queueRef = useRef(null);
  const metricsRef = useRef(null);

  useEffect(() => {
    // GSAP Entrance Animations
    const ctx = gsap.context(() => {
      gsap.fromTo(
        '.hero-animate',
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 1, stagger: 0.2, ease: 'power3.out' }
      );
    }, heroRef);

    return () => ctx.revert();
  }, []);

  return (
    <div className="bg-[#0a1422] text-[#d9e3f7] font-['Hanken_Grotesk',sans-serif] min-h-screen overflow-x-hidden relative selection:bg-[#25d9f5] selection:text-[#00363e]">
      {/* Background SVG Artwork */}
      <BackgroundArtwork />

      {/* Navigation Bar & Mobile Menu */}
      <Navbar mobileMenuOpen={mobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen} />

      {/* Main Page Layout */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <main className="flex-grow flex flex-col items-center justify-start w-full relative">
          {/* Section 1: Hero Section */}
          <HeroSection heroRef={heroRef} />

          {/* Section 2: Voice Input Section */}
          <VoiceInputSection voiceRef={voiceRef} />

          {/* Section 3: Response Queue Section */}
          <ResponseQueueSection queueRef={queueRef} />

          {/* Section 4: Latency Dashboard */}
          <LatencyDashboard metricsRef={metricsRef} />

          {/* Section 5: Footer */}
          <Footer />
        </main>
      </div>
    </div>
  );
}
