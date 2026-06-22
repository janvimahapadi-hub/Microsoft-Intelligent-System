import json
import os
import re
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

# You can override model from PowerShell:
# $env:OLLAMA_MODEL="llama3.2:3b"
# streamlit run app.py
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen3:8b")

DEBUG_LLM = os.getenv("DEBUG_LLM", "0") == "1"


def clean_response(text):
    if not text:
        return ""

    raw_text = text.strip()

    # Remove Qwen thinking blocks only if there is text outside them.
    without_think = re.sub(
        r"<think>.*?</think>",
        "",
        raw_text,
        flags=re.DOTALL
    ).strip()

    if without_think:
        text = without_think
    else:
        text = raw_text.replace("<think>", "").replace("</think>", "").strip()

    if "## 1." in text:
        trimmed = text[text.find("## 1."):]
        if len(trimmed.strip()) > 30:
            text = trimmed

    return text.strip()


def validate_answer(answer):
    if not answer or len(answer.strip()) < 20:
        raise RuntimeError("LLM returned an empty or too-short response.")

    return answer.strip()


def ask_ollama(
    prompt,
    model_name=MODEL_NAME,
    temperature=0.2,
    num_predict=900,
    num_ctx=4096,
    timeout=900
):
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
            "num_predict": num_predict,
            "num_ctx": num_ctx
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            stream=True,
            timeout=(10, timeout)
        )

    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure Ollama is running on port 11434."
        )

    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama timed out before responding.")

    if response.status_code != 200:
        raise RuntimeError(
            f"Ollama error {response.status_code}: {response.text}"
        )

    chunks = []

    try:
        for line in response.iter_lines():
            if not line:
                continue

            try:
                data = json.loads(line.decode("utf-8"))
            except json.JSONDecodeError:
                continue

            if "response" in data:
                chunks.append(data["response"])

            if data.get("done", False):
                break

    except requests.exceptions.Timeout:
        raise RuntimeError(
            "Ollama started generating but took too long to finish."
        )

    raw_output = "".join(chunks)
    cleaned = clean_response(raw_output)

    if DEBUG_LLM:
        print("\n" + "=" * 100)
        print("RAW LLM OUTPUT")
        print("=" * 100)
        print(raw_output[:3000])
        print("\n" + "=" * 100)
        print("CLEANED LLM OUTPUT")
        print("=" * 100)
        print(cleaned[:3000])
        print("=" * 100)

    return cleaned


def generate_response(
    system_prompt,
    user_prompt,
    model_name=MODEL_NAME,
    mode="playbook"
):
    full_prompt = f"""
{system_prompt}

USER TASK:
{user_prompt}

Rules:
- Use only the provided evidence.
- Do not invent facts.
- Be specific and practical.
- Return the final answer only.
"""

    if mode == "fast":
        answer = ask_ollama(
            prompt=full_prompt,
            model_name=model_name,
            temperature=0.2,
            num_predict=700,
            num_ctx=4096,
            timeout=240
        )
        return validate_answer(answer)

    if mode == "chat":
        answer = ask_ollama(
            prompt=full_prompt,
            model_name=model_name,
            temperature=0.2,
            num_predict=450,
            num_ctx=3072,
            timeout=180
        )
        return validate_answer(answer)

    answer = ask_ollama(
        prompt=full_prompt,
        model_name=model_name,
        temperature=0.2,
        num_predict=1000,
        num_ctx=4096,
        timeout=300
    )
    return validate_answer(answer)


if __name__ == "__main__":
    result = generate_response(
        system_prompt="You are a helpful assistant.",
        user_prompt="In one sentence, say that the AI CEO Agent is working.",
        mode="fast"
    )
    print(result)