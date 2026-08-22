import React, { useState, useEffect } from 'react';
import { ExpandableTabs } from './ui/expandable-tabs';

export default function Navbar({ mobileMenuOpen, setMobileMenuOpen }) {
  const [activeTab, setActiveTab] = useState('#hero');

  useEffect(() => {
    const handleHashChange = () => {
      setActiveTab(window.location.hash || '#hero');
    };
    handleHashChange(); // Set initial
    window.addEventListener('hashchange', handleHashChange);

    const sectionIds = ['hero', 'voice-interaction', 'response-queue', 'performance-metrics'];
    
    // Create an intersection observer with a precise detection zone (a 1% band located 30% from the top)
    const observerOptions = {
      root: null,
      rootMargin: '-30% 0px -69% 0px', 
      threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setActiveTab(`#${entry.target.id}`);
        }
      });
    }, observerOptions);

    // Observe all sections
    sectionIds.forEach((id) => {
      const section = document.getElementById(id);
      if (section) observer.observe(section);
    });

    return () => {
      window.removeEventListener('hashchange', handleHashChange);
      observer.disconnect();
    };
  }, []);

  const navLinks = [
    { name: 'Intelligence', href: '#hero' },
    { name: 'Voice Synthesis', href: '#voice-interaction' },
    { name: 'HH Goa 2026', href: '#response-queue' },
    { name: 'Latency', href: '#performance-metrics' },
  ];

  // Find the index of the active tab for the mobile ExpandableTabs
  const activeTabIndex = navLinks.findIndex(link => link.href === activeTab);

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 py-1.5 w-full md:w-[85%] max-w-6xl md:mx-auto md:mt-3 rounded-full bg-[#0a1422]/60 backdrop-blur-2xl border border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.37)] md:px-6 md:py-2 transition-all">
        {/* Brand Logo & Open Source Badge */}
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="Dhwani AI Logo" className="h-8 md:h-12 w-auto object-contain drop-shadow-[0_0_12px_rgba(37,217,245,0.4)]" />
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#25d9f5]/10 border border-[#25d9f5]/30 text-[10px] font-['JetBrains_Mono'] text-[#25d9f5] uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-[#25d9f5] animate-pulse"></span>
            Open Source
          </div>
        </div>

        {/* Desktop Nav Links */}
        <div className="hidden md:flex items-center space-x-8">
          {navLinks.map((link) => (
            <a
              key={link.href}
              className={`font-['JetBrains_Mono'] text-[14px] transition-colors pb-1 ${
                activeTab === link.href
                  ? "text-[#a2eeff] font-bold border-b-2 border-[#a2eeff] glow-text"
                  : "text-[#bbc9cd] hover:text-[#a2eeff]"
              }`}
              href={link.href}
              onClick={() => setActiveTab(link.href)}
            >
              {link.name}
            </a>
          ))}
        </div>

        {/* Right Actions */}
        <div className="hidden md:flex items-center space-x-4">
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-3 py-1 rounded-full border border-[#a2eeff]/20 bg-white/5 hover:bg-[#25d9f5]/15 hover:border-[#25d9f5]/50 text-[#bbc9cd] hover:text-[#25d9f5] transition-all font-['JetBrains_Mono'] text-[12px] shadow-sm backdrop-blur-md"
          >
            <i className="bi bi-github"></i>
            <span>Star</span>
            <span className="px-1.5 py-0.2 bg-[#25d9f5]/20 text-[#25d9f5] text-[10px] rounded-full">4.2k</span>
          </a>
        </div>

        {/* Removed Mobile Hamburger Button */}
      </nav>

      {/* Mobile Bottom Navigation using ExpandableTabs */}
      <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 md:hidden w-[92%] flex justify-center">
        <ExpandableTabs
          tabs={[
            { title: "Intelligence", icon: "bi-cpu", href: "#hero" },
            { title: "Synthesis", icon: "bi-mic", href: "#voice-interaction" },
            { title: "HH Goa", icon: "bi-layers", href: "#response-queue" },
            { title: "Latency", icon: "bi-speedometer2", href: "#performance-metrics" },
          ]}
          activeTab={activeTabIndex !== -1 ? activeTabIndex : 0}
          className="bg-[#16202f]/80 backdrop-blur-xl border-[#a2eeff]/20 w-auto justify-between px-2"
          activeColor="text-[#25d9f5]"
        />
      </div>
    </>
  );
}
