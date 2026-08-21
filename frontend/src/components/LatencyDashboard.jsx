import React from 'react';

export default function LatencyDashboard({ metricsRef }) {
  return (
    <section id="performance-metrics" ref={metricsRef} className="relative w-full min-h-screen flex flex-col items-center justify-center overflow-hidden py-24 bg-[#06111F]">
      <div className="relative z-10 flex flex-col items-center w-full max-w-5xl mx-auto px-6 space-y-12">
        <div className="flex flex-col items-center text-center space-y-4">
          <span className="font-['JetBrains_Mono'] text-[12px] text-[#25d9f5] tracking-[0.2em]">04 / PERFORMANCE</span>
          <h2 className="font-['Sora'] font-bold text-[36px] md:text-[56px] leading-[1.1] text-[#d9e3f7]">
            Measured <span className="text-gradient">Intelligence</span>
          </h2>
          <p className="font-['Hanken_Grotesk'] text-[#bbc9cd]/70 max-w-[600px]">
            Every response is evaluated for quality, grounding, and retrieval performance.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full text-left">
          {/* Answer Quality Dial */}
          <div className="glass-panel p-8 rounded-2xl flex flex-col space-y-8">
            <div className="flex items-center justify-between">
              <h3 className="font-['JetBrains_Mono'] text-[#d9e3f7] tracking-wider">ANSWER QUALITY</h3>
              <span className="font-['JetBrains_Mono'] text-[#25d9f5] font-bold">94 / 100</span>
            </div>
            <div className="flex items-center justify-center py-4">
              <div className="relative w-48 h-48 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                  <circle className="text-[#25d9f5]/10" cx="50" cy="50" r="45" fill="transparent" stroke="currentColor" strokeWidth="8"></circle>
                  <circle className="text-[#25d9f5] transition-all duration-1000 ease-out" cx="50" cy="50" r="45" fill="transparent" stroke="currentColor" strokeWidth="8" strokeDasharray="282.7" strokeDashoffset="16.9" strokeLinecap="round"></circle>
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="font-['Sora'] font-bold text-5xl text-[#d9e3f7]">94</span>
                  <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">PERCENT</span>
                </div>
              </div>
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-[12px] font-['JetBrains_Mono']">
                  <span className="text-[#bbc9cd]">GROUNDING</span>
                  <span className="text-[#25d9f5]">96%</span>
                </div>
                <div className="h-1.5 w-full bg-[#25d9f5]/10 rounded-full overflow-hidden">
                  <div className="h-full bg-[#25d9f5] rounded-full" style={{ width: '96%' }}></div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-[12px] font-['JetBrains_Mono']">
                  <span className="text-[#bbc9cd]">RELEVANCE</span>
                  <span className="text-[#25d9f5]">94%</span>
                </div>
                <div className="h-1.5 w-full bg-[#25d9f5]/10 rounded-full overflow-hidden">
                  <div className="h-full bg-[#25d9f5] rounded-full" style={{ width: '94%' }}></div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-[12px] font-['JetBrains_Mono']">
                  <span className="text-[#bbc9cd]">COMPLETENESS</span>
                  <span className="text-[#25d9f5]">92%</span>
                </div>
                <div className="h-1.5 w-full bg-[#25d9f5]/10 rounded-full overflow-hidden">
                  <div className="h-full bg-[#25d9f5] rounded-full" style={{ width: '92%' }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Latency Dashboard */}
          <div className="glass-panel p-8 rounded-2xl flex flex-col space-y-8">
            <div className="flex items-center justify-between">
              <h3 className="font-['JetBrains_Mono'] text-[#d9e3f7] tracking-wider">LATENCY</h3>
              <div className="flex gap-4">
                <div className="flex flex-col items-end">
                  <span className="text-[10px] text-[#bbc9cd]/60 font-['JetBrains_Mono']">P50</span>
                  <span className="text-[#25d9f5] font-bold font-['JetBrains_Mono']">145ms</span>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-[10px] text-[#bbc9cd]/60 font-['JetBrains_Mono']">P70</span>
                  <span className="text-[#d9e3f7] font-['JetBrains_Mono']">178ms</span>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-[10px] text-[#bbc9cd]/60 font-['JetBrains_Mono']">P100</span>
                  <span className="text-[#d9e3f7] font-['JetBrains_Mono']">196ms</span>
                </div>
              </div>
            </div>

            {/* Histogram Chart */}
            <div className="h-32 flex items-end gap-2 w-full px-2">
              <div className="flex-grow bg-[#25d9f5]/20 h-[20%] rounded-t"></div>
              <div className="flex-grow bg-[#25d9f5]/30 h-[40%] rounded-t"></div>
              <div className="flex-grow bg-[#25d9f5]/40 h-[70%] rounded-t"></div>
              <div className="flex-grow bg-[#25d9f5] h-[90%] rounded-t shadow-[0_0_10px_rgba(37,217,245,0.3)]"></div>
              <div className="flex-grow bg-[#25d9f5]/60 h-[60%] rounded-t"></div>
              <div className="flex-grow bg-[#25d9f5]/40 h-[30%] rounded-t"></div>
              <div className="flex-grow bg-[#25d9f5]/20 h-[15%] rounded-t"></div>
            </div>

            <div className="space-y-3 pt-4">
              <div className="flex justify-between items-center py-2 border-b border-[#25d9f5]/10">
                <span className="font-['JetBrains_Mono'] text-[12px] text-[#bbc9cd]">SPEECH TO TEXT</span>
                <span className="font-['JetBrains_Mono'] text-[12px] text-[#d9e3f7]">42 ms</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-[#25d9f5]/10">
                <span className="font-['JetBrains_Mono'] text-[12px] text-[#bbc9cd]">RETRIEVAL</span>
                <span className="font-['JetBrains_Mono'] text-[12px] text-[#d9e3f7]">38 ms</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-[#25d9f5]/10">
                <span className="font-['JetBrains_Mono'] text-[12px] text-[#bbc9cd]">GENERATION</span>
                <span className="font-['JetBrains_Mono'] text-[12px] text-[#d9e3f7]">65 ms</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="font-['JetBrains_Mono'] text-[12px] text-[#25d9f5] font-bold">TOTAL LATENCY</span>
                <span className="font-['JetBrains_Mono'] text-[14px] text-[#25d9f5] font-bold glow-text">145 ms</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 pt-8">
          <div className="w-2 h-2 rounded-full bg-[#25d9f5] shadow-[0_0_8px_#25d9f5]"></div>
          <span className="font-['JetBrains_Mono'] text-[12px] text-[#25d9f5] tracking-widest">SYSTEM PERFORMANCE: OPTIMAL</span>
        </div>
      </div>
    </section>
  );
}
