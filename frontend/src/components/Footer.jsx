import React from 'react';

export default function Footer() {
  return (
    <footer className="relative w-full py-24 bg-[#06111F] overflow-hidden border-t border-[#25d9f5]/10">
      <div className="relative z-10 max-w-5xl mx-auto px-6 flex flex-col items-center">
        {/* HH Goa Badge */}
        <div className="glass-panel px-4 py-1.5 rounded-full border-[#25d9f5]/30 mb-12">
          <span className="font-['JetBrains_Mono'] text-[10px] text-[#25d9f5] tracking-widest flex items-center gap-2">
            <span className="text-[#25d9f5]">✦</span> BUILT FOR HH GOA 2026
          </span>
        </div>

        {/* Branding */}
        <div className="flex flex-col items-center space-y-4 mb-12">
          <span className="font-['Sora'] font-bold text-3xl tracking-tight text-[#a2eeff] glow-text flex items-center gap-2">
            <i className="bi bi-soundwave text-[#25d9f5]"></i> ध्वनि AI
          </span>
          <p className="font-['Hanken_Grotesk'] text-[#bbc9cd]/60 text-center">Voice-powered intelligence, grounded in knowledge.</p>
        </div>

        {/* Capabilities */}
        <div className="flex flex-wrap justify-center gap-3 mb-12">
          <span className="glass-panel px-4 py-2 rounded-full font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]/80 border-[#25d9f5]/10">VOICE AI</span>
          <span className="glass-panel px-4 py-2 rounded-full font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]/80 border-[#25d9f5]/10">SPEECH TO TEXT</span>
          <span className="glass-panel px-4 py-2 rounded-full font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]/80 border-[#25d9f5]/10">RAG</span>
          <span className="glass-panel px-4 py-2 rounded-full font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]/80 border-[#25d9f5]/10">VECTOR SEARCH</span>
          <span className="glass-panel px-4 py-2 rounded-full font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]/80 border-[#25d9f5]/10">GROUNDED ANSWERS</span>
        </div>

        {/* Footer Links */}
        <div className="flex flex-wrap justify-center items-center gap-8 mb-12">
          <a className="font-['JetBrains_Mono'] text-[12px] text-[#d9e3f7]/70 hover:text-[#25d9f5] transition-colors tracking-widest" href="#hero">
            HOME
          </a>
          <a className="font-['JetBrains_Mono'] text-[12px] text-[#d9e3f7]/70 hover:text-[#25d9f5] transition-colors tracking-widest" href="#voice-interaction">
            VOICE
          </a>
          <a className="font-['JetBrains_Mono'] text-[12px] text-[#d9e3f7]/70 hover:text-[#25d9f5] transition-colors tracking-widest" href="#response-queue">
            RESPONSE
          </a>
          <a className="font-['JetBrains_Mono'] text-[12px] text-[#d9e3f7]/70 hover:text-[#25d9f5] transition-colors tracking-widest" href="#performance-metrics">
            PERFORMANCE
          </a>
        </div>

        {/* Social Icons */}
        <div className="flex items-center space-x-4 mb-16">
          <a className="w-10 h-10 rounded-full glass-panel border-[#25d9f5]/20 flex items-center justify-center hover:border-[#25d9f5]/60 transition-all group" href="#">
            <i className="bi bi-code-slash text-lg text-[#bbc9cd] group-hover:text-[#25d9f5]"></i>
          </a>
          <a className="w-10 h-10 rounded-full glass-panel border-[#25d9f5]/20 flex items-center justify-center hover:border-[#25d9f5]/60 transition-all group" href="#">
            <i className="bi bi-share text-lg text-[#bbc9cd] group-hover:text-[#25d9f5]"></i>
          </a>
        </div>

        {/* Bottom Copyright */}
        <div className="w-full pt-8 border-t border-[#25d9f5]/10 flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]/40">© 2026 DHWANI AI</span>
          <div className="h-[1px] flex-grow bg-[#25d9f5]/5 mx-8 hidden md:block"></div>
          <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]/40 tracking-widest">HH GOA 2026</span>
        </div>
      </div>
    </footer>
  );
}
