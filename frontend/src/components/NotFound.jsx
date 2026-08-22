import React from "react";

export default function NotFound() {
  const handleGoHome = (e) => {
    e.preventDefault();
    window.history.pushState({}, "", "/");
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  return (
    <div className="bg-[#0a1422] text-[#d9e3f7] font-['Hanken_Grotesk',sans-serif] min-h-screen w-screen flex flex-col items-center justify-center relative overflow-hidden px-6 selection:bg-[#25d9f5] selection:text-[#00363e]">
      {/* Background Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-[#25d9f5]/5 filter blur-[120px] pointer-events-none z-0" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-500/5 filter blur-[120px] pointer-events-none z-0" />

      {/* Main Container */}
      <div className="relative z-10 flex flex-col items-center text-center max-w-lg space-y-8">
        
        {/* Animated Icon Container */}
        <div className="relative flex items-center justify-center w-28 h-28">
          {/* Animated rings */}
          <div className="absolute inset-0 rounded-full border border-dashed border-[#25d9f5]/30 animate-spin" style={{ animationDuration: '15s' }}></div>
          <div className="absolute inset-2 rounded-full border border-double border-purple-500/20 animate-spin" style={{ animationDuration: '10s', animationDirection: 'reverse' }}></div>
          <div className="absolute inset-4 rounded-full bg-[#16202f]/80 backdrop-blur-xl border border-white/5 flex items-center justify-center shadow-[0_0_30px_rgba(37,217,245,0.1)]">
            <span className="font-['Sora'] font-bold text-3xl text-transparent bg-clip-text bg-gradient-to-r from-[#25d9f5] to-purple-400">404</span>
          </div>
        </div>

        {/* Text Details */}
        <div className="space-y-3">
          <h1 className="font-['Sora'] font-bold text-[28px] md:text-[36px] leading-tight text-[#d9e3f7]">
            Signal <span className="text-gradient">Lost</span>
          </h1>
          <p className="font-['Hanken_Grotesk'] text-[#bbc9cd]/75 text-sm md:text-base max-w-[400px] mx-auto">
            The voice command or retrieval path you are looking for has disconnected from the Dhwani interface.
          </p>
        </div>

        {/* Broken Wave Animation */}
        <div className="flex items-center gap-1.5 justify-center py-2 h-10 w-full">
          {[0.2, 0.5, 0.1, 0.8, 0.3, 0.6, 0.2, 0.4, 0.7, 0.3, 0.5, 0.2].map((delay, index) => (
            <div
              key={index}
              className="w-1 rounded bg-gradient-to-t from-[#25d9f5]/60 to-purple-400/80 animate-pulse"
              style={{
                height: `${12 + Math.sin(index) * 16}px`,
                animationDelay: `${delay}s`,
                animationDuration: '1.2s'
              }}
            />
          ))}
        </div>

        {/* Back Button CTA */}
        <div className="pt-4">
          <a
            href="/"
            onClick={handleGoHome}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-[#25d9f5] to-[#42ded8] text-[#00363e] font-['JetBrains_Mono'] font-bold px-8 py-3.5 rounded-lg hover:opacity-90 transition-all glow-button scale-95 active:scale-90"
          >
            <i className="bi bi-house-door-fill text-lg"></i>
            Restore Connection
          </a>
        </div>
      </div>
    </div>
  );
}
