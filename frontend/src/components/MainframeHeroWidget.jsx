import React, { useState, useEffect, useRef } from 'react';

// Custom typewriter hook
function useTypewriter(text, speed = 38, startDelay = 600) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);

  useEffect(() => {
    setDisplayed('');
    setDone(false);

    let index = 0;
    let timer = null;

    const delayTimer = setTimeout(() => {
      timer = setInterval(() => {
        if (index < text.length) {
          setDisplayed(text.slice(0, index + 1));
          index++;
        } else {
          setDone(true);
          clearInterval(timer);
        }
      }, speed);
    }, startDelay);

    return () => {
      clearTimeout(delayTimer);
      if (timer) clearInterval(timer);
    };
  }, [text, speed, startDelay]);

  return { displayed, done };
}

export default function MainframeHeroWidget() {
  const videoRef = useRef(null);
  const prevXRef = useRef(null);
  const targetTimeRef = useRef(0);
  const isSeekingRef = useRef(false);

  const [pillsVisible, setPillsVisible] = useState(false);
  const [copied, setCopied] = useState(false);

  const typewriterText = "Welcome to Dhwani AI. Grounded in speech, verified in real-time. What would you like to know?";
  const { displayed, done } = useTypewriter(typewriterText, 38, 600);

  // Fade-in action pill buttons 400ms after page load
  useEffect(() => {
    const timer = setTimeout(() => {
      setPillsVisible(true);
    }, 400);
    return () => clearTimeout(timer);
  }, []);

  // Mouse scrubbing for background video with requestAnimationFrame interpolation
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const SENSITIVITY = 0.8;
    let animationFrameId = null;
    let currentSmoothTime = 0;

    const handleMouseMove = (e) => {
      if (prevXRef.current === null) {
        prevXRef.current = e.clientX;
        return;
      }

      const delta = e.clientX - prevXRef.current;
      prevXRef.current = e.clientX;

      if (video.duration && !isNaN(video.duration)) {
        const timeOffset = (delta / window.innerWidth) * SENSITIVITY * video.duration;
        let newTarget = targetTimeRef.current + timeOffset;
        newTarget = Math.max(0, Math.min(video.duration, newTarget));
        targetTimeRef.current = newTarget;
      }
    };

    // Smooth render loop lerping current video time towards target time
    const updateVideoSeek = () => {
      if (video.duration && !isNaN(video.duration)) {
        const diff = targetTimeRef.current - currentSmoothTime;
        if (Math.abs(diff) > 0.001) {
          currentSmoothTime += diff * 0.15; // Smooth interpolation factor
          if (!video.seeking) {
            video.currentTime = currentSmoothTime;
          }
        }
      }
      animationFrameId = requestAnimationFrame(updateVideoSeek);
    };

    animationFrameId = requestAnimationFrame(updateVideoSeek);
    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, []);

  const handleCopyEmail = (e) => {
    e.preventDefault();
    navigator.clipboard.writeText("team@dhwani.ai");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative w-full h-[440px] lg:h-[480px] rounded-2xl overflow-hidden shadow-2xl border border-white/10 text-black flex flex-col justify-end pb-8 sm:pb-12 px-6 sm:px-10">
      {/* Mouse Scrubbed Video Layer */}
      <video
        ref={videoRef}
        src="https://go.screenpal.com/watch/cOjYYCnvLoa.mp4"
        muted
        playsInline
        preload="auto"
        className="absolute inset-0 w-full h-full object-cover object-[70%_center] z-0 pointer-events-none"
      />

      {/* Light card backdrop container for high contrast */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-[2px] pointer-events-none z-0" />

      {/* Content Container */}
      <div className="max-w-xl relative z-10 text-left">
        {/* Blurred Intro Label */}
        <div className="pointer-events-none select-none mb-5 sm:mb-6 text-[clamp(18px,4vw,26px)] leading-[1.3] font-normal text-white filter blur-[4px]">
          Hey there, meet <span className="font-['Poppins']">ध्वनि AI</span>,<br />
          Your real-time speech retrieval companion.
        </div>

        {/* Typewriter Text */}
        <p className="text-white mb-5 sm:mb-6 text-[clamp(18px,4vw,26px)] leading-[1.35] font-normal min-h-[54px]">
          {displayed}
          {!done && (
            <span
              className="inline-block w-[2px] h-[1.1em] bg-white align-middle ml-[2px]"
              style={{ animation: 'blink 1s step-end infinite' }}
            />
          )}
        </p>

        {/* Action Pill Buttons */}
        <div
          className="flex flex-wrap gap-y-1 transition-all duration-400 ease-out"
          style={{
            opacity: pillsVisible ? 1 : 0,
            transform: pillsVisible ? 'translateY(0)' : 'translateY(8px)',
          }}
        >
          {/* White Pill Buttons */}
          <a href="#voice-interaction" className="inline-flex items-center justify-center bg-white text-black border border-black/10 rounded-full text-[13px] sm:text-[15px] px-4 sm:px-5 py-[0.3em] mx-[0.2em] mb-[0.4em] whitespace-nowrap hover:bg-black hover:text-white transition-colors duration-200 cursor-pointer no-underline">
            Try Voice Input
          </a>
          <a href="#performance-metrics" className="inline-flex items-center justify-center bg-white text-black border border-black/10 rounded-full text-[13px] sm:text-[15px] px-4 sm:px-5 py-[0.3em] mx-[0.2em] mb-[0.4em] whitespace-nowrap hover:bg-black hover:text-white transition-colors duration-200 cursor-pointer no-underline">
            Explore Latency
          </a>
          <a href="#response-queue" className="inline-flex items-center justify-center bg-white text-black border border-black/10 rounded-full text-[13px] sm:text-[15px] px-4 sm:px-5 py-[0.3em] mx-[0.2em] mb-[0.4em] whitespace-nowrap hover:bg-black hover:text-white transition-colors duration-200 cursor-pointer no-underline">
            View Response Queue
          </a>
          <a href="#hero" className="inline-flex items-center justify-center bg-white text-black border border-black/10 rounded-full text-[13px] sm:text-[15px] px-4 sm:px-5 py-[0.3em] mx-[0.2em] mb-[0.4em] whitespace-nowrap hover:bg-black hover:text-white transition-colors duration-200 cursor-pointer no-underline">
            HH Goa 2026
          </a>

          {/* Outline Pill Button with Copy Email */}
          <button
            onClick={handleCopyEmail}
            className="inline-flex items-center justify-center text-white bg-transparent border border-white rounded-full text-[13px] sm:text-[15px] px-4 sm:px-5 py-[0.3em] mx-[0.2em] mb-[0.4em] whitespace-nowrap gap-2 sm:gap-3 hover:bg-white hover:text-black transition-colors duration-200 cursor-pointer group"
          >
            <span>
              Reach us:{' '}
              <span className="underline underline-offset-1">
                {copied ? 'Copied to clipboard!' : 'team@dhwani.ai'}
              </span>
            </span>
            <svg
              className="w-3 h-3 fill-current opacity-90 group-hover:opacity-100"
              viewBox="0 0 16 16"
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect x="2" y="2" width="9" height="9" fill="none" stroke="currentColor" strokeWidth="1.5" rx="1" />
              <rect x="5" y="5" width="9" height="9" fill="none" stroke="currentColor" strokeWidth="1.5" rx="1" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
