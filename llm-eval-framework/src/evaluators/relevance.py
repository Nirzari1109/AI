import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def score_relevance(question: str, actual: str) -> float:
    """
    Scores how relevant the actual answer is to the question.
    Returns a float between 0 and 1.
    """
    prompt = f"""You are an expert evaluator for AI systems.
Score how relevant the ANSWER is to the QUESTION asked.

QUESTION: {question}

ANSWER: {actual}

Scoring criteria:
5 = Directly and completely answers the question
4 = Mostly answers the question with minor tangents
3 = Partially answers, somewhat off-topic
2 = Mostly irrelevant to the question
1 = Completely irrelevant or refuses to answer

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
        return round(score / 5.0, 2)
    except Exception as e:
        print(f"Relevance scoring error: {e}")
        return 0.5