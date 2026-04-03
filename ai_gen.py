import os
import re
import env_loader

GROQ_KEY_FILE = "D:\\groq_key.txt"   # legacy fallback

def _get_key():
    # 1. Try .env first
    key = env_loader.get("GROQ_API_KEY")
    if key and key != "your_groq_api_key_here":
        return key
    # 2. Fall back to old key file
    if os.path.exists(GROQ_KEY_FILE):
        return open(GROQ_KEY_FILE).read().strip()
    return None

def set_key(api_key):
    api_key = api_key.strip()
    # Save to both .env and legacy file
    env_loader.set_value("GROQ_API_KEY", api_key)
    with open(GROQ_KEY_FILE, 'w') as f:
        f.write(api_key)
    print("Groq API key saved to .env")

def ai_gen(prompt, filepath):
    from file_ops import safe_path
    from groq import Groq

    key = _get_key()
    if not key:
        print("No API key found. Run: ai setkey <your_groq_api_key>")
        return

    p = safe_path(filepath)
    print(f"Generating code for: {prompt}")

    client = Groq(api_key=key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a code generator. Return ONLY raw code with no explanation, no markdown, no code fences. Just the code itself."},
            {"role": "user", "content": prompt}
        ]
    )

    code = response.choices[0].message.content.strip()
    # Strip markdown code fences if model returns them anyway
    code = re.sub(r'^```[\w]*\n?', '', code)
    code = re.sub(r'\n?```$', '', code)

    os.makedirs(os.path.dirname(p) or "D:\\", exist_ok=True)
    with open(p, 'w') as f:
        f.write(code)

    print(f"Code written to: {p}")
    print(f"--- Preview (first 5 lines) ---")
    for line in code.splitlines()[:5]:
        print(f"  {line}")

def ai_ask(prompt):
    from groq import Groq

    key = _get_key()
    if not key:
        print("No API key found. Run: ai setkey <your_groq_api_key>")
        return

    client = Groq(api_key=key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    print(response.choices[0].message.content.strip())
