"""
Euri AI Gateway Integration Probe (Phase 1.14).

Verifies the integration contract specified in docs/INTEGRATIONS-EURI.md:
  - GET /models ( pricing & model availability )
  - POST /embeddings (gemini-embedding-2-preview, 1536 dim, text-only)
  - POST /chat/completions (gpt-4.1)

SAFETY RULES:
  - Prints NO secret values (API keys are masked)
  - Performs NO write or mutation operations
"""

from __future__ import annotations

import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath("backend"))

from app.config import get_settings
from app.euri_client import get_euri_client


async def run_probe() -> None:
    settings = get_settings()
    if not settings.euri_api_key:
        print("[!] ERROR: EURI_API_KEY is not set in environment or backend/.env")
        sys.exit(1)

    print("[*] Probing Euri AI Gateway at:", settings.euri_base_url)
    client = get_euri_client()

    try:
        # 1. Probe Models Endpoint
        print("\n--- 1. Models & Pricing ---")
        models_data = await client.list_models()
        print(f"[OK] Successfully retrieved model catalog ({len(models_data)} models returned)")
        for m in models_data[:5]:
            print(f"    - Model ID: {m.get('id', 'unknown')}")

        # 2. Probe Embedding Model
        print(f"\n--- 2. Embedding ({settings.euri_embedding_model}) ---")
        test_text = "EKBA Euri Gateway Probe Test String"
        vectors = await client.embed([test_text])
        emb = vectors[0] if vectors else []
        print("[OK] Successfully generated embedding vector")
        print(f"    - Vector dimensions: {len(emb)}")
        if len(emb) != settings.euri_embedding_dimensions:
            raise RuntimeError(
                f"Dimension mismatch: {len(emb)} != {settings.euri_embedding_dimensions}"
            )

        # 3. Probe Chat Model
        print(f"\n--- 3. Chat Completion ({settings.euri_generation_model}) ---")
        chat_res = await client.chat(
            messages=[
                {"role": "system", "content": "You are a test assistant. Reply concisely."},
                {"role": "user", "content": "Say 'OK'"},
            ],
            model=settings.euri_generation_model,
            max_tokens=10,
        )
        print(f"[OK] Received chat response: '{chat_res.content.strip()}'")
        print(
            f"    - Usage: prompt={chat_res.prompt_tokens}, completion={chat_res.completion_tokens}"
        )

        print("\n==========================================")
        print("[OK] ALL EURI GATEWAY PROBES PASSED CLEANLY")
        print("==========================================")

    except Exception as err:
        print(f"\n[!] PROBE FAILED: {err}")
        sys.exit(1)
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(run_probe())
