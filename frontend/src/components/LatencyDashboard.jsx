import React, { useState } from 'react';
import { DonutChart } from './ui/donut-chart';
import { ArrowRight } from 'lucide-react';

const qualityData = [
  { value: 96, color: "hsl(190, 95%, 50%)", label: "Grounding" },     // Cyan
  { value: 94, color: "hsl(142, 76%, 40%)", label: "Relevance" },     // Green
  { value: 92, color: "hsl(262, 83%, 60%)", label: "Completeness" },  // Purple
];

export default function LatencyDashboard({ metricsRef, telemetry }) {
  const [hoveredSegment, setHoveredSegment] = useState(null);

  const activeSegment = hoveredSegment;
  const displayValue = activeSegment ? activeSegment.value : 94;
  const displayLabel = activeSegment ? activeSegment.label : "Answer Quality";

  // Use simulated backend telemetry (~200ms) as the single source of truth for the demo
  const t = telemetry?.demo ? {
    stt_ms: telemetry.demo.extraction_ms,
    matching_ms: telemetry.demo.matching_ms,
    answer_ms: telemetry.demo.answer_ms,
    gemini_ms: telemetry.actual?.gemini_ms > 0 ? telemetry.demo.generation_ms : 0,
    total_ms: telemetry.actual?.gemini_ms > 0 
      ? telemetry.demo.overall_ms 
      : (telemetry.demo.overall_ms - telemetry.demo.generation_ms)
  } : {
    stt_ms: 0,
    matching_ms: 0,
    answer_ms: 0,
    gemini_ms: 0,
    total_ms: 0
  };

  return (
    <section id="performance-metrics" ref={metricsRef} className="relative w-full min-h-fit lg:h-screen lg:max-h-screen flex flex-col items-center justify-center overflow-hidden py-8 md:py-16 bg-[#06111F]">
      <div className="relative z-10 flex flex-col items-center w-full max-w-5xl mx-auto px-6 space-y-6">
        {/* Header */}
        <div className="flex flex-col items-center text-center space-y-2">
          <span className="font-['JetBrains_Mono'] text-[12px] text-[#25d9f5] tracking-[0.2em]">04 / LATENCY & PERFORMANCE</span>
          <h2 className="font-['Sora'] font-bold text-[32px] md:text-[42px] leading-[1.1] text-[#d9e3f7]">
            Real-Time <span className="text-gradient font-['Poppins']">Telemetry</span>
          </h2>
        </div>

        {/* Dashboard Grid */}
        <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
          
          {/* Latency Pipeline (Takes up 2 columns on desktop) */}
          <div className="md:col-span-2 glass-panel p-6 rounded-2xl border-[#25d9f5]/20 flex flex-col justify-between h-full bg-[#0a1928]/50">
            <div className="flex items-center justify-between mb-8 border-b border-[#25d9f5]/10 pb-4">
              <span className="font-['JetBrains_Mono'] text-[12px] text-[#bbc9cd]">PIPELINE BREAKDOWN</span>
              <span className="font-['JetBrains_Mono'] text-[12px] text-[#25d9f5]">REAL TIME</span>
            </div>
            
            <div className="flex flex-col space-y-6">
              {/* STT */}
              <div className="flex items-center justify-between w-full group cursor-default">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded bg-[#06111F] border border-[#25d9f5]/30 flex items-center justify-center group-hover:border-[#25d9f5] transition-colors">
                    <i className="bi bi-mic text-[#25d9f5]/60 group-hover:text-[#25d9f5]"></i>
                  </div>
                  <span className="font-['JetBrains_Mono'] text-[12px] text-[#d9e3f7]">Speech-to-Text</span>
                </div>
                <div className="flex items-center gap-4 w-1/2">
                  <div className="h-1 bg-[#25d9f5]/20 rounded-full flex-grow overflow-hidden relative">
                    <div className="absolute top-0 left-0 h-full bg-[#25d9f5] rounded-full shadow-[0_0_10px_#25d9f5] transition-all duration-500" style={{ width: `${Math.min((t.stt_ms / (t.total_ms || 1)) * 100, 100)}%` }}></div>
                  </div>
                  <span className="font-['JetBrains_Mono'] text-[12px] text-[#25d9f5] w-[40px] text-right">{t.stt_ms.toFixed(0)}ms</span>
                </div>
              </div>

              {/* Vector DB */}
              <div className="flex items-center justify-between w-full group cursor-default">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded bg-[#06111F] border border-[#25d9f5]/30 flex items-center justify-center group-hover:border-[#25d9f5] transition-colors">
                    <i className="bi bi-database text-[#25d9f5]/60 group-hover:text-[#25d9f5]"></i>
                  </div>
                  <span className="font-['JetBrains_Mono'] text-[12px] text-[#d9e3f7]">Vector/Demo Match</span>
                </div>
                <div className="flex items-center gap-4 w-1/2">
                  <div className="h-1 bg-[#25d9f5]/20 rounded-full flex-grow overflow-hidden relative">
                    <div className="absolute top-0 left-0 h-full bg-[#25d9f5] rounded-full shadow-[0_0_10px_#25d9f5] transition-all duration-500" style={{ width: `${Math.min((t.matching_ms / (t.total_ms || 1)) * 100, 100)}%` }}></div>
                  </div>
                  <span className="font-['JetBrains_Mono'] text-[12px] text-[#25d9f5] w-[40px] text-right">{t.matching_ms.toFixed(0)}ms</span>
                </div>
              </div>

              {/* Generation */}
              <div className="flex items-center justify-between w-full group cursor-default">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded bg-[#06111F] border border-[#25d9f5]/30 flex items-center justify-center group-hover:border-[#25d9f5] transition-colors">
                    <i className="bi bi-lightning text-[#25d9f5]/60 group-hover:text-[#25d9f5]"></i>
                  </div>
                  <span className="font-['JetBrains_Mono'] text-[12px] text-[#d9e3f7]">Gemini Fallback</span>
                </div>
                <div className="flex items-center gap-4 w-1/2">
                  <div className="h-1 bg-[#25d9f5]/20 rounded-full flex-grow overflow-hidden relative">
                    <div className="absolute top-0 left-0 h-full bg-[#25d9f5] rounded-full shadow-[0_0_10px_#25d9f5] transition-all duration-500" style={{ width: `${t.gemini_ms > 0 ? Math.min((t.gemini_ms / (t.total_ms || 1)) * 100, 100) : 0}%` }}></div>
                  </div>
                  <span className="font-['JetBrains_Mono'] text-[12px] text-[#25d9f5] w-[40px] text-right">{t.gemini_ms > 0 ? t.gemini_ms.toFixed(0) : '—'}</span>
                </div>
              </div>
            </div>

            <div className="mt-8 pt-4 border-t border-[#25d9f5]/10 flex justify-between items-end">
              <div className="flex flex-col">
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]/60">END-TO-END LATENCY</span>
                <span className="font-['JetBrains_Mono'] text-[32px] text-[#25d9f5] font-bold leading-none glow-text">{t.total_ms.toFixed(0)}<span className="text-[16px] text-[#25d9f5]/60 font-normal">ms</span></span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full text-left">
          
          {/* Answer Quality Card (DestinationCard styling) */}
          <div
            style={{ "--theme-color": "190 95% 10%" }}
            className="group w-full relative rounded-2xl overflow-hidden shadow-lg transition-all duration-500 ease-in-out hover:scale-[1.02] hover:shadow-[0_0_50px_-10px_hsl(var(--theme-color)/0.8)] border border-[#25d9f5]/15 bg-[#0a1928]/60"
          >
            {/* Background Image with Parallax Zoom */}
            <div
              className="absolute inset-0 bg-cover bg-center opacity-30 transition-transform duration-500 ease-in-out group-hover:scale-110"
              style={{ backgroundImage: `url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=60')` }}
            />
            {/* Gradient Overlay */}
            <div
              className="absolute inset-0"
              style={{
                background: `linear-gradient(to top, hsl(var(--theme-color) / 0.98), hsl(var(--theme-color) / 0.8) 40%, transparent 95%)`,
              }}
            />

            {/* Content */}
            <div className="relative z-10 p-5 md:p-6 flex flex-col justify-between h-full text-white space-y-4">
              <div>
                <div className="flex items-center justify-between">
                  <h3 className="font-['Poppins'] text-[#d9e3f7] font-semibold tracking-wide text-sm">ANSWER QUALITY</h3>
                  <span className="font-['Poppins'] text-[#25d9f5] font-bold text-sm">94 / 100</span>
                </div>
                
                <div className="flex items-center justify-center py-3">
                  <DonutChart
                    data={qualityData}
                    size={110}
                    strokeWidth={14}
                    highlightOnHover={true}
                    onSegmentHover={setHoveredSegment}
                    centerContent={
                      <div className="flex flex-col items-center justify-center text-center">
                        <span className="font-['Poppins'] text-[8px] text-[#bbc9cd]/80 uppercase tracking-widest truncate max-w-[70px]">
                          {displayLabel}
                        </span>
                        <span className="font-['Poppins'] font-bold text-2xl text-[#d9e3f7] mt-0.5">
                          {displayValue}%
                        </span>
                      </div>
                    }
                  />
                </div>

                <div className="space-y-2">
                  <div className="space-y-0.5">
                    <div className={`flex justify-between text-[11px] font-['Poppins'] font-medium transition-all ${hoveredSegment?.label === 'Grounding' ? 'text-[#25d9f5] scale-[1.02]' : 'text-[#bbc9cd]'}`}>
                      <span>GROUNDING</span>
                      <span>96%</span>
                    </div>
                    <div className="h-1 w-full bg-[#25d9f5]/10 rounded-full overflow-hidden">
                      <div className="h-full bg-[#25d9f5] rounded-full" style={{ width: '96%' }}></div>
                    </div>
                  </div>
                  <div className="space-y-0.5">
                    <div className={`flex justify-between text-[11px] font-['Poppins'] font-medium transition-all ${hoveredSegment?.label === 'Relevance' ? 'text-[#42ded8] scale-[1.02]' : 'text-[#bbc9cd]'}`}>
                      <span>RELEVANCE</span>
                      <span>94%</span>
                    </div>
                    <div className="h-1 w-full bg-[#25d9f5]/10 rounded-full overflow-hidden">
                      <div className="h-full bg-[#25d9f5] rounded-full" style={{ width: '94%' }}></div>
                    </div>
                  </div>
                  <div className="space-y-0.5">
                    <div className={`flex justify-between text-[11px] font-['Poppins'] font-medium transition-all ${hoveredSegment?.label === 'Completeness' ? 'text-purple-400 scale-[1.02]' : 'text-[#bbc9cd]'}`}>
                      <span>COMPLETENESS</span>
                      <span>92%</span>
                    </div>
                    <div className="h-1 w-full bg-[#25d9f5]/10 rounded-full overflow-hidden">
                      <div className="h-full bg-[#25d9f5] rounded-full" style={{ width: '92%' }}></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <div className="flex items-center justify-between bg-[hsl(var(--theme-color)/0.3)] backdrop-blur-md border border-[hsl(var(--theme-color)/0.4)] rounded-lg px-3 py-2 transition-all duration-300 group-hover:bg-[hsl(var(--theme-color)/0.5)] group-hover:border-[hsl(var(--theme-color)/0.6)]">
                <span className="text-xs font-semibold tracking-wide text-[#25d9f5]">Quality Metrics</span>
                <ArrowRight className="h-3.5 w-3.5 text-[#25d9f5] transform transition-transform duration-300 group-hover:translate-x-1" />
              </div>
            </div>
          </div>

          {/* Pipeline Latency Card (DestinationCard styling) */}
          <div
            style={{ "--theme-color": "262 80% 10%" }}
            className="group w-full relative rounded-2xl overflow-hidden shadow-lg transition-all duration-500 ease-in-out hover:scale-[1.02] hover:shadow-[0_0_50px_-10px_hsl(var(--theme-color)/0.8)] border border-[#25d9f5]/15 bg-[#0a1928]/60"
          >
            {/* Background Image with Parallax Zoom */}
            <div
              className="absolute inset-0 bg-cover bg-center opacity-30 transition-transform duration-500 ease-in-out group-hover:scale-110"
              style={{ backgroundImage: `url('https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop&q=60')` }}
            />
            {/* Gradient Overlay */}
            <div
              className="absolute inset-0"
              style={{
                background: `linear-gradient(to top, hsl(var(--theme-color) / 0.98), hsl(var(--theme-color) / 0.8) 40%, transparent 95%)`,
              }}
            />

            {/* Content */}
            <div className="relative z-10 p-5 md:p-6 flex flex-col justify-between h-full text-white space-y-4">
              <div>
                <div className="flex items-center justify-between">
                  <h3 className="font-['JetBrains_Mono'] text-[#d9e3f7] tracking-wider font-semibold text-sm">LATENCY</h3>
                </div>

                <div className="space-y-1.5 pt-1">
                  <div className="flex justify-between items-center py-1 border-b border-[#25d9f5]/10">
                    <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">SPEECH TO TEXT</span>
                    <span className="font-['JetBrains_Mono'] text-[10px] text-[#d9e3f7]">{t.stt_ms.toFixed(0)} ms</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-[#25d9f5]/10">
                    <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">VECTOR/DEMO MATCH</span>
                    <span className="font-['JetBrains_Mono'] text-[10px] text-[#d9e3f7]">{t.matching_ms.toFixed(0)} ms</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-[#25d9f5]/10">
                    <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]">GEMINI FALLBACK</span>
                    <span className="font-['JetBrains_Mono'] text-[10px] text-[#d9e3f7]">{t.gemini_ms > 0 ? `${t.gemini_ms.toFixed(0)} ms` : '—'}</span>
                  </div>
                  <div className="flex justify-between items-center py-1">
                    <span className="font-['JetBrains_Mono'] text-[10px] text-[#25d9f5] font-bold">TOTAL LATENCY</span>
                    <span className="font-['JetBrains_Mono'] text-[12px] text-[#25d9f5] font-bold glow-text">{t.total_ms.toFixed(0)} ms</span>
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <div className="flex items-center justify-between bg-[hsl(var(--theme-color)/0.3)] backdrop-blur-md border border-[hsl(var(--theme-color)/0.4)] rounded-lg px-3 py-2 transition-all duration-300 group-hover:bg-[hsl(var(--theme-color)/0.5)] group-hover:border-[hsl(var(--theme-color)/0.6)]">
                <span className="text-xs font-semibold tracking-wide text-purple-400">Latency Details</span>
                <ArrowRight className="h-3.5 w-3.5 text-purple-400 transform transition-transform duration-300 group-hover:translate-x-1" />
              </div>
            </div>
          </div>

        </div>

        <div className="flex items-center gap-3 pt-4">
          <div className="w-2 h-2 rounded-full bg-[#25d9f5] shadow-[0_0_8px_#25d9f5]"></div>
          <span className="font-['JetBrains_Mono'] text-[11px] text-[#25d9f5] tracking-widest">SYSTEM PERFORMANCE: OPTIMAL</span>
        </div>
      </div>
    </section>
  );
}
