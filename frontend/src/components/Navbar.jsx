import React from 'react';

export default function Navbar({ mobileMenuOpen, setMobileMenuOpen }) {
  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 md:px-8 py-3 w-[92%] mx-auto mt-4 rounded-[20px] bg-[#16202f]/40 backdrop-blur-xl border-[0.5px] border-[#a2eeff]/20 shadow-[0px_0px_15px_rgba(37,217,245,0.1)]">
        {/* Brand Logo */}
        <div className="flex items-center">
          <span className="font-['Sora'] font-bold text-2xl tracking-tight text-[#a2eeff] glow-text flex items-center gap-2">
            <i className="bi bi-soundwave text-[#25d9f5]"></i> ध्वनि <span className="text-xs px-2 py-0.5 rounded-full bg-[#25d9f5]/20 border border-[#25d9f5]/40 text-[#25d9f5]">AI</span>
          </span>
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
        <div className="hidden md:flex items-center space-x-6">
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

        {/* Mobile Hamburger Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden text-[#25d9f5] p-2 focus:outline-none"
          aria-label="Toggle navigation menu"
        >
          <i className={`bi ${mobileMenuOpen ? 'bi-x-lg' : 'bi-list'} text-2xl`}></i>
        </button>
      </nav>

      {/* Mobile Slide-out Menu */}
      {mobileMenuOpen && (
        <div className="fixed inset-x-4 top-20 z-50 md:hidden glass-panel p-6 rounded-2xl border border-[#25d9f5]/30 shadow-2xl flex flex-col space-y-4 animate-in fade-in slide-in-from-top-4">
          <a
            onClick={() => setMobileMenuOpen(false)}
            className="text-[#a2eeff] font-bold font-['JetBrains_Mono'] text-[16px] py-2 border-b border-[#25d9f5]/20 flex items-center gap-2"
            href="#hero"
          >
            <i className="bi bi-cpu"></i> Intelligence
          </a>
          <a
            onClick={() => setMobileMenuOpen(false)}
            className="text-[#bbc9cd] hover:text-[#a2eeff] font-['JetBrains_Mono'] text-[16px] py-2 border-b border-[#25d9f5]/20 flex items-center gap-2"
            href="#voice-interaction"
          >
            <i className="bi bi-mic"></i> Voice Synthesis
          </a>
          <a
            onClick={() => setMobileMenuOpen(false)}
            className="text-[#bbc9cd] hover:text-[#a2eeff] font-['JetBrains_Mono'] text-[16px] py-2 border-b border-[#25d9f5]/20 flex items-center gap-2"
            href="#response-queue"
          >
            <i className="bi bi-layers"></i> HH Goa 2026
          </a>
          <a
            onClick={() => setMobileMenuOpen(false)}
            className="text-[#bbc9cd] hover:text-[#a2eeff] font-['JetBrains_Mono'] text-[16px] py-2 border-b border-[#25d9f5]/20 flex items-center gap-2"
            href="#performance-metrics"
          >
            <i className="bi bi-speedometer2"></i> Latency Dashboard
          </a>
          <div className="pt-2 flex flex-col space-y-3">
            <a className="text-center text-[#bbc9cd] font-['JetBrains_Mono'] text-[14px] py-2" href="#">
              Sign In
            </a>
            <a
              className="bg-[#25d9f5] text-[#00363e] text-center font-bold px-6 py-3 rounded-lg font-['JetBrains_Mono'] text-[14px] glow-button"
              href="#"
            >
              Get Started
            </a>
          </div>
        </div>
      )}
    </>
  );
}
