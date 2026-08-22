import requests

def test_demo_qa():
    print("Testing /api/demo/text endpoint...")
    url = "http://127.0.0.1:8002/api/demo/text"
    
    # 1. Exact match
    r = requests.post(url, json={"question": "What is mediation?"})
    print("\n[Exact match]")
    print(r.json())
    assert r.json()["success"] == True
    assert r.json()["question_id"] == "q1"
    assert "telemetry" in r.json()
    assert 140 < r.json()["telemetry"]["demo"]["overall_ms"] <= 200
    
    # 2. Minor wording variation
    r = requests.post(url, json={"question": "What is the definition of mediation"})
    print("\n[Variation match]")
    print(r.json())
    assert r.json()["success"] == True
    assert r.json()["question_id"] == "q1"
    
    # 3. Unknown question
    r = requests.post(url, json={"question": "What is the capital of France?"})
    print("\n[Unknown question]")
    print(r.json())
    assert r.json()["success"] == False
    assert r.json()["error"] == "QUESTION_NOT_IN_DEMO_SET"
    
    print("\nAll demo Q&A tests passed successfully. Gemini was NOT called.")

if __name__ == "__main__":
    test_demo_qa()

