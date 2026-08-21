import React from 'react';

export default function VoiceInputSection({ voiceRef }) {
  return (
    <section id="voice-interaction" ref={voiceRef} className="relative w-full min-h-[90vh] flex flex-col items-center justify-center overflow-hidden py-24 bg-gradient-to-b from-[#06111F] to-[#081525]">
      <div className="relative z-10 flex flex-col items-center w-full max-w-4xl mx-auto px-6 text-center space-y-12">
        {/* Header */}
        <div className="flex flex-col items-center space-y-4">
          <span className="font-['JetBrains_Mono'] text-[12px] text-[#25d9f5] tracking-[0.2em]">02 / VOICE INPUT</span>
          <h2 className="font-['Sora'] font-bold text-[36px] md:text-[56px] leading-[1.1] text-[#d9e3f7]">
            Speak to <span className="text-gradient">ध्वनि</span>
          </h2>
          <p className="font-['Hanken_Grotesk'] text-[#bbc9cd]/80 max-w-[500px]">
            Tap the microphone and start speaking. Dhwani listens, understands, and finds the right information.
          </p>
        </div>

        {/* Interactive Microphone Button Visual */}
        <div className="relative w-[280px] h-[280px] md:w-[380px] md:h-[380px] flex items-center justify-center mt-8 mb-4">
          <div className="absolute inset-0 rounded-full border border-[#25d9f5]/20 animate-pulse-ring"></div>
          <div className="absolute inset-4 rounded-full border border-[#25d9f5]/40 border-dashed animate-spin" style={{ animationDuration: '30s' }}></div>
          <div className="absolute inset-8 rounded-full bg-[#25d9f5]/10 blur-2xl animate-pulse"></div>
          <button className="relative z-10 w-[140px] h-[140px] md:w-[160px] md:h-[160px] rounded-full bg-[#06111F] border-2 border-[#25d9f5] flex flex-col items-center justify-center glow-button hover:bg-[#212a39] transition-all group shadow-[0_0_30px_rgba(37,217,245,0.5)] cursor-pointer">
            <i className="bi bi-mic-fill text-5xl md:text-6xl text-[#25d9f5] group-hover:scale-110 transition-transform"></i>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#25d9f5] mt-2 tracking-widest opacity-80">READY</span>
            <div className="absolute inset-0 rounded-full bg-[#25d9f5]/20 animate-ping opacity-20 pointer-events-none"></div>
          </button>
        </div>

        {/* Animated Waveform */}
        <div className="flex items-end justify-center space-x-1.5 h-[40px]">
          <div className="w-1.5 bg-[#25d9f5]/40 rounded-full animate-wave-1"></div>
          <div className="w-1.5 bg-[#25d9f5]/60 rounded-full animate-wave-2"></div>
          <div className="w-1.5 bg-[#25d9f5]/80 rounded-full animate-wave-3"></div>
          <div className="w-1.5 bg-[#25d9f5] rounded-full animate-wave-4"></div>
          <div className="w-1.5 bg-[#25d9f5]/80 rounded-full animate-wave-5"></div>
          <div className="w-1.5 bg-[#25d9f5] rounded-full animate-wave-3"></div>
          <div className="w-1.5 bg-[#25d9f5]/80 rounded-full animate-wave-4"></div>
          <div className="w-1.5 bg-[#25d9f5]/60 rounded-full animate-wave-2"></div>
          <div className="w-1.5 bg-[#25d9f5]/40 rounded-full animate-wave-1"></div>
        </div>

        {/* Live Transcription Card */}
        <div className="backdrop-blur-xl border w-full max-w-[500px] p-6 rounded-2xl flex flex-col items-start space-y-3 relative overflow-hidden shadow-xl bg-[#0a1928]/70 border-[#25d9f5]/30">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-[#25d9f5] animate-pulse"></div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#25d9f5] tracking-wider">READY TO LISTEN</span>
          </div>
          <p className="font-['Hanken_Grotesk'] text-[#bbc9cd]/60 italic text-left w-full">
            "Tap the microphone and start speaking..."
          </p>
        </div>

        {/* Voice Pipeline Steps */}
        <div className="flex items-center justify-center space-x-4 md:space-x-6 pt-6 w-full max-w-md">
          <div className="flex flex-col items-center space-y-2">
            <div className="w-10 h-10 rounded-full border border-[#25d9f5]/30 flex items-center justify-center bg-[#06111F] shadow-[0_0_10px_rgba(37,217,245,0.1)]">
              <i className="bi bi-mic text-[18px] text-[#25d9f5]"></i>
            </div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">MIC</span>
          </div>
          <div className="h-[1px] w-8 bg-[#25d9f5]/30"></div>
          <div className="flex flex-col items-center space-y-2">
            <div className="w-10 h-10 rounded-full border border-[#25d9f5]/30 flex items-center justify-center bg-[#06111F] shadow-[0_0_10px_rgba(37,217,245,0.1)]">
              <i className="bi bi-body-text text-[18px] text-[#25d9f5]"></i>
            </div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">STT</span>
          </div>
          <div className="h-[1px] w-8 bg-[#25d9f5]/30"></div>
          <div className="flex flex-col items-center space-y-2">
            <div className="w-10 h-10 rounded-full border border-[#25d9f5]/30 flex items-center justify-center bg-[#06111F] shadow-[0_0_10px_rgba(37,217,245,0.1)]">
              <i className="bi bi-cpu text-[18px] text-[#25d9f5]"></i>
            </div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">NLP</span>
          </div>
        </div>
      </div>
    </section>
  );
}
