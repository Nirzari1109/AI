import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def score_faithfulness(question: str, expected: str, actual: str) -> float:
    """
    LLM-as-judge: scores how faithful the actual answer is
    to the expected answer. Returns a float between 0 and 1.
    """
    prompt = f"""You are an expert evaluator for AI systems.
Score the faithfulness of the ACTUAL answer compared to the EXPECTED answer.

QUESTION: {question}

EXPECTED ANSWER: {expected}

ACTUAL ANSWER: {actual}

Scoring criteria:
5 = Actual answer is completely faithful, covers all key points
4 = Mostly faithful, minor omissions
3 = Partially faithful, some key points missing
2 = Mostly unfaithful, major points missing or wrong
1 = Completely wrong or hallucinated

Reply with ONLY a single integer: 1, 2, 3, 4, or 5. Nothing else."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0
        )
        score_str = response.choices[0].message.content.strip()
        score = int(score_str)
        if score < 1 or score > 5:
            score = 3
        return round(score / 5.0, 2)  # normalise to 0–1
    except Exception as e:
        print(f"Faithfulness scoring error: {e}")
        return 0.5  # default on error