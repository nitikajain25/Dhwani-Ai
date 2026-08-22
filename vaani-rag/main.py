from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
from fastapi.middleware.cors import CORSMiddleware

frontend_url = os.getenv("FRONTEND_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url] if frontend_url else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI(title="Dhawani API")

class QueryRequest(BaseModel):
    query: str
    language: str = "en"
    top_k: int = 5

class LatencyInfo(BaseModel):
    embedding_ms: float
    retrieval_ms: float
    reranking_ms: float
    context_prep_ms: float
    gemini_generation_ms: float
    total_ms: float
    stt_ms: Optional[float] = None
    tts_ms: Optional[float] = None

class QueryResponse(BaseModel):
    success: bool
    query: str
    answer: str
    sources: List[str]
    latency: LatencyInfo
    detected_language: Optional[str] = None

_rag_pipeline = None

def get_rag_pipeline():
    global _rag_pipeline
    if _rag_pipeline is None:
        project_root = Path(__file__).resolve().parent
        embedder_path = project_root / "models" / "bge-m3-openvino"
        reranker_path = project_root / "models" / "bge-reranker-v2-m3-openvino"
        
        if not embedder_path.exists():
            raise HTTPException(status_code=503, detail="Embedding model is not available")
        
        from ingestion.rag_pipeline import RAGBaselinePipeline
        from ingestion.embedder import BGEM3Embedder
        from ingestion.reranker import BGEM3Reranker
        
        embedder = BGEM3Embedder()
        reranker = None
        if reranker_path.exists():
            reranker = BGEM3Reranker()
            
        _rag_pipeline = RAGBaselinePipeline(embedder=embedder, reranker=reranker)
        
    return _rag_pipeline

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Dhawani"}

@app.post("/api/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    try:
        pipeline = get_rag_pipeline()
    except HTTPException as e:
        return JSONResponse(status_code=503, content={"success": False, "error": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})
        
    res = pipeline.generate_answer(
        query=request.query,
        language=request.language,
        top_k=request.top_k
    )
    
    return QueryResponse(
        success=res.success,
        query=res.query,
        answer=res.answer,
        sources=res.sources,
        latency=LatencyInfo(
            embedding_ms=res.telemetry.embedding_ms,
            retrieval_ms=res.telemetry.retrieval_ms,
            reranking_ms=res.telemetry.reranking_ms,
            context_prep_ms=res.telemetry.context_prep_ms,
            gemini_generation_ms=res.telemetry.gemini_generation_ms,
            total_ms=res.telemetry.total_ms
        )
    )

@app.post("/api/voice")
async def voice_rag(file: UploadFile = File(...), top_k: int = Form(5)):
    try:
        pipeline = get_rag_pipeline()
    except HTTPException as e:
        return JSONResponse(status_code=503, content={"success": False, "error": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})
        
    from backend.services.sarvam_service import get_sarvam_service
    try:
        sarvam = get_sarvam_service()
    except ValueError as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})
        
    # 1. STT
    audio_bytes = await file.read()
    transcript, detected_lang, stt_ms = sarvam.transcribe(audio_bytes, language_code="unknown")
    if not transcript:
         return JSONResponse(status_code=400, content={"success": False, "error": "Transcription failed."})
         
    # 2. RAG
    # Map Sarvam language code to RAG language code if needed (e.g. hi-IN -> hi)
    rag_lang = detected_lang.split("-")[0] if detected_lang and "-" in detected_lang else (detected_lang or "en")
    
    res = pipeline.generate_answer(
        query=transcript,
        language=rag_lang,
        top_k=top_k
    )
    
    # 3. TTS
    audio_out, tts_ms = sarvam.synthesize(text=res.answer, language_code=detected_lang or "hi-IN")
    
    # We return audio output and include headers for JSON metadata
    import json
    metadata = {
        "success": res.success,
        "query": res.query,
        "answer": res.answer,
        "sources": res.sources,
        "detected_language": detected_lang,
        "latency": {
            "stt_ms": stt_ms,
            "embedding_ms": res.telemetry.embedding_ms,
            "retrieval_ms": res.telemetry.retrieval_ms,
            "reranking_ms": res.telemetry.reranking_ms,
            "context_prep_ms": res.telemetry.context_prep_ms,
            "gemini_generation_ms": res.telemetry.gemini_generation_ms,
            "tts_ms": tts_ms,
            "total_ms": res.telemetry.total_ms
        }
    }
    
    return Response(
        content=audio_out,
        media_type="audio/wav",
        headers={"X-RAG-Metadata": json.dumps(metadata)}
    )

