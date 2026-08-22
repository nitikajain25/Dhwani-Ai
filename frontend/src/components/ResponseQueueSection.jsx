import React from 'react';

export default function ResponseQueueSection({ queueRef, responses = [] }) {
  const latestResponse = responses.length > 0 ? responses[0] : null;

  return (
    <section id="response-queue" ref={queueRef} className="snap-start relative w-full min-h-fit lg:min-h-screen flex flex-col items-center justify-center overflow-hidden py-12 md:py-24 bg-[#081525]">
      <div className="relative z-10 flex flex-col items-center w-full max-w-5xl mx-auto px-6 space-y-12">
        {/* Header */}
        <div className="flex flex-col items-center text-center space-y-4">
          <span className="font-['JetBrains_Mono'] text-[12px] text-[#25d9f5] tracking-[0.2em]">03 / RESPONSE QUEUE</span>
          <h2 className="font-['Sora'] font-bold text-[36px] md:text-[56px] leading-[1.1] text-[#d9e3f7]">
            Finding Your <span className="text-gradient">Answer</span>
          </h2>
          <p className="font-['Hanken_Grotesk'] text-[#bbc9cd]/70 max-w-[600px]">
            Dhwani retrieves the most relevant context before generating a grounded response.
          </p>
        </div>

        {/* Live Query Bar */}
        <div className="w-full max-w-3xl glass-panel p-4 rounded-xl flex flex-col md:flex-row items-start md:items-center justify-between border-[#25d9f5]/30 shadow-[0_0_20px_rgba(37,217,245,0.1)] gap-4">
          <div className="flex items-center gap-4">
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#25d9f5] bg-[#25d9f5]/10 px-2 py-1 rounded">VOICE QUERY</span>
            <p className="font-['Hanken_Grotesk'] text-[#d9e3f7] text-left">
              "{latestResponse ? latestResponse.transcript : 'Waiting for voice input...'}"
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${latestResponse ? 'bg-[#25d9f5]' : 'bg-[#bbc9cd]/30'} animate-pulse`}></div>
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#25d9f5] tracking-widest">
              {latestResponse ? 'PROCESSED' : 'IDLE'}
            </span>
          </div>
        </div>

        {/* Technical Pipeline */}
        <div className="flex items-center justify-center space-x-4 md:space-x-8 w-full">
          <div className="flex flex-col items-center gap-1">
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]/40">QUERY</span>
          </div>
          <div className="h-[1px] w-8 bg-[#3c494c]"></div>
          <div className="flex flex-col items-center gap-1">
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#25d9f5] font-bold glow-text">RANK</span>
            <div className="w-1 h-1 rounded-full bg-[#25d9f5]"></div>
          </div>
          <div className="h-[1px] w-8 bg-[#3c494c]"></div>
          <div className="flex flex-col items-center gap-1">
            <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]/40">SELECT</span>
          </div>
        </div>

        {/* Response Grid */}
        <div className="grid grid-cols-1 w-full max-w-3xl text-left gap-6">
          {latestResponse && (
            <div className={`glass-panel p-6 rounded-2xl flex flex-col space-y-4 transition-all hover:scale-[1.02] ${latestResponse.mode === 'demo' ? 'border-[#25d9f5]/50 shadow-[0_0_30px_rgba(37,217,245,0.2)] bg-[#0a1928]/80' : 'border-[#d925f5]/50 shadow-[0_0_30px_rgba(217,37,245,0.2)] bg-[#190a28]/80'}`}>
              <div className="flex justify-between items-start">
                <div className="flex flex-col">
                  <span className={`font-['JetBrains_Mono'] text-[10px] ${latestResponse.mode === 'demo' ? 'text-[#25d9f5]' : 'text-[#d925f5]'}`}>
                    {latestResponse.mode === 'demo' ? '01 / CORPUS ANSWER' : '01 / GEMINI FALLBACK'}
                  </span>
                  <span className="font-['JetBrains_Mono'] text-[12px] text-[#d9e3f7] font-bold">
                    {latestResponse.mode === 'demo' ? 'PREDEFINED MATCH' : 'MODEL KNOWLEDGE'}
                  </span>
                </div>
                <span className={`font-['JetBrains_Mono'] text-[12px] font-bold ${latestResponse.mode === 'demo' ? 'text-[#25d9f5]' : 'text-[#d925f5]'}`}>
                  {latestResponse.mode === 'demo' ? '100%' : 'N/A'}
                </span>
              </div>
              <p className="font-['Hanken_Grotesk'] text-[#bbc9cd] text-sm leading-relaxed">
                {latestResponse.answer}
              </p>
              <div className={`pt-4 border-t flex justify-between items-center ${latestResponse.mode === 'demo' ? 'border-[#25d9f5]/10' : 'border-[#d925f5]/10'}`}>
                <span className="font-['JetBrains_Mono'] text-[10px] text-[#bbc9cd]/60">
                  TOTAL LATENCY: {latestResponse.telemetry?.demo ? (latestResponse.telemetry.actual?.gemini_ms > 0 ? latestResponse.telemetry.demo.overall_ms : latestResponse.telemetry.demo.overall_ms - latestResponse.telemetry.demo.generation_ms).toFixed(0) : 0} ms
                </span>
                <span className={`font-['JetBrains_Mono'] text-[10px] ${latestResponse.mode === 'demo' ? 'text-[#25d9f5]' : 'text-[#d925f5]'}`}>
                  {latestResponse.mode === 'demo' ? 'DEMO DATASET' : 'LLM FALLBACK'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Verification Footer */}
        <div className="flex flex-col items-center gap-2 pt-8">
          <div className="flex items-center gap-2 text-[#25d9f5]">
            <i className="bi bi-patch-check-fill text-xl"></i>
            <span className="font-['JetBrains_Mono'] text-[12px] tracking-widest">CONTEXT VERIFIED</span>
          </div>
          <span className="font-['Hanken_Grotesk'] text-[#bbc9cd]/60 text-sm">Grounded response ready</span>
          <i className="bi bi-chevron-double-down text-[#25d9f5]/40 text-xl animate-bounce mt-4"></i>
        </div>
      </div>
    </section>
  );
}
