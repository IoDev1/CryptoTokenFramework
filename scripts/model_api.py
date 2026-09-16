#!/usr/bin/env python3
"""Shared helpers for the two model steps when they run on the Claude API (unattended, CI).

Credentials: ANTHROPIC_API_KEY in the environment (a GitHub Actions secret in CI). If it is
missing, callers should skip the step and keep the last stored output, so the site never breaks
because a key was not set.

Model choice:
  - news stance      -> claude-haiku-4-5   (classification over headlines; cheap)
  - research pass    -> claude-opus-5      (judgment with web search; monthly)
Costs are per token-batch, never per visitor.
"""
import json, os, re, sys, time

HAIKU = "claude-haiku-4-5"
OPUS = "claude-opus-5"


def have_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def client():
    import anthropic  # imported lazily so the fetch scripts never need the SDK
    return anthropic.Anthropic()


def text_of(message) -> str:
    """Concatenate the text blocks of a Messages API response."""
    return "".join(b.text for b in message.content if getattr(b, "type", "") == "text")


def extract_json(s: str):
    """Return the first top-level JSON object found in a string, or None."""
    start = s.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(s)):
            if s[i] == "{": depth += 1
            elif s[i] == "}":
                depth -= 1
                if depth == 0:
                    try: return json.loads(s[start:i + 1])
                    except json.JSONDecodeError: break
        start = s.find("{", start + 1)
    return None


def run_json(system: str, user: str, *, model: str, max_tokens: int, tools=None, effort: str | None = None,
             max_rounds: int = 6, log=print):
    """One request (streamed; continues through pause_turn) that must end in a JSON object.

    Returns (obj, usage_dict). Raises RuntimeError on refusal or when no JSON came back.
    """
    c = client()
    messages = [{"role": "user", "content": user}]
    kwargs = dict(model=model, max_tokens=max_tokens, system=system, messages=messages)
    if tools: kwargs["tools"] = tools
    if effort: kwargs["output_config"] = {"effort": effort}
    usage = {"input_tokens": 0, "output_tokens": 0, "web_search_requests": 0}
    for _ in range(max_rounds):
        with c.messages.stream(**kwargs) as stream:
            msg = stream.get_final_message()
        u = msg.usage
        usage["input_tokens"] += u.input_tokens; usage["output_tokens"] += u.output_tokens
        stu = getattr(u, "server_tool_use", None)
        if stu and getattr(stu, "web_search_requests", None): usage["web_search_requests"] += stu.web_search_requests
        if msg.stop_reason == "refusal":
            raise RuntimeError(f"refused: {getattr(msg, 'stop_details', None)}")
        if msg.stop_reason == "pause_turn":
            # server-side tool loop paused: send the assistant turn back unchanged and continue
            messages.append({"role": "assistant", "content": msg.content}); continue
        obj = extract_json(text_of(msg))
        if obj is None:
            raise RuntimeError("no JSON object in the response; stop_reason=" + str(msg.stop_reason))
        return obj, usage
    raise RuntimeError("gave up after repeated pause_turn")


def cost_usd(model: str, usage: dict) -> float:
    """Rough cost from the public price list (input/output $ per MTok) plus $10 per 1k searches."""
    price = {HAIKU: (1.0, 5.0), OPUS: (5.0, 25.0)}.get(model, (5.0, 25.0))
    return usage["input_tokens"] / 1e6 * price[0] + usage["output_tokens"] / 1e6 * price[1] + usage["web_search_requests"] / 1000 * 10.0
