import React, { useState } from 'react';
import { VoicePoweredOrb } from './ui/voice-powered-orb';
import { Button } from './ui/button';

export default function VoiceInputSection({ voiceRef }) {
  const [isRecording, setIsRecording] = useState(false);
  const [voiceDetected, setVoiceDetected] = useState(false);

  return (
    <section id="voice-interaction" ref={voiceRef} className="snap-start snap-always relative w-full min-h-fit lg:h-screen lg:max-h-screen flex flex-col items-center justify-center overflow-hidden py-8 md:py-16 bg-gradient-to-b from-[#06111F] to-[#081525]">
      <div className="relative z-10 flex flex-col items-center w-full max-w-4xl mx-auto px-6 text-center space-y-3.5">
        {/* Header */}
        <div className="flex flex-col items-center space-y-1">
          <span className="font-['JetBrains_Mono'] text-[11px] text-[#25d9f5] tracking-[0.2em]">02 / VOICE INPUT</span>
          <h2 className="font-['Sora'] font-bold text-[26px] md:text-[34px] leading-[1.1] text-[#d9e3f7]">
            Speak to <span className="text-gradient font-['Poppins']">ध्वनि</span>
          </h2>
          <p className="font-['Hanken_Grotesk'] text-[#bbc9cd]/80 max-w-[500px] text-xs">
            Tap the button to enable voice control. Speak to see the orb respond to your voice in real-time.
          </p>
        </div>

        {/* WebGL Voice Orb Container */}
        <div className="relative w-[150px] h-[150px] md:w-[200px] md:h-[200px] flex items-center justify-center mt-1">
          {/* Subtle Outer Glow Rings */}
          <div className={`absolute inset-0 rounded-full border border-[#25d9f5]/20 transition-all duration-500 ${isRecording ? 'animate-pulse-ring' : 'scale-95 opacity-50'}`}></div>
          <div className={`absolute inset-3 rounded-full border border-[#25d9f5]/40 border-dashed animate-spin transition-opacity duration-500 ${isRecording ? 'opacity-100' : 'opacity-20'}`} style={{ animationDuration: '35s' }}></div>
          <div className={`absolute inset-6 rounded-full bg-[#25d9f5]/10 blur-2xl transition-opacity duration-500 ${isRecording && voiceDetected ? 'opacity-100 animate-pulse' : 'opacity-0'}`}></div>
          
          <VoicePoweredOrb
            enableVoiceControl={isRecording}
            onVoiceDetected={setIsRecording ? setVoiceDetected : undefined}
            className="rounded-full overflow-hidden z-10 border border-white/5"
            hue={190} // Set custom cyan hue
            voiceSensitivity={1.8}
            maxRotationSpeed={1.5}
            maxHoverIntensity={1.0}
          />
        </div>

        {/* Control Button */}
        <Button
          onClick={() => setIsRecording(!isRecording)}
          variant={isRecording ? "destructive" : "default"}
          size="sm"
          className={`px-6 py-2 rounded-full font-['JetBrains_Mono'] tracking-widest text-[11px] transition-all cursor-pointer ${
            isRecording 
              ? 'bg-red-600 hover:bg-red-700 text-white shadow-[0_0_15px_rgba(220,38,38,0.4)] border border-red-500/50' 
              : 'bg-[#25d9f5]/10 border border-[#25d9f5] text-[#25d9f5] hover:bg-[#25d9f5] hover:text-[#00363e] shadow-[0_0_15px_rgba(37,217,245,0.2)]'
          }`}
        >
          {isRecording ? (
            <span className="flex items-center gap-2">
              <i className="bi bi-mic-mute-fill"></i> STOP LISTENING
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <i className="bi bi-mic-fill"></i> START LISTENING
            </span>
          )}
        </Button>

        {/* Animated Waveform (Only active when voice is detected) */}
        <div className={`flex items-end justify-center space-x-1.5 h-[24px] transition-opacity duration-300 ${isRecording && voiceDetected ? 'opacity-100' : 'opacity-30'}`}>
          <div className="w-1 bg-[#25d9f5]/40 rounded-full animate-wave-1"></div>
          <div className="w-1 bg-[#25d9f5]/60 rounded-full animate-wave-2"></div>
          <div className="w-1 bg-[#25d9f5]/80 rounded-full animate-wave-3"></div>
          <div className="w-1 bg-[#25d9f5] rounded-full animate-wave-4"></div>
          <div className="w-1 bg-[#25d9f5]/80 rounded-full animate-wave-5"></div>
          <div className="w-1 bg-[#25d9f5] rounded-full animate-wave-3"></div>
          <div className="w-1 bg-[#25d9f5]/80 rounded-full animate-wave-4"></div>
          <div className="w-1 bg-[#25d9f5]/60 rounded-full animate-wave-2"></div>
          <div className="w-1 bg-[#25d9f5]/40 rounded-full animate-wave-1"></div>
        </div>

        {/* Live Transcription Card */}
        <div className={`backdrop-blur-xl border w-full max-w-[450px] p-4 rounded-2xl flex flex-col items-start space-y-2 relative overflow-hidden shadow-xl transition-all duration-300 ${isRecording ? 'bg-[#0a1928]/90 border-[#25d9f5]/50 shadow-[0_0_20px_rgba(37,217,245,0.15)]' : 'bg-[#0a1928]/70 border-[#25d9f5]/20'}`}>
          <div className="flex items-center space-x-2">
            <div className={`w-1.5 h-1.5 rounded-full ${isRecording ? (voiceDetected ? 'bg-red-500 animate-ping' : 'bg-[#25d9f5] animate-pulse') : 'bg-[#bbc9cd]/30'}`}></div>
            <span className="font-['JetBrains_Mono'] text-[9px] text-[#25d9f5] tracking-wider">
              {isRecording ? (voiceDetected ? 'LISTENING (SPEECH DETECTED)' : 'LISTENING (WAITING FOR INPUT)') : 'SYSTEM IDLE'}
            </span>
          </div>
          <p className="font-['Hanken_Grotesk'] text-[#bbc9cd]/60 italic text-left w-full text-xs">
            {isRecording ? '"Listening in real-time. Speak now..."' : '"Tap Start Listening to interact..."'}
          </p>
        </div>

        {/* Voice Pipeline Steps */}
        <div className="flex items-center justify-center space-x-4 md:space-x-6 pt-1 w-full max-w-md">
          <div className="flex flex-col items-center space-y-2">
            <div className={`w-10 h-10 rounded-full border flex items-center justify-center bg-[#06111F] transition-all ${isRecording ? 'border-[#25d9f5] shadow-[0_0_10px_rgba(37,217,245,0.25)] text-[#25d9f5]' : 'border-[#25d9f5]/30 text-[#25d9f5]/60'}`}>
              <i className="bi bi-mic text-[18px]"></i>
            </div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">MIC</span>
          </div>
          <div className="h-[1px] w-8 bg-[#25d9f5]/30"></div>
          <div className="flex flex-col items-center space-y-2">
            <div className={`w-10 h-10 rounded-full border flex items-center justify-center bg-[#06111F] transition-all ${isRecording && voiceDetected ? 'border-[#25d9f5] shadow-[0_0_10px_rgba(37,217,245,0.25)] text-[#25d9f5]' : 'border-[#25d9f5]/30 text-[#25d9f5]/60'}`}>
              <i className="bi bi-body-text text-[18px]"></i>
            </div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">STT</span>
          </div>
          <div className="h-[1px] w-8 bg-[#25d9f5]/30"></div>
          <div className="flex flex-col items-center space-y-2">
            <div className={`w-10 h-10 rounded-full border flex items-center justify-center bg-[#06111F] transition-all ${isRecording && voiceDetected ? 'border-[#25d9f5] shadow-[0_0_10px_rgba(37,217,245,0.25)] text-[#25d9f5]' : 'border-[#25d9f5]/30 text-[#25d9f5]/60'}`}>
              <i className="bi bi-cpu text-[18px]"></i>
            </div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">NLP</span>
          </div>
        </div>
      </div>
    </section>
  );
}
