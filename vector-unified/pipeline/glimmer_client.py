"""
Glimmer Client — stdlib-only local evaluator for MTNN v9/v4 unified G2/G3

Zero-deps: stdlib only (urllib, json, os, socket)
Never synthetic: fails honest 503 if no local Glimmer endpoint
Honest 503: prints 503 and exits 11 when blocked

Backends tried in order:
  1. Ollama  (http://localhost:11434) — model glimmer / muse-glimmer / meta-glimmer
  2. llama.cpp server (http://localhost:8080)
  3. MLX / ExecuTorch via env GLIMMER_ENDPOINT (generic OpenAI-compatible)
  4. vLLM / SGLang (same OpenAI-compatible)

Usage:
  from glimmer_client import GlimmerClient
  client = GlimmerClient()
  if not client.available:
      client.honest_503("Glimmer not running")
  out = client.generate("Judge this eval", system="You are an MLOps evaluator")

Reasoning effort control via system prompt:
  low / medium / high / xhigh — Glimmer supports controllable reasoning effort
  via system prompt per model card (131k context, 100+ languages, ViT-G/14 1.8B)
"""
from __future__ import annotations

import json
import os
import socket
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any, List

DEFAULT_OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_LLAMA_CPP = os.environ.get("LLAMA_CPP_HOST", "http://localhost:8080")
DEFAULT_GENERIC = os.environ.get("GLIMMER_ENDPOINT", "")  # OpenAI-compatible base
GLIMMER_MODELS_TRY = ["glimmer", "muse-glimmer", "meta-glimmer", "glimmer-30b", "Muse-Glimmer-30B"]

def _honest_503(msg: str) -> int:
    print(f"503 glimmer_eval real-mode requires {msg} — honest fail, not fabricated", file=sys.stderr, flush=True)
    print(f"Hint: start Glimmer locally:", file=sys.stderr)
    print(f"  ollama run glimmer   # or: llama-server -m glimmer-30b.gguf --port 8080", file=sys.stderr)
    print(f"  export GLIMMER_ENDPOINT=http://localhost:8000/v1  # for vLLM/SGLang/MLX", file=sys.stderr)
    raise SystemExit(11)

def _is_port_open(host: str, port: int, timeout=0.8) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def _parse_host_port(url: str):
    # very small parser: http://host:port/path
    try:
        from urllib.parse import urlparse
        p = urlparse(url)
        host = p.hostname or "localhost"
        port = p.port or (443 if p.scheme=="https" else 80)
        return host, port, p
    except Exception:
        return "localhost", 11434, None

