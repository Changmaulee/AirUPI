"""
Live Test & Demonstration of Project Brahmand:
1. Autonomous Real-time Learning from Text (Zero GPU hours).
2. Thinker Ground-Truth & Exact ALU Execution (0% Hallucination).
3. Fluid Multi-Lingual Speaker Articulation.
"""

import time
from brahmand_pipeline import BrahmandPipeline

def run_pipeline_demo():
    print("=" * 80)
    print(" [PROJECT BRAHMAND: AUTONOMOUS SOVEREIGN LLM PIPELINE DEMO]")
    print("=" * 80)
    
    pipeline = BrahmandPipeline()
    
    # --- DEMO 1: Exact ALU Math & Hinglish Query ---
    q1 = "18 ande me kitna protein hoga?"
    res1 = pipeline.ask(q1)
    print(f"\nQuery 1 (Hinglish Math): '{q1}'")
    print(f"Answer: {res1['answer']}")
    print(f"Latency: {res1['latency_ms']:.3f} ms | Hallucination: {res1['hallucination_rate']} | Multipliers: {res1['hardware_multipliers']}")
    
    # --- DEMO 2: English Technical Avionics Query ---
    q2 = "What is the B737 hydraulic pressure?"
    res2 = pipeline.ask(q2)
    print(f"\nQuery 2 (Avionics Technical): '{q2}'")
    print(f"Answer: {res2['answer']}")
    print(f"Latency: {res2['latency_ms']:.3f} ms | Hallucination: {res2['hallucination_rate']} | Multipliers: {res2['hardware_multipliers']}")

    # --- DEMO 3: Autonomous Real-Time Learning from Internet / Docs (<5ms on CPU) ---
    print("\n" + "-" * 80)
    print(" [DEMO 3: AUTONOMOUS REAL-TIME LEARNING (0 GPU Training Hours)]")
    print("-" * 80)
    new_doc = """
    Quantum Computing is defined as computation using quantum mechanical phenomena.
    Qubit coherence time is 150 microseconds.
    Sycamore quantum processor operates at 15 millikelvin.
    """
    print("Teaching new topic: 'Quantum Computing' from text...")
    learn_res = pipeline.learn_topic("Quantum Computing", new_doc)
    print(f"Learned {learn_res['sentence_count']} facts in {learn_res['compile_time_ms']:.2f} ms on CPU!")
    
    # Query the newly learned topic immediately
    q3 = "What is the qubit coherence time for 4 qubits?"
    res3 = pipeline.ask(q3)
    print(f"\nImmediate Query on New Topic: '{q3}'")
    print(f"Answer: {res3['answer']}")
    print(f"Latency: {res3['latency_ms']:.3f} ms | Hallucination: {res3['hallucination_rate']} | Multipliers: {res3['hardware_multipliers']}")
    print("=" * 80)

if __name__ == '__main__':
    run_pipeline_demo()
