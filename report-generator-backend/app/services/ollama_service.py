
import json
import re
import requests

from app.services.retrieval_service import retrieve_relevant_examples


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3.5:4b"


SYSTEM_PROMPT = """
You are an assistant that prepares faculty accomplishment reports
for a university.

Your task is to rewrite raw faculty activity notes into concise,
professional accomplishment statements.

STRICT WRITING RULES:
1. Translate Bisaya, Taglish, or informal English into professional English.
2. Use past tense because the activities have already been completed.
3. Begin directly with an appropriate action verb.
4. Keep the original meaning and all factual details.
5. Do not invent activities, dates, outcomes, participants, or achievements.
6. Preserve official subject names exactly as provided.
7. Do not use phrases such as:
   - "The faculty member..."
   - "The instructor..."
   - "The professor..."
   - "Currently..."
8. Avoid unnecessary explanations and overly elaborate wording.
9. Keep the accomplishment statement concise, preferably one sentence.
10. Historical examples are references for writing style only.
    Never copy their activities or treat them as current activities.

REMARKS RULES:
1. Suggest a short, relevant remark only when it can be supported
   by the supplied activity.
2. Do not invent evidence, outcomes, or accomplishments.
3. If no appropriate remark can be determined, return an empty string.

Return ONLY valid JSON using this exact structure:
{
    "accomplishment": "Rewritten accomplishment statement",
    "remarks": "Suggested remark or empty string"
}
"""


def extract_json_response(response_text: str) -> dict:
    """Extract the JSON object returned by the model."""

    response_text = response_text.strip()

    # Remove Markdown code fences if the model adds them.
    response_text = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        response_text,
        flags=re.IGNORECASE
    ).strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to locate a JSON object within the response.
        match = re.search(r"\{.*\}", response_text, re.DOTALL)

        if not match:
            raise ValueError(
                "The AI returned an invalid response."
            )

        return json.loads(match.group(0))


def generate_accomplishment(
    raw_text: str,
    examples: list[dict] | None = None
) -> dict:
    """
    Rewrite one raw accomplishment note using the local Ollama model.

    Returns:
        {
            "accomplishment": "...",
            "remarks": "..."
        }
    """

    raw_text = raw_text.strip()

    if not raw_text:
        raise ValueError("Accomplishment notes cannot be empty.")

    # Retrieve historical examples if none were supplied.
    if examples is None:
        examples = retrieve_relevant_examples(raw_text)

    example_text = "\n".join(
        f"- {item['text']}"
        for item in examples
    )

    if not example_text:
        example_text = "No relevant historical examples found."

    user_prompt = f"""
RAW ACCOMPLISHMENT NOTES:
{raw_text}

HISTORICAL WRITING REFERENCES:
{example_text}

Rewrite the raw notes according to the system instructions.

Remember:
- Historical examples are not current activities.
- Do not add details that are not in the raw notes.
- Return only the required JSON.
"""

    payload = {
        "model": MODEL_NAME,
        "think": False,
        "stream": False,
        "format": "json",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "options": {
            "temperature": 0.2,
            "num_predict": 200
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=300
        )

        response.raise_for_status()

        result = response.json()
        model_response = result["message"]["content"]

        parsed = extract_json_response(model_response)

        accomplishment = str(
            parsed.get("accomplishment", "")
        ).strip()

        remarks = str(
            parsed.get("remarks", "")
        ).strip()

        if not accomplishment:
            raise ValueError(
                "The AI did not return an accomplishment statement."
            )

        return {
            "accomplishment": accomplishment,
            "remarks": remarks
        }

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Cannot connect to Ollama. Make sure Ollama is running."
        ) from exc

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "The AI model took too long to respond. "
            "Try again or use shorter notes."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Ollama request failed: {exc}"
        ) from exc
