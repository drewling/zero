#!/usr/bin/env python3
"""LLM provider abstraction for zero.

Provider dispatch is DATA-DRIVEN: each KNOWN_PROVIDERS entry carries an argv
template list. Tokens {prompt} and {model} are substituted at call time.
Adding a new provider (e.g. gemini, or any agent CLI you run) is a data entry
here with its argv template, not a code change.
"""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SETTINGS_PATH = os.path.join(ROOT, "app", "settings.json")

# Each entry: name, label, bin, bin_env, argv_template, wired, model_map.
# argv_template: list of str; {prompt} and {model} are substituted at call time.
KNOWN_PROVIDERS = [
    {
        "name": "claude",
        "label": "Claude (Anthropic)",
        "bin": "claude",
        "bin_env": "CLAUDE_BIN",
        "wired": True,
        # claude CLI: claude -p <prompt> --model <model>
        "argv_template": ["-p", "{prompt}", "--model", "{model}"],
        "model_map": {
            "haiku": "haiku",
            "sonnet": "sonnet",
            "opus": "opus",
        },
    },
    {
        "name": "codex",
        "label": "Codex (OpenAI)",
        "bin": "codex",
        "bin_env": "CODEX_BIN",
        "wired": True,
        # OpenAI Codex CLI non-interactive form: codex exec --model <model> <prompt>
        "argv_template": ["exec", "--model", "{model}", "{prompt}"],
        "model_map": {
            "haiku": "gpt-4o-mini",
            "sonnet": "gpt-4o",
            "opus": "o1",
        },
    },
    {
        "name": "hermes",
        "label": "Hermes (local)",
        "bin": "hermes",
        "bin_env": "HERMES_BIN",
        "wired": True,
        # Hermes local runner: hermes run --model <model> --prompt <prompt>
        "argv_template": ["run", "--model", "{model}", "--prompt", "{prompt}"],
        "model_map": {
            "haiku": "hermes-3-llama-3.1-8b",
            "sonnet": "hermes-3-llama-3.1-70b",
            "opus": "hermes-3-llama-3.1-70b",
        },
    },
]

# Index by name for O(1) lookup.
_BY_NAME = {p["name"]: p for p in KNOWN_PROVIDERS}


def _active_provider_name():
    """Read the active provider from settings (default 'claude'). Never throws."""
    try:
        if os.path.isfile(SETTINGS_PATH):
            with open(SETTINGS_PATH) as f:
                return json.load(f).get("provider", "claude")
    except Exception:
        pass
    return "claude"


def _bin_for(provider):
    """Resolve the binary path for a provider entry, honoring env override."""
    return os.environ.get(provider["bin_env"], provider["bin"])


def _version(binary):
    """Run `<binary> --version`, return stripped stdout, or None on failure."""
    try:
        r = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=5)
        out = (r.stdout or r.stderr or "").strip().splitlines()
        return out[0].strip() if out else None
    except Exception:
        return None


def detect_providers():
    """Return a list of provider status dicts.

    Shape: [{name, label, available: bool, version: str|None, active: bool}]
    A provider is available only if it is wired AND its binary is on PATH.
    """
    active = _active_provider_name()
    result = []
    for p in KNOWN_PROVIDERS:
        binary = _bin_for(p)
        available = bool(p.get("wired")) and shutil.which(binary) is not None
        result.append({
            "name": p["name"],
            "label": p["label"],
            "available": available,
            "version": _version(binary) if available else None,
            "active": p["name"] == active,
        })
    return result


def _build_cmd(provider, binary, prompt, model_arg):
    """Expand the provider's argv_template into a full command list."""
    template = provider.get("argv_template", ["-p", "{prompt}", "--model", "{model}"])
    return [binary] + [
        t.replace("{prompt}", prompt).replace("{model}", model_arg)
        for t in template
    ]


def run_prompt(prompt, model="haiku", timeout=120):
    """Run a prompt through the active provider's CLI.

    Returns (stdout_text: str, ok: bool).
    Falls back to claude if the active provider is unavailable or fails.
    """
    active_name = _active_provider_name()
    provider = _BY_NAME.get(active_name) or _BY_NAME["claude"]
    # If the active provider binary isn't on PATH, fall back to claude — but say so,
    # otherwise a user who selected Codex/Hermes is silently running on claude.
    binary = _bin_for(provider)
    if provider["name"] != "claude" and not shutil.which(binary):
        print(f"llm: {provider['name']} binary ({binary}) not on PATH, using claude",
              file=sys.stderr)
        provider = _BY_NAME["claude"]
        binary = _bin_for(provider)
    model_arg = provider["model_map"].get(model, model)
    cmd = _build_cmd(provider, binary, prompt, model_arg)

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return ("", False)
    except Exception:
        return ("", False)
    if r.returncode != 0:
        # If the active provider failed and it isn't already claude, try claude once.
        if provider["name"] != "claude":
            print(f"llm: {provider['name']} failed (exit {r.returncode}): "
                  f"{(r.stderr or '').strip()[:200]} — falling back to claude",
                  file=sys.stderr)
            fallback = _BY_NAME["claude"]
            fb_binary = _bin_for(fallback)
            fb_model = fallback["model_map"].get(model, model)
            fb_cmd = _build_cmd(fallback, fb_binary, prompt, fb_model)
            try:
                r = subprocess.run(fb_cmd, capture_output=True, text=True, timeout=timeout)
            except Exception as e:
                print(f"llm: claude fallback errored: {e}", file=sys.stderr)
                return ("", False)
            if r.returncode != 0:
                print(f"llm: claude fallback also failed (exit {r.returncode})", file=sys.stderr)
                return ("", False)
            return (r.stdout, True)
        return ("", False)
    return (r.stdout, True)
