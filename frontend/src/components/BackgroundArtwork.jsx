import React from 'react';

export default function BackgroundArtwork() {
  return (
    <div className="fixed inset-0 z-0 bg-[#07111F] pointer-events-none overflow-hidden">
      <svg
        className="absolute inset-0 w-full h-full opacity-[0.1] mix-blend-screen"
        preserveAspectRatio="xMidYMax slice"
        viewBox="0 0 1440 900"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern id="halftone" width="4" height="4" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="0.5" fill="#25d9f5" opacity="0.15" />
          </pattern>
          <linearGradient id="fadeCenter" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#0b2930" />
            <stop offset="30%" stopColor="#07111f" stopOpacity="0" />
            <stop offset="70%" stopColor="#07111f" stopOpacity="0" />
            <stop offset="100%" stopColor="#0b2930" />
          </linearGradient>
          <linearGradient id="fadeTop" x1="0" y1="1" x2="0" y2="0">
            <stop offset="0%" stopColor="#0b2930" stopOpacity="0.8" />
            <stop offset="60%" stopColor="#07111f" stopOpacity="0" />
          </linearGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#halftone)" />
        {/* Left Edge: Palm leaves and coastal silhouettes */}
        <g fill="none" stroke="#25d9f5" strokeWidth="1.5" opacity="0.7">
          <path d="M-50,100 Q150,150 200,300 Q180,250 100,200 Q220,350 250,500 Q200,400 120,350" />
          <path d="M-50,100 Q50,200 80,350" />
          <path d="M-50,100 Q100,100 150,200" />
          <path d="M-20,0 Q250,50 300,250 Q250,180 150,150" opacity="0.6" strokeWidth="1" />
          <path d="M0,600 Q150,620 300,700 T600,750" fill="#0b2930" opacity="0.6" />
          <path d="M0,600 Q150,620 300,700 T600,750" />
          <rect x="50" y="650" width="100" height="80" fill="#0b2930" opacity="0.8" />
          <rect x="50" y="650" width="100" height="80" />
          <path d="M40,650 L100,600 L160,650 Z" fill="#0b2930" />
          <path d="M40,650 L100,600 L160,650 Z" />
          <rect x="70" y="680" width="30" height="30" />
          <path d="M0,550 Q100,530 200,560 T400,580" opacity="0.3" />
        </g>
        {/* Right Edge: Palm trees and Beach Shack */}
        <g fill="none" stroke="#25d9f5" strokeWidth="1.5" opacity="0.75">
          <path d="M1350,800 Q1300,600 1320,400" />
          <path d="M1360,800 Q1310,600 1330,400" />
          <path d="M1350,750 L1360,755 M1345,700 L1355,705 M1335,650 L1345,655" opacity="0.5" />
          <path d="M1250,800 Q1220,650 1260,550" strokeWidth="1" />
          <path d="M1258,800 Q1228,650 1268,550" strokeWidth="1" />
          <path d="M1325,400 Q1200,350 1150,450" />
          <path d="M1325,400 Q1250,250 1200,300" />
          <path d="M1325,400 Q1350,250 1400,300" />
          <path d="M1325,400 Q1450,350 1480,450" />
          <path d="M1325,400 Q1300,500 1250,550" />
          <path d="M1325,400 Q1400,500 1450,550" />
          <path d="M1264,550 Q1200,520 1180,580" strokeWidth="1" />
          <path d="M1264,550 Q1240,480 1220,500" strokeWidth="1" />
          <path d="M1264,550 Q1300,480 1330,500" strokeWidth="1" />
          <path d="M1264,550 Q1320,580 1340,620" strokeWidth="1" />
          <rect x="1100" y="650" width="180" height="150" fill="#0b2930" opacity="0.9" />
          <rect x="1100" y="650" width="180" height="150" />
          <path d="M1080,650 L1190,580 L1300,650 Z" fill="#0b2930" />
          <path d="M1080,650 L1190,580 L1300,650 Z" />
          <path d="M1100,650 L1190,600 L1280,650" strokeDasharray="2,2" />
          <rect x="1120" y="680" width="140" height="60" />
          <path d="M1140,750 L1140,780 M1135,780 L1145,780" />
          <path d="M1190,750 L1190,780 M1185,780 L1195,780" />
          <path d="M1240,750 L1240,780 M1235,780 L1245,780" />
          <rect x="1150" y="620" width="80" height="20" fill="#07111F" />
          <rect x="1150" y="620" width="80" height="20" />
          <text x="1190" y="634" fill="#25d9f5" fontFamily="JetBrains Mono, monospace" fontSize="10" fontWeight="500" textAnchor="middle" stroke="none">GOA 2026</text>
        </g>
        {/* Bottom: Ocean Waves, tiny sailboat */}
        <g fill="none" stroke="#25d9f5" strokeWidth="1" opacity="0.6">
          <path d="M0,780 Q100,770 200,780 T400,780 T600,780 T800,780 T1000,780 T1200,780 T1440,780" />
          <path d="M0,810 Q150,795 300,810 T600,810 T900,810 T1200,810 T1440,810" />
          <path d="M0,840 Q100,830 200,840 T400,840 T600,840 T800,840 T1000,840 T1200,840 T1440,840" />
          <path d="M0,870 Q150,860 300,870 T600,870 T900,870 T1200,870 T1440,870" />
          <path d="M350,750 L380,750 L390,740 L340,740 Z" fill="#0b2930" opacity="0.8" />
          <path d="M350,750 L380,750 L390,740 L340,740 Z" />
          <path d="M365,740 L365,710 L385,735 Z" fill="#0b2930" opacity="0.8" />
          <path d="M365,740 L365,710 L385,735 Z" />
          <path d="M450,780 C600,780 700,600 720,500" opacity="0.6" strokeDasharray="5,5" />
          <path d="M500,810 C700,810 800,650 820,550" opacity="0.4" strokeDasharray="2,4" />
          <path d="M800,840 C900,840 950,600 950,450" opacity="0.5" strokeDasharray="4,6" />
        </g>
        <rect width="100%" height="100%" fill="url(#fadeCenter)" opacity="0.85" />
        <rect width="100%" height="100%" fill="url(#fadeTop)" opacity="0.95" />
      </svg>
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_20%,#07111F_75%)] opacity-90"></div>
      <div className="absolute inset-0 bg-gradient-to-b from-[#07111F] via-transparent to-[#07111F] opacity-70"></div>
    </div>
  );
}
