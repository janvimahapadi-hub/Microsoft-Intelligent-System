import json
import os
import re
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

# Default model. You can override it from PowerShell:
# $env:OLLAMA_MODEL="phi3:mini"
# streamlit run app.py
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen3:8b")


def clean_response(text):
    """
    Cleans model output, especially Qwen-style thinking tags.
    """
    if not text:
        return ""

    # Remove Qwen thinking blocks if they appear.
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = text.replace("<think>", "").replace("</think>", "")
    text = text.strip()

    # If the model adds extra preamble, start from the first numbered markdown section.
    if "## 1." in text:
        text = text[text.find("## 1."):]

    return text.strip()


def ask_ollama(
    prompt,
    model_name=MODEL_NAME,
    temperature=0.2,
    num_predict=900,
    num_ctx=4096,
    timeout=900
):
    """
    Calls Ollama using streaming mode.

    Streaming is more reliable than stream=False because the server keeps sending
    partial tokens while generating. This reduces timeout problems in Streamlit.
    """

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
        raise RuntimeError(
            "Ollama timed out before responding."
        )

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

    return clean_response("".join(chunks))


def generate_response(
    system_prompt,
    user_prompt,
    model_name=MODEL_NAME,
    mode="playbook"
):
    """
    mode='fast'      : shorter, faster answer for demo
    mode='playbook'  : deeper strategic answer
    mode='chat'      : follow-up Q&A
    """

    full_prompt = f"""
/no_think

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
        return ask_ollama(
            prompt=full_prompt,
            model_name=model_name,
            temperature=0.2,
            num_predict=1000,
            num_ctx=4096,
            timeout=700
        )

    if mode == "chat":
        return ask_ollama(
            prompt=full_prompt,
            model_name=model_name,
            temperature=0.2,
            num_predict=750,
            num_ctx=3072,
            timeout=600
        )

    return ask_ollama(
        prompt=full_prompt,
        model_name=model_name,
        temperature=0.2,
        num_predict=1600,
        num_ctx=4096,
        timeout=900
    )


if __name__ == "__main__":
    result = ask_ollama(
        "In one sentence, say that the AI CEO Agent is working.",
        num_predict=60
    )
    print(result)