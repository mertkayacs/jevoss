"""Run suite items through any predictor and turn answers into decision records.

A predictor is any callable taking a Jev request dict and returning a Jev
response dict: an HTTP endpoint, a local engine, or a stub.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .metrics import Decision
from .suites import option_values

Predictor = Callable[[dict[str, Any]], dict[str, Any]]

# Must match jevalt.format.UNKNOWN so model output and gold align.
UNKNOWN = "unknown"


def needs_unknown(item: dict[str, Any]) -> bool:
    """True when the item's targets require the unknown option."""
    if item.get("abstain"):
        return True
    for target in item.get("targets", {}).values():
        if str(target.get("label", "")).lower() == UNKNOWN:
            return True
        dist = target.get("dist")
        if dist and UNKNOWN in dist:
            return True
    return False


def http_predictor(base_url: str, model: str = "jev-latest", api_key: str = "local", timeout: float = 120) -> Predictor:
    """Client for any TypeSafe-compatible `/v1/systemone` endpoint."""
    url = base_url.rstrip("/") + "/v1/systemone"

    def predict(request: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps({**request, "model": request.get("model", model)}).encode()
        for attempt in range(5):
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    return json.load(response)
            except urllib.error.HTTPError as err:
                if err.code not in (429, 500, 502, 503, 529) or attempt == 4:
                    raise
            except (urllib.error.URLError, TimeoutError):
                if attempt == 4:
                    raise
            time.sleep(2**attempt)
        raise RuntimeError("unreachable")

    return predict


def _probs(question: dict[str, Any], answer: dict[str, Any], values: tuple[str, ...]) -> tuple[float, ...]:
    if question["type"] == "noul":
        p = float(answer["noul"])
        return (1.0 - p, p)
    table = {str(k): float(v) for k, v in answer["probabilities"].items()}
    raw = [table.get(v, 0.0) for v in values]
    total = sum(raw) or 1.0
    return tuple(p / total for p in raw)


def to_decisions(item: dict[str, Any], response: dict[str, Any]) -> list[Decision]:
    out = []
    need_unknown = needs_unknown(item)
    for field, question in item["questions"].items():
        values = option_values(question)
        if need_unknown and question["type"] in ("choice", "score") and UNKNOWN not in values:
            values = values + (UNKNOWN,)
        target = item["targets"][field]
        dist = target.get("dist")
        out.append(
            Decision(
                item=item["id"],
                field=field,
                kind=question["type"],
                lang=item.get("lang", "en"),
                values=values,
                probs=_probs(question, response["answers"][field], values),
                gold=str(target["label"]),
                gold_dist=tuple(float(dist.get(v, 0.0)) for v in values) if dist else None,
                tags=tuple(item.get("tags", ())) + (f"type:{question['type']}",),
            )
        )
    return out


def run(items: Iterable[dict[str, Any]], predict: Predictor, *, extra: dict[str, Any] | None = None, workers: int = 1, on_error: str = "raise") -> tuple[list[Decision], list[dict[str, Any]]]:
    """Returns decision records plus raw responses (for audit files)."""
    items = list(items)

    def one(item):
        request = {"state": item["state"], "questions": item["questions"], **(extra or {})}
        if needs_unknown(item) and "abstain" not in request:
            request["abstain"] = True
        try:
            return item, predict(request), None
        except Exception as err:  # noqa: BLE001, a failed row is recorded, not hidden
            if on_error == "raise":
                raise
            return item, None, repr(err)

    decisions: list[Decision] = []
    raw: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for item, response, error in pool.map(one, items):
            raw.append({"id": item["id"], "response": response, "error": error})
            if response is not None:
                decisions.extend(to_decisions(item, response))
    return decisions, raw
