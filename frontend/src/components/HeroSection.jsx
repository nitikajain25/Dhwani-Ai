import React from 'react';
import MainframeHeroWidget from './MainframeHeroWidget';

export default function HeroSection({ heroRef }) {
  return (
    <section id="hero" ref={heroRef} className="w-full flex items-center justify-center px-6 md:px-16 pt-3 md:pt-4 pb-12 min-h-fit relative max-w-[1440px] mx-auto">
      <div className="flex flex-col lg:flex-row items-center justify-between w-full h-full gap-12 lg:gap-16 pt-8 md:pt-20">
        {/* LEFT COLUMN (50%) */}
        <div className="w-full lg:w-[48%] flex flex-col items-start space-y-3 z-10">
          {/* Badge */}
          <div className="hero-animate glass-panel px-4 py-2 rounded-full flex items-center space-x-2 mt-4 md:mt-6">
            <span className="text-[#25d9f5] text-lg">✦</span>
            <span className="font-['Poppins'] font-semibold text-[#d9e3f7] tracking-wider text-xs md:text-sm">MEET ध्वनि AI</span>
          </div>
          {/* Main Heading */}
          <h1 className="hero-animate font-['Sora'] font-bold text-[32px] sm:text-[40px] md:text-[48px] lg:text-[42px] xl:text-[48px] leading-[1.1] text-[#d9e3f7] tracking-tight text-left">
            Your Voice.<br />
            <span className="text-gradient">Intelligent</span><br />
            Answers.
          </h1>
          {/* Description */}
          <p className="hero-animate font-['Hanken_Grotesk'] text-[#bbc9cd] max-w-[480px] text-left text-sm md:text-base">
            Advanced semantic retrieval meets real-time voice synthesis. Ask complex questions naturally, and experience data-driven answers grounded in verified intelligence.
          </p>
          {/* Process Indicator */}
          <div className="hero-animate flex items-center justify-between w-full max-w-[400px] relative py-4">
            <div className="absolute top-1/2 left-0 w-full h-[1px] bg-[#3c494c] -z-10 transform -translate-y-1/2">
              <div className="h-full bg-[#25d9f5]/30 w-[80%]"></div>
            </div>
            <div className="flex flex-col items-center gap-2 bg-[#0a1422] p-1">
              <div className="w-8 h-8 rounded-full border border-[#25d9f5]/50 flex items-center justify-center bg-[#16202f]">
                <i className="bi bi-mic text-[14px] text-[#25d9f5]"></i>
              </div>
              <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">VOICE</span>
            </div>
            <div className="flex flex-col items-center gap-2 bg-[#0a1422] p-1">
              <div className="w-8 h-8 rounded-full border border-[#25d9f5]/50 flex items-center justify-center bg-[#16202f]">
                <i className="bi bi-search text-[14px] text-[#25d9f5]"></i>
              </div>
              <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">RETRIEVE</span>
            </div>
            <div className="flex flex-col items-center gap-2 bg-[#0a1422] p-1">
              <div className="w-8 h-8 rounded-full border border-[#25d9f5]/50 flex items-center justify-center bg-[#16202f]">
                <i className="bi bi-cpu text-[14px] text-[#25d9f5]"></i>
              </div>
              <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">UNDERSTAND</span>
            </div>
            <div className="flex flex-col items-center gap-2 bg-[#0a1422] p-1">
              <div className="w-8 h-8 rounded-full border border-[#25d9f5] flex items-center justify-center bg-[#25d9f5] shadow-[0_0_10px_rgba(37,217,245,0.5)]">
                <i className="bi bi-volume-up text-[14px] text-[#00363e]"></i>
              </div>
              <span className="font-['JetBrains_Mono'] text-[10px] text-[#25d9f5] font-bold">ANSWER</span>
            </div>
          </div>
          {/* CTAs */}
          <div className="hero-animate flex flex-col sm:flex-row items-center gap-4 pt-4 w-full sm:w-auto">
            <a href="#voice-interaction" className="w-full sm:w-auto bg-gradient-to-r from-[#25d9f5] to-[#42ded8] text-[#00363e] font-['JetBrains_Mono'] font-bold px-8 py-4 rounded-lg flex items-center justify-center gap-2 hover:opacity-90 transition-opacity glow-button">
              <i className="bi bi-mic-fill text-lg"></i>
              Try ध्वनि AI ↓
            </a>
            <a href="#response-queue" className="w-full sm:w-auto glass-panel text-[#d9e3f7] font-['JetBrains_Mono'] px-8 py-4 rounded-lg flex items-center justify-center gap-2 hover:bg-[#212a39] transition-colors">
              See How It Works
              <i className="bi bi-arrow-right text-lg"></i>
            </a>
          </div>
        </div>

        {/* RIGHT COLUMN (50%): Mainframe Interactive Hero Widget */}
        <div className="w-full lg:w-[48%] relative flex items-center justify-center z-10">
          <MainframeHeroWidget />
        </div>
      </div>

      {/* Scroll Down Hint */}
      <a href="#voice-interaction" className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex flex-col items-center gap-2 z-20 cursor-pointer group">
        <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd] group-hover:text-[#25d9f5] transition-colors tracking-widest">SCROLL TO SPEAK</span>
        <i className="bi bi-arrow-down text-[#25d9f5] text-lg animate-bounce"></i>
      </a>
    </section>
  );
}
