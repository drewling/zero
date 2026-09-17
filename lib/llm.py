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
        # claude CLI: claude -p <prompt> --model <model>. Extra flags keep this a pure
        # text-in/JSON-out call with no side effects: --strict-mcp-config (don't load the
        # user's MCP servers — slow + irrelevant here) and --no-session-persistence (don't
        # write transcripts). Documents-walk avoidance is handled via CLAUDE_CONFIG_DIR
        # in _run_cmd, not a flag (--bare would also drop OAuth login).
        "argv_template": ["-p", "{prompt}", "--model", "{model}",
                          "--strict-mcp-config", "--no-session-persistence"],
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
    {
        "name": "jev",
        "label": "Jev (TypeSafe AI)",
        # Jev is NOT a CLI: it's lib/jev.py, an HTTP client for typed
        # classification (noul/choice/score). It cannot generate free-form
        # text, so it is never used for run_prompt()'s text-in/text-out
        # contract — run_prompt() falls back to claude immediately whenever
        # the active provider is jev. It's listed here purely so the
        # provider picker can show/select it (see detect_providers()).
        "bin": None,
        "bin_env": "JEV_BIN",  # unused; kept for shape consistency, never resolved
        "wired": True,
        "is_http_client": True,
        "argv_template": [],
        "model_map": {
            "haiku": "jev-latest",
            "sonnet": "jev-latest",
            "opus": "jev-latest",
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
    """Resolve the binary path for a provider entry, honoring env override.

    jev has no binary (it's an HTTP client, see lib/jev.py) — bin_env is
    unused for it and this is never called on its behalf in practice."""
    if provider.get("bin") is None:
        return None
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
    jev is the exception: it's an HTTP client, not a binary, so its
    availability is whether an API key is configured (see lib/jev.py).
    """
    active = _active_provider_name()
    result = []
    for p in KNOWN_PROVIDERS:
        if p.get("is_http_client"):
            try:
                import jev as _jev  # local import: keep jev.py optional/isolated
                available = bool(p.get("wired")) and _jev.available()
            except Exception:
                available = False
            result.append({
                "name": p["name"],
                "label": p["label"],
                "available": available,
                "version": "jev-latest" if available else None,
                "active": p["name"] == active,
            })
            continue
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


def _claude_home():
    """An isolated CLAUDE_CONFIG_DIR for the claude provider.

    WHY: Claude Code stat-walks the project paths listed in the user's ~/.claude.json on
    startup. When the spawning app is a sandboxed GUI without "Documents" access, that
    walk into ~/Documents triggers a macOS TCC permission prompt — which is MODAL and
    blocks claude's read, freezing the whole run at 0%. An isolated config with an empty
    projects map has nothing under ~/Documents to walk, so no prompt, no hang — and it's
    stable across the app's ad-hoc re-signing (a fresh signature otherwise re-prompts).

    Returns the dir, or None if it can't be made usable (caller falls back to the default
    config, so we never do worse than before)."""
    home = os.path.join(ROOT, "claude-home")
    try:
        os.makedirs(home, exist_ok=True)
        cfg = os.path.join(home, ".claude.json")
        if not os.path.exists(cfg):
            with open(cfg, "w") as f:
                json.dump({}, f)                      # empty projects → no Documents walk
        creds = os.path.join(home, ".credentials.json")
        if not os.path.exists(creds):
            # Seed login from the Keychain item the user's interactive claude created.
            r = subprocess.run(["security", "find-generic-password",
                                "-s", "Claude Code-credentials", "-w"],
                               capture_output=True, text=True, timeout=10,
                               stdin=subprocess.DEVNULL)
            if r.returncode != 0 or not r.stdout.strip():
                return None                           # no creds to seed → use default config
            with open(creds, "w") as f:
                f.write(r.stdout.strip())
            os.chmod(creds, 0o600)
        return home
    except Exception:
        return None


def _run_cmd(cmd, provider_name, timeout):
    """Run a provider command (stdin closed so it can never block on input).

    For claude: try the isolated config first (no Documents-walk TCC prompt). If that
    isn't logged in / fails for a non-timeout reason, retry once with the default config
    so a stale seeded credential never breaks classification. Returns the
    CompletedProcess, or None on timeout/spawn error."""
    base = os.environ.copy()
    # Run from the app's data dir, never an inherited cwd that might sit under ~/Documents
    # (claude records its cwd as a project; we never want a Documents path in there).
    cwd = ROOT if os.path.isdir(ROOT) else None
    if provider_name == "claude":
        home = _claude_home()
        if home:
            iso = dict(base); iso["CLAUDE_CONFIG_DIR"] = home
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                                   stdin=subprocess.DEVNULL, env=iso, cwd=cwd)
                if r.returncode == 0:
                    return r
                # Non-zero (e.g. seeded creds went stale → "Not logged in"): fall through
                # and retry on the default config below.
            except subprocess.TimeoutExpired:
                return None                           # hung; don't double the wait
            except Exception:
                pass
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                             stdin=subprocess.DEVNULL, env=base, cwd=cwd)
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None


def run_prompt(prompt, model="haiku", timeout=120):
    """Run a prompt through the active provider's CLI.

    Returns (stdout_text: str, ok: bool).
    Falls back to claude if the active provider is unavailable or fails.
    """
    active_name = _active_provider_name()
    provider = _BY_NAME.get(active_name) or _BY_NAME["claude"]
    # Jev cannot generate free-form text (it's a typed-classification HTTP
    # client, not a CLI) — drafting/prompting always falls back to claude
    # when jev is the active provider. Say so, same as any other fallback.
    if provider.get("is_http_client"):
        print(f"llm: {provider['name']} cannot serve text-generation prompts, "
              f"using claude", file=sys.stderr)
        provider = _BY_NAME["claude"]
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

    r = _run_cmd(cmd, provider["name"], timeout)
    if r is None:
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
            r = _run_cmd(fb_cmd, "claude", timeout)
            if r is None or r.returncode != 0:
                print("llm: claude fallback also failed", file=sys.stderr)
                return ("", False)
            return (r.stdout, True)
        return ("", False)
    return (r.stdout, True)
