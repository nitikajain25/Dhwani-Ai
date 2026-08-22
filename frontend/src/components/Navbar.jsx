import React from 'react';
import { ExpandableTabs } from './ui/expandable-tabs';

export default function Navbar({ mobileMenuOpen, setMobileMenuOpen }) {
  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 py-2 w-full md:w-[92%] md:mx-auto md:mt-4 md:rounded-[20px] bg-[#16202f]/40 backdrop-blur-xl border-[0.5px] border-[#a2eeff]/20 shadow-[0px_0px_15px_rgba(37,217,245,0.1)] md:px-8 md:py-3">
        {/* Brand Logo & Open Source Badge */}
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="Dhwani AI Logo" className="h-10 md:h-20 w-auto object-contain drop-shadow-[0_0_15px_rgba(255,255,255,0.4)]" />
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#25d9f5]/10 border border-[#25d9f5]/30 text-[10px] font-['JetBrains_Mono'] text-[#25d9f5] uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-[#25d9f5] animate-pulse"></span>
            Open Source
          </div>
        </div>

        {/* Desktop Nav Links */}
        <div className="hidden md:flex items-center space-x-8">
          <a className="text-[#a2eeff] font-bold border-b-2 border-[#a2eeff] pb-1 font-['JetBrains_Mono'] glow-text text-[14px]" href="#hero">
            Intelligence
          </a>
          <a className="text-[#bbc9cd] hover:text-[#a2eeff] transition-colors font-['JetBrains_Mono'] text-[14px]" href="#voice-interaction">
            Voice Synthesis
          </a>
          <a className="text-[#bbc9cd] hover:text-[#a2eeff] transition-colors font-['JetBrains_Mono'] text-[14px]" href="#response-queue">
            HH Goa 2026
          </a>
          <a className="text-[#bbc9cd] hover:text-[#a2eeff] transition-colors font-['JetBrains_Mono'] text-[14px]" href="#performance-metrics">
            Latency
          </a>
        </div>

        {/* Right Actions */}
        <div className="hidden md:flex items-center space-x-4">
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[#a2eeff]/20 bg-[#16202f]/60 hover:bg-[#25d9f5]/10 hover:border-[#25d9f5]/40 text-[#bbc9cd] hover:text-[#25d9f5] transition-all font-['JetBrains_Mono'] text-[12px]"
          >
            <i className="bi bi-github"></i>
            <span>Star</span>
            <span className="px-1.5 py-0.2 bg-[#25d9f5]/20 text-[#25d9f5] text-[10px] rounded">4.2k</span>
          </a>
          <a className="text-[#bbc9cd] hover:text-[#a2eeff] font-['JetBrains_Mono'] text-[14px] transition-colors" href="#">
            Sign In
          </a>
          <a
            className="bg-[#25d9f5]/10 border border-[#25d9f5] text-[#25d9f5] px-6 py-2 rounded-lg font-['JetBrains_Mono'] text-[14px] hover:bg-[#25d9f5] hover:text-[#00363e] transition-all glow-button scale-95 active:scale-90 flex items-center gap-2"
            href="#"
          >
            Get Started
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
          className="bg-[#16202f]/80 backdrop-blur-xl border-[#a2eeff]/20 w-auto justify-between px-2"
          activeColor="text-[#25d9f5]"
        />
      </div>
    </>
  );
}
