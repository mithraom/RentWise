"""Robust .env loader (handles Windows quirks: UTF-8 BOM, UTF-16 files, '.env.txt' names)."""
import io
import os
from pathlib import Path
from dotenv import dotenv_values

HERE = Path(__file__).resolve().parent


def load_env():
    for name in (".env", ".env.txt"):
        path = HERE / name
        if not path.exists():
            continue
        raw = path.read_bytes()
        text = None
        for enc in ("utf-8-sig", "utf-16"):
            try:
                text = raw.decode(enc)
                break
            except UnicodeError:
                continue
        if text is None:
            print(f"[env] Could not read {path}. Re-save it as UTF-8.")
            return
        for key, value in dotenv_values(stream=io.StringIO(text)).items():
            if value is not None:
                os.environ.setdefault(key.strip(), value.strip())
        print(f"[env] Loaded {path}")
        return
    print(f"[env] No .env file found in {HERE}. Using defaults for local development "
          f"(copy .env.example to .env to change them).")
