# Illustrative rates for this lab's ledger, in USD per million tokens.
# They are not an invoice. Check current OpenAI pricing before you budget with them.
import json

from tutorial.common.harness import call_tool, set_hook

INPUT_USD_PER_MILLION = 0.40
OUTPUT_USD_PER_MILLION = 1.60

CACHEABLE = {
    "get_shop_fact",
    "read_shop_file",
    "query_inventory",
    "list_notes",
    "read_note",
    "load_skill",
    "fetch_page",
    "memory_search",
    "read_supplier_note",
}
CACHE = {}
CACHE_EVENTS = []


def reset_cache():
    CACHE.clear()
    CACHE_EVENTS.clear()


def route_task(user_text):
    """Pick a model class. This lab still calls one model; the log shows the decision."""
    text = user_text.lower()
    if any(word in text for word in ("restock", "ticket", "verify")):
        return {
            "task": "shop-decision",
            "model": "gpt-4.1-mini",
            "reason": "needs tools and a policy check",
        }
    return {
        "task": "counter-question",
        "model": "gpt-4.1-mini",
        "reason": "short lookup on the default tool-calling model",
    }


def cost_summary(usage_rows):
    prompt = sum(row["prompt_tokens"] for row in usage_rows)
    completion = sum(row["completion_tokens"] for row in usage_rows)
    usd = (prompt * INPUT_USD_PER_MILLION + completion * OUTPUT_USD_PER_MILLION) / 1_000_000
    latency = sum(row["latency_ms"] for row in usage_rows)
    return {
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "estimated_usd": round(usd, 6),
        "latency_ms": round(latency, 3),
        "rate_note": "illustrative, not an invoice",
    }


def cached_call(call):
    """Return a cached read, or run the tool and store it."""
    name = call["name"]
    if name not in CACHEABLE:
        return call_tool(call), False
    key = name + " " + json.dumps(call["arguments"], sort_keys=True, default=str)
    if key in CACHE:
        print("cache: HIT", key)
        CACHE_EVENTS.append("HIT " + key)
        return CACHE[key], True
    print("cache: MISS", name)
    CACHE_EVENTS.append("MISS " + name)
    result = call_tool(call)
    CACHE[key] = result
    return result, False


set_hook("route_task", route_task)
set_hook("cached_call", cached_call)
