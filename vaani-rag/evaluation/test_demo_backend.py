import os
import sys
import time
import json
import unittest.mock
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import dotenv
dotenv.load_dotenv()

def print_result(num, name, status):
    print(f"[{num}] {name:<28} {'PASS' if status else 'FAIL'}")

def main():
    print("============================================================")
    print("DHAWANI DEMO BACKEND TEST")
    print("============================================================\n")
    
    results = {}
    actual_latency = {}
    demo_latency = {}
    
    # ------------------------------------------------------------
    # TEST 1 - ENVIRONMENT
    # ------------------------------------------------------------
    try:
        sarvam_key = os.getenv("SARVAM_API_KEY")
        assert sarvam_key is not None, "SARVAM_API_KEY is missing"
        import sarvamai
        results[1] = True
    except Exception as e:
        print(f"Test 1 Failed: {e}")
        results[1] = False
        
    # ------------------------------------------------------------
    # TEST 2 - DEMO Q&A DATA
    # ------------------------------------------------------------
    try:
        from backend.data.demo_questions import DEMO_QA
        assert len(DEMO_QA) >= 4, "Not enough demo questions"
        for q in DEMO_QA:
            assert "id" in q and "question" in q and "answer" in q and "language" in q
            assert q["answer"].strip() != ""
            
        print("DEMO QUESTIONS")
        print("--------------")
        for i, q in enumerate(DEMO_QA[:4]):
            print(f"Q{i+1}: {q['question']}")
        print("")
        results[2] = True
    except Exception as e:
        print(f"Test 2 Failed: {e}")
        results[2] = False
        
    # ------------------------------------------------------------
    # TEST 3 - EXACT MATCH
    # ------------------------------------------------------------
    try:
        from backend.services.demo_matcher import match_demo_question
        exact_q = DEMO_QA[0]["question"]
        match = match_demo_question(exact_q)
        assert match is not None
        assert match["id"] == DEMO_QA[0]["id"]
        assert match["answer"] == DEMO_QA[0]["answer"]
        results[3] = True
    except Exception as e:
        print(f"Test 3 Failed: {e}")
        results[3] = False
        
    # ------------------------------------------------------------
    # TEST 4 - FUZZY MATCH (MINOR VARIATION)
    # ------------------------------------------------------------
    try:
        original = DEMO_QA[0]["question"]
        variation = "What is the definition of " + original.replace("What is ", "").replace("?", "")
        match = match_demo_question(variation)
        assert match is not None
        assert match["id"] == DEMO_QA[0]["id"]
        
        print(f"Original question: {original}")
        print(f"Test variation:    {variation}")
        print(f"Match:             {match['question']}")
        print(f"Score:             (Threshold logic passed)\n")
        results[4] = True
    except Exception as e:
        print(f"Test 4 Failed: {e}")
        results[4] = False
        
    # ------------------------------------------------------------
    # TEST 5 - UNKNOWN QUESTION
    # ------------------------------------------------------------
    try:
        unknown_q = "What is the population of Japan?"
        match = match_demo_question(unknown_q)
        assert match is None
        results[5] = True
    except Exception as e:
        print(f"Test 5 Failed: {e}")
        results[5] = False
        
    # ------------------------------------------------------------
    # TEST 6 - GEMINI NOT CALLED
    # ------------------------------------------------------------
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        # Monkeypatch the entire google genai module just in case
        with unittest.mock.patch.dict('sys.modules', {'google.genai': unittest.mock.MagicMock(side_effect=Exception("GEMINI INVOKED!"))}):
            client = TestClient(app)
            r = client.post("/api/demo/text", json={"question": DEMO_QA[0]["question"]})
            assert r.status_code == 200
            assert r.json()["success"] == True
            
        results[6] = True
    except Exception as e:
        print(f"Test 6 Failed: {e}")
        results[6] = False
        
    # ------------------------------------------------------------
    # TEST 7 - SARVAM STT
    # ------------------------------------------------------------
    audio_file = "test_match_audio.wav" if Path("test_match_audio.wav").exists() else "test_out.wav"
    try:
        if Path(audio_file).exists():
            from backend.services.sarvam_service import get_sarvam_service
            sarvam = get_sarvam_service()
            with open(audio_file, "rb") as f:
                ab = f.read()
            tx, lang, lat = sarvam.transcribe(ab, language_code="en-IN")
            
            print(f"STT Success: {'True' if tx else 'False (Empty/Silent Audio)'}")
            print(f"Transcript: {tx}")
            print(f"Language: {lang}")
            print(f"Actual STT Latency: {lat:.2f} ms\n")
            results[7] = True
        else:
            print(f"Test 7 Skipped: {audio_file} not found")
            results[7] = False
    except Exception as e:
        print(f"Test 7 Failed: {e}")
        results[7] = False
        
    # ------------------------------------------------------------
    # TEST 8 - SARVAM TTS
    # ------------------------------------------------------------
    try:
        sarvam = get_sarvam_service()
        audio_out, lat = sarvam.synthesize(DEMO_QA[0]["answer"], language_code="en-IN")
        assert len(audio_out) > 0
        with open("evaluation/test_demo_output.wav", "wb") as f:
            f.write(audio_out)
        results[8] = True
    except Exception as e:
        print(f"Test 8 Failed: {e}")
        results[8] = False
        
    # ------------------------------------------------------------
    # TEST 9 - DEMO TEXT API
    # ------------------------------------------------------------
    try:
        client = TestClient(app)
        r = client.post("/api/demo/text", json={"question": DEMO_QA[0]["question"]})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] == True
        assert data["mode"] == "demo"
        assert data["question_id"] == DEMO_QA[0]["id"]
        assert data["answer"] == DEMO_QA[0]["answer"]
        assert "telemetry" in data
        results[9] = True
    except Exception as e:
        print(f"Test 9 Failed: {e}")
        results[9] = False
        
    # ------------------------------------------------------------
    # TEST 10 - DEMO VOICE API
    # ------------------------------------------------------------
    try:
        if Path(audio_file).exists():
            with open(audio_file, "rb") as f:
                r = client.post("/api/demo/voice", files={"file": (audio_file, f, "audio/wav")})
            assert r.status_code == 200
            meta = json.loads(r.headers["X-RAG-Metadata"])
            assert meta["success"] == True
            assert meta["answer"] != ""
            assert "telemetry" in meta
            
            actual_latency = meta["telemetry"]["actual"]
            demo_latency = meta["telemetry"]["demo"]
            results[10] = True
        else:
            results[10] = False
    except Exception as e:
        print(f"Test 10 Failed: {e}")
        results[10] = False
        
    # ------------------------------------------------------------
    # TEST 11 - ACTUAL TELEMETRY
    # ------------------------------------------------------------
    try:
        assert "stt_ms" in actual_latency
        assert "matching_ms" in actual_latency
        assert "tts_ms" in actual_latency
        assert "total_ms" in actual_latency
        assert actual_latency["stt_ms"] >= 0
        assert actual_latency["total_ms"] >= 0
        results[11] = True
    except Exception as e:
        print(f"Test 11 Failed: {e}")
        results[11] = False
        
    # ------------------------------------------------------------
    # TEST 12 - DEMO BENCHMARK TELEMETRY
    # ------------------------------------------------------------
    try:
        assert demo_latency["is_simulated"] == True
        assert 140 < demo_latency["overall_ms"] <= 200
        assert demo_latency["target_ms"] == 200
        assert "extraction_ms" in demo_latency
        assert "matching_ms" in demo_latency
        assert "answer_ms" in demo_latency
        assert "generation_ms" in demo_latency
        results[12] = True
    except Exception as e:
        print(f"Test 12 Failed: {e}")
        results[12] = False
        
    # ------------------------------------------------------------
    # TEST 13 - TELEMETRY SEPARATION
    # ------------------------------------------------------------
    try:
        # Verify actual was not overridden by the hardcoded 200ms demo target
        assert actual_latency["total_ms"] != demo_latency["overall_ms"]
        results[13] = True
    except Exception as e:
        print(f"Test 13 Failed: {e}")
        results[13] = False
        
    # ------------------------------------------------------------
    # TEST 14 - RAG INDEPENDENCE
    # ------------------------------------------------------------
    try:
        # The fact we could boot main.app and run these endpoints without crashing proves this
        from main import _rag_pipeline
        assert _rag_pipeline is None, "RAG pipeline was unexpectedly initialized"
        results[14] = True
    except Exception as e:
        print(f"Test 14 Failed: {e}")
        results[14] = False
        
    # ------------------------------------------------------------
    # TEST 15 - EXISTING IMPORTS
    # ------------------------------------------------------------
    try:
        from ingestion.embedder import BGEM3Embedder
        from ingestion.retriever import QdrantRetriever
        from ingestion.rag_pipeline import RAGBaselinePipeline
        results[15] = True
    except Exception as e:
        print(f"Test 15 Failed: {e}")
        results[15] = False

    # ------------------------------------------------------------
    # PRINT RESULTS
    # ------------------------------------------------------------
    tests = [
        "Environment", "Demo Q&A Data", "Exact Match", "Fuzzy Match",
        "Unknown Question", "Gemini Not Called", "Sarvam STT", "Sarvam TTS",
        "Demo Text API", "Demo Voice API", "Actual Telemetry",
        "Demo Benchmark Telemetry", "Telemetry Separation", "Model Independence",
        "Existing Imports"
    ]
    
    print("============================================================")
    print("DHAWANI DEMO BACKEND TEST")
    print("============================================================\n")
    for i, name in enumerate(tests):
        print_result(i+1, name, results.get(i+1, False))
        
    print("\n============================================================")
    print("LATENCY")
    print("============================================================")
    
    if actual_latency:
        print(f"Actual STT:          {actual_latency.get('stt_ms', 0):.2f} ms")
        print(f"Actual Matching:      {actual_latency.get('matching_ms', 0):.2f} ms")
        print(f"Actual Answer:        {actual_latency.get('answer_ms', 0):.2f} ms")
        print(f"Actual TTS:         {actual_latency.get('tts_ms', 0):.2f} ms")
        print(f"Actual Total:       {actual_latency.get('total_ms', 0):.2f} ms\n")
    else:
        print("Actual Telemetry:   MISSING\n")
        
    if demo_latency:
        print("Demo Benchmark:")
        print(f"Extraction:           {demo_latency.get('extraction_ms')} ms")
        print(f"Matching:             {demo_latency.get('matching_ms')} ms")
        print(f"Answer:               {demo_latency.get('answer_ms')} ms")
        print(f"Generation:           {demo_latency.get('generation_ms')} ms")
        print(f"Overall:             {demo_latency.get('overall_ms')} ms")
        print(f"Target:              <{demo_latency.get('target_ms')} ms\n")
    
    print("IMPORTANT:")
    print("Demo benchmark values are simulated/target values and are NOT")
    print("actual measured latency.\n")
    
    print("============================================================")
    all_passed = all(results.get(i+1, False) for i in range(len(tests)))
    if all_passed:
        print("PASS")
    else:
        print("FAIL")
        for i, name in enumerate(tests):
            if not results.get(i+1, False):
                print(f"-> Failed Test [{i+1}] {name}")
                
    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()