# ============================================================
# DEMO MODE ENDPOINTS
# ============================================================
from backend.services.demo_matcher import match_demo_question
import time
import json
import random

def get_demo_benchmark_telemetry():
    ext = random.randint(120, 150)
    mat = random.randint(20, 35)
    ans = random.randint(20, 35)
    gen = random.randint(80, 110)
    overall = ext + mat + ans + gen
    return {
        "is_simulated": True,
        "extraction_ms": ext,
        "matching_ms": mat,
        "answer_ms": ans,
        "generation_ms": gen,
        "overall_ms": overall,
        "target_ms": 200
    }

class DemoTextRequest(BaseModel):
    question: str

@app.post("/api/demo/text")
def demo_text(request: DemoTextRequest):
    t0 = time.perf_counter()
    transcript = request.question
    
    match_t0 = time.perf_counter()
    match = match_demo_question(transcript)
    match_ms = (time.perf_counter() - match_t0) * 1000.0

    if not match:
        return JSONResponse(status_code=400, content={
            "success": False,
            "mode": "demo",
            "error": "QUESTION_NOT_IN_DEMO_SET",
            "transcript": transcript,
            "answer": None
        })
        
    answer_t0 = time.perf_counter()
    answer = match["answer"]
    answer_ms = (time.perf_counter() - answer_t0) * 1000.0

    total_ms = (time.perf_counter() - t0) * 1000.0
    
    return {
        "success": True,
        "mode": "demo",
        "question_id": match["id"],
        "matched_question": match["question"],
        "transcript": transcript,
        "answer": answer,
        "telemetry": {
            "actual": {
                "stt_ms": 0.0,
                "matching_ms": match_ms,
                "answer_ms": answer_ms,
                "tts_ms": 0.0,
                "total_ms": total_ms
            },
            "demo": get_demo_benchmark_telemetry()
        }
    }

@app.post("/api/demo/voice")
async def demo_voice(file: UploadFile = File(...)):
    total_t0 = time.perf_counter()
    
    from backend.services.sarvam_service import get_sarvam_service
    try:
        sarvam = get_sarvam_service()
    except ValueError as e:
        return JSONResponse(status_code=500, content={"success": False, "mode": "demo", "error": str(e)})
        
    # 1. STT
    audio_bytes = await file.read()
    transcript, detected_lang, stt_ms = sarvam.transcribe(audio_bytes, language_code="en-IN")
    if not transcript:
        return JSONResponse(status_code=400, content={
            "success": False,
            "mode": "demo",
            "error": "Transcription failed.",
            "transcript": transcript,
            "answer": None
        })
         
    # 2. MATCHING
    match_t0 = time.perf_counter()
    match = match_demo_question(transcript)
    match_ms = (time.perf_counter() - match_t0) * 1000.0
    
    answer_ms = 0.0
    gemini_ms = 0.0
    mode = "demo"
    question_id = None
    matched_question = None

    if not match:
        mode = "gemini_fallback"
        # EXISTING GEMINI FALLBACK
        t_gemini = time.perf_counter()
        try:
            from google import genai
            import os
            api_key = os.getenv("GEMINI_API_KEY")
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            client = genai.Client(api_key=api_key)
            gemini_response = client.models.generate_content(
                model=model,
                contents=f"Answer concisely: {transcript}"
            )
            answer = gemini_response.text or "I could not generate a response."
        except Exception as e:
            answer = "Sorry, I encountered an error connecting to Gemini."
        gemini_ms = (time.perf_counter() - t_gemini) * 1000.0
    else:
        answer_t0 = time.perf_counter()
        answer = match["answer"]
        answer_ms = (time.perf_counter() - answer_t0) * 1000.0
        question_id = match["id"]
        matched_question = match["question"]
    
    # 3. TTS
    audio_out, tts_ms = sarvam.synthesize(text=answer, language_code="en-IN")
    
    total_ms = (time.perf_counter() - total_t0) * 1000.0
    
    metadata = {
        "success": True,
        "mode": mode,
        "question_id": question_id,
        "transcript": transcript,
        "matched_question": matched_question,
        "answer": answer,
        "telemetry": {
            "actual": {
                "stt_ms": stt_ms,
                "matching_ms": match_ms,
                "answer_ms": answer_ms,
                "gemini_ms": gemini_ms,
                "tts_ms": tts_ms,
                "total_ms": total_ms
            },
            "demo": get_demo_benchmark_telemetry()
        }
    }
    
    return Response(
        content=audio_out,
        media_type="audio/wav",
        headers={"X-RAG-Metadata": json.dumps(metadata)}
    )
