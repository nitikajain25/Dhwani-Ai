import React, { useEffect, useState, useRef } from 'react';

export default function EyesComponent({ className = '' }) {
  const containerRef = useRef(null);
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;

      const dx = e.clientX - cx;
      const dy = e.clientY - cy;

      const distance = Math.min(8, Math.hypot(dx, dy));
      const angle = Math.atan2(dy, dx);

      setOffset({
        x: Math.cos(angle) * distance,
        y: Math.sin(angle) * distance,
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div
      ref={containerRef}
      className={`inline-flex items-center gap-1.5 bg-[#121d2d]/80 border border-[#a2eeff]/30 px-2 py-1 rounded-full shadow-[0_0_15px_rgba(37,217,245,0.2)] backdrop-blur-md ${className}`}
      style={{ height: '36px' }}
      title="Interactive Eyes"
    >
      {/* Left Eye */}
      <div className="relative w-5 h-7 bg-white rounded-full flex items-center justify-center overflow-hidden shadow-inner">
        <div
          className="relative w-3.5 h-4.5 bg-[#0c0c0c] rounded-full flex items-center justify-center transition-transform duration-75 ease-out"
          style={{
            transform: `translate(${offset.x}px, ${offset.y}px)`,
          }}
        >
          {/* Pupil Highlight */}
          <div className="absolute bottom-0.5 w-1 h-1 bg-white rounded-full" />
        </div>
      </div>

      {/* Right Eye */}
      <div className="relative w-5 h-7 bg-white rounded-full flex items-center justify-center overflow-hidden shadow-inner">
        <div
          className="relative w-3.5 h-4.5 bg-[#0c0c0c] rounded-full flex items-center justify-center transition-transform duration-75 ease-out"
          style={{
            transform: `translate(${offset.x}px, ${offset.y}px)`,
          }}
        >
          {/* Pupil Highlight */}
          <div className="absolute bottom-0.5 w-1 h-1 bg-white rounded-full" />
        </div>
      </div>
    </div>
  );
}
