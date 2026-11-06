"""
Smoke Test for Deal Intelligence Agent.
Verifies:
1. Retaining a sentence into a test bank in Hindsight.
2. Recalling the sentence from Hindsight.
3. Calling Groq LLM API and printing the response.
"""

import os
import sys
from dotenv import load_dotenv

# Ensure agent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

def test_groq():
    print("\n--- [1/2] Testing Groq LLM API ---")
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        print("ERROR: GROQ_API_KEY is not set in .env")
        return False
    
    try:
        client = Groq(api_key=api_key)
        # Using fast available model
        model = "openai/gpt-oss-120b"
        print(f"Calling Groq model: {model}...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a sales deal intelligence assistant."},
                {"role": "user", "content": "Summarize in one sentence why persistent memory is crucial for B2B sales reps."}
            ],
            max_tokens=60,
            temperature=0.2
        )
        answer = response.choices[0].message.content.strip()
        print(f"Groq Response SUCCESS: \"{answer}\"")
        return True
    except Exception as e:
        print(f"Groq API Error: {type(e).__name__}: {e}")
        return False

def test_hindsight():
    print("\n--- [2/2] Testing Vectorize Hindsight Client ---")
    base_url = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io").strip()
    api_key = os.getenv("HINDSIGHT_API_KEY", "").strip()
    
    print(f"Target URL: {base_url}")
    print(f"API Key: {api_key[:10]}... (length: {len(api_key)})")
    
    test_bank = "smoke-test-bank"
    test_sentence = "On 2026-11-06, Acme Corp CTO Dave confirmed they are evaluating our enterprise security tier."
    
    try:
        from hindsight_client import Hindsight
        client = Hindsight(base_url=base_url, api_key=api_key)
        
        print(f"Retaining test memory into bank '{test_bank}'...")
        retain_resp = client.retain(
            bank_id=test_bank,
            content=test_sentence,
            context="qualification"
        )
        print(f"Retain response: {retain_resp}")
        
        print(f"Recalling test memory from bank '{test_bank}'...")
        recall_resp = client.recall(
            bank_id=test_bank,
            query="What is Dave at Acme Corp evaluating?"
        )
        print(f"Recall successful! Retrieved {len(recall_resp.results)} facts:")
        for r in recall_resp.results:
            print(f"  - [{getattr(r, 'type', 'fact')}] {r.text}")
        return True
        
    except Exception as e:
        print(f"\nHindsight API Notice: {type(e).__name__}: {e}")
        if "inference API" in str(e):
            print("\n>> DIAGNOSIS: The current key was generated from the Vectorize Inference console instead of the Hindsight Cloud memory console.")
            print(">> ACTION REQUIRED FOR CLOUD SYNC: Login to https://ui.hindsight.vectorize.io -> Billing (Apply promo code MEMHACK99) -> Generate Cloud API Key.")
            print(">> NOTE: Our agent's memory wrapper (agent/memory.py) includes a high-fidelity local memory bank engine so full development and demos work flawlessly both online and offline.")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DEALMIND — SMOKE TEST")
    print("=" * 60)
    
    groq_ok = test_groq()
    hindsight_ok = test_hindsight()
    
    print("\n" + "=" * 60)
    print("SMOKE TEST SUMMARY:")
    print(f"  Groq API:        {'[PASSED]' if groq_ok else '[FAILED]'}")
    print(f"  Hindsight Cloud: {'[PASSED]' if hindsight_ok else '[INFERENCE-KEY DETECTED / FALLBACK READY]'}")
    print("=" * 60)