class GlimmerClient:
    def __init__(self, ollama_host: str = DEFAULT_OLLAMA_HOST,
                 llama_cpp_host: str = DEFAULT_LLAMA_CPP,
                 generic_endpoint: str = DEFAULT_GENERIC):
        self.ollama_host = ollama_host.rstrip("/")
        self.llama_cpp_host = llama_cpp_host.rstrip("/")
        self.generic_endpoint = generic_endpoint.rstrip("/")
        self.backend: Optional[str] = None
        self.model: Optional[str] = None
        self.available: bool = False
        self._detect()

    def _detect(self):
        # 1. Ollama
        try:
            oh_host, oh_port, _ = _parse_host_port(self.ollama_host)
            if _is_port_open(oh_host, oh_port, 0.6):
                # try /api/tags to see models
                try:
                    req = urllib.request.Request(f"{self.ollama_host}/api/tags", method="GET")
                    with urllib.request.urlopen(req, timeout=1.5) as r:
                        data = json.loads(r.read().decode("utf-8", errors="ignore"))
                        models = [m.get("name","") for m in data.get("models",[])]
                        for cand in GLIMMER_MODELS_TRY:
                            for m in models:
                                if cand in m.lower():
                                    self.backend = "ollama"
                                    self.model = m
                                    self.available = True
                                    return
                        # if any model exists, still allow generic glimmer call
                        if models:
                            # try glimmer anyway — ollama will 404 if missing, we still mark available
                            self.backend = "ollama"
                            self.model = GLIMMER_MODELS_TRY[0]
                            self.available = True
                            return
                except Exception:
                    # port open but /api/tags failed — still consider available for generate attempt
                    self.backend = "ollama"
                    self.model = GLIMMER_MODELS_TRY[0]
                    self.available = True
                    return
        except Exception:
            pass

        # 2. llama.cpp
        try:
            lh_host, lh_port, _ = _parse_host_port(self.llama_cpp_host)
            if _is_port_open(lh_host, lh_port, 0.6):
                self.backend = "llama_cpp"
                self.model = "glimmer"
                self.available = True
                return
        except Exception:
            pass

        # 3. Generic OpenAI-compatible (vLLM, SGLang, MLX, ExecuTorch)
        if self.generic_endpoint:
            try:
                gh_host, gh_port, _ = _parse_host_port(self.generic_endpoint)
                if _is_port_open(gh_host, gh_port, 0.6):
                    self.backend = "openai_compat"
                    self.model = GLIMMER_MODELS_TRY[0]
                    self.available = True
                    return
            except Exception:
                pass

        self.available = False

    def generate(self, prompt: str, system: str = "", reasoning_effort: str = "medium",
                 temperature: float = 0.2, max_tokens: int = 2048) -> str:
        if not self.available:
            _honest_503("local Glimmer endpoint — no backend detected")

        # Map reasoning effort to system prompt prefix per Glimmer model card
        # low / medium / high / xhigh controllable via system prompt
        effort_prefix = {
            "low": "Reasoning effort: low. Be concise.",
            "medium": "Reasoning effort: medium. Balance depth and speed.",
            "high": "Reasoning effort: high. Think step-by-step, show calibration.",
            "xhigh": "Reasoning effort: xhigh. Exhaustive chain-of-thought, glass-box audit."
        }.get(reasoning_effort, "Reasoning effort: medium.")

        full_system = f"{effort_prefix}\n{system}".strip() if system else effort_prefix

        if self.backend == "ollama":
            return self._gen_ollama(prompt, full_system, temperature, max_tokens)
        elif self.backend == "llama_cpp":
            return self._gen_llama_cpp(prompt, full_system, temperature, max_tokens)
        elif self.backend == "openai_compat":
            return self._gen_openai_compat(prompt, full_system, temperature, max_tokens)
        else:
            _honest_503(f"unknown backend {self.backend}")

    def _gen_ollama(self, prompt: str, system: str, temperature: float, max_tokens: int) -> str:
        # Ollama /api/generate — non-streaming
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": 131072,  # Glimmer supports 131k+
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"{self.ollama_host}/api/generate", data=data,
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                out = json.loads(r.read().decode("utf-8", errors="ignore"))
                return out.get("response", "").strip()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                _honest_503(f"model {self.model} not found in Ollama — pull glimmer first")
            raise
        except Exception as e:
            _honest_503(f"Ollama generate failed: {e}")

    def _gen_llama_cpp(self, prompt: str, system: str, temperature: float, max_tokens: int) -> str:
        # llama.cpp /completion
        full_prompt = f"{system}\n\nUser: {prompt}\nAssistant:" if system else prompt
        payload = {
            "prompt": full_prompt,
            "temperature": temperature,
            "n_predict": max_tokens,
            "n_ctx": 131072,
            "stop": ["User:", "###"]
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"{self.llama_cpp_host}/completion", data=data,
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                out = json.loads(r.read().decode("utf-8", errors="ignore"))
                return out.get("content", "").strip()
        except Exception as e:
            _honest_503(f"llama.cpp completion failed: {e}")

    def _gen_openai_compat(self, prompt: str, system: str, temperature: float, max_tokens: int) -> str:
        # OpenAI-compatible /chat/completions
        url = self.generic_endpoint
        if not url.endswith("/chat/completions"):
            if url.endswith("/v1"):
                url = url + "/chat/completions"
            elif "/v1/" not in url:
                url = url.rstrip("/") + "/v1/chat/completions"
            else:
                url = url.rstrip("/") + "/chat/completions"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model or "glimmer",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data,
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                out = json.loads(r.read().decode("utf-8", errors="ignore"))
                choices = out.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
                return ""
        except Exception as e:
            _honest_503(f"OpenAI-compat generate failed at {url}: {e}")

    def judge(self, eval_json: Dict[str, Any], reasoning_effort: str = "high") -> Dict[str, Any]:
        """LLM-as-judge for MTNN v9/v4 unified G2/G3 eval"""
        # Construct honest, glass-box prompt — no synthetic data, real eval only
        prompt = f"""
You are Glimmer, a local MLOps evaluator for MTNN v9/v4 unified G2/G3.

Given this real evaluation report (no synthetic data, honest 503 if blocked), judge:

INPUT EVAL JSON:
{json.dumps(eval_json, indent=2)[:8000]}

Tasks:
1. G2 floor lock: sport classifier accuracy vs majority 0.6258, delta_vs_majority should be near 0 (invariant), effective rank >=32 (half of 64-d). Is G2 locked at ≤0.615? Honest PASS/FAIL with why.
2. G3 dual: silhouette over cross-sport archetypes, separation (within-between) >0.05, composite ≥0.91. Is G3 coherent? PASS/FAIL.
3. Construct validity: What does MTNN v9/v4 64-d L2 sphere measure? Operationalize, convergent/discriminant/predictive evidence, threats (vanity metrics, leakage, null 0.6258 trap, separation null +0.044).
4. Glass-box: Which TCA 7 heads (volume/playmaking/defense/shotmix/teammates/draft-class/era) or TAA k8 contribute most? Permutation/SHAP signals.
5. Ship gate: Should this checkpoint ship to PWA v67? 59→73 hashes, CORE20 offline13k, void #080A0F 40px sticky, LOD4000/8000 DPR1.

Output JSON only (no markdown) with keys:
{{"g2_judgement": "PASS|FAIL", "g2_reason": "...", "g3_judgement": "PASS|FAIL", "g3_reason": "...", "construct_validity": "...", "threats": ["..."], "glass_box_top_heads": ["..."], "ship_recommendation": "SHIP|HOLD|RETRAIN", "confidence": 0.0-1.0, "honest_503_notes": "..."}}
"""
        system = """You are Glimmer, Meta's 30B open-weight local agent model (131k context, ViT-G/14 1.8B perception, Apache 2.0).
You run locally on a single GPU, always-on, honest, zero-deps, never synthetic. You judge MLOps evals with 5-fold CV, SHAP/permutation, construct validity.
Be calibrated, cite numbers, flag vanity metrics, never hallucinate data. Output JSON only."""
        raw = self.generate(prompt, system=system, reasoning_effort=reasoning_effort, temperature=0.15, max_tokens=1800)
        # Try to parse JSON — be tolerant of markdown fences
        try:
            # strip ```json fences
            txt = raw.strip()
            if txt.startswith("```"):
                txt = txt.split("\n", 1)[1] if "\n" in txt else txt
                if txt.endswith("```"):
                    txt = txt[:-3]
                txt = txt.strip()
                if txt.startswith("json"):
                    txt = txt[4:].strip()
            j = json.loads(txt)
            return j
        except Exception:
            # fallback: return raw as reason, still honest
            return {
                "g2_judgement": "HOLD",
                "g2_reason": f"Glimmer returned non-JSON: {raw[:600]}",
                "g3_judgement": "HOLD",
                "g3_reason": "Parse failed — manual review needed",
                "construct_validity": "unknown — parse failed",
                "threats": ["judge parse failure"],
                "glass_box_top_heads": [],
                "ship_recommendation": "HOLD",
                "confidence": 0.3,
                "honest_503_notes": "judge output not JSON — retry with high effort",
                "_raw": raw[:2000]
            }

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Glimmer client smoke test — stdlib only, honest 503")
    ap.add_argument("--prompt", default="Judge: is G2 0.62 vs majority 0.6258 locked?", help="test prompt")
    ap.add_argument("--effort", default="medium", choices=["low","medium","high","xhigh"])
    args = ap.parse_args()
    c = GlimmerClient()
    if not c.available:
        _honest_503("no Glimmer backend — start Ollama/llama.cpp/vLLM")
    print(f"Backend: {c.backend} model={c.model} host={c.ollama_host}/{c.llama_cpp_host}/{c.generic_endpoint}")
    out = c.generate(args.prompt, system="You are an MLOps evaluator", reasoning_effort=args.effort)
    print(out)

if __name__ == "__main__":
    main()
