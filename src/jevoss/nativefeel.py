"""Blind native-quality rating of model-written text (reasoning traces) per language.

A judge model from a different family rates each text on a 1 to 5 rubric. Scores are only
comparable within one judge and one rubric version, so reports always name both.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.request

RUBRIC_VERSION = "native-feel-v2"

RUBRIC = {
    "tr": (
        "Sen Türkçe editörüsün. Aşağıdaki kısa metni bir Türk okur gözüyle değerlendir: "
        "doğallık, çeviri kokusu (İngilizceden kalıp aktarma), ek ve hâl eki hataları, söz dizimi, üslup. "
        "1 = açıkça çeviri veya hatalı, 3 = anlaşılır ama yer yer yapay, 5 = anadili Türkçe olan birinin yazacağı gibi.\n"
        "Yalnızca doğal dildeki metni değerlendir. JSON anahtarlarını, tanımlayıcıları, kod parçalarını, "
        "ürün ve marka adlarını ve Türk mühendislerin normalde İngilizce yazdığı teknik terimleri görmezden gel. "
        "Resmî iş Türkçesindeki \"verilecektir\", \"yapılacaktır\" gibi ifadeler doğrudur, hata değildir. "
        "Sadece JSON döndür: {\"score\": 1-5, \"issue\": \"en önemli sorun, yoksa boş\"}"
    ),
    "de": (
        "Du bist Lektorin für Deutsch. Bewerte den kurzen Text aus Sicht einer deutschen Leserin: "
        "Natürlichkeit, Übersetzungsdeutsch, Fall- und Endungsfehler, Satzbau, Stil. "
        "1 = klar übersetzt oder fehlerhaft, 3 = verständlich, aber stellenweise hölzern, "
        "5 = so, wie es eine Muttersprachlerin schreiben würde.\n"
        "Bewerte nur die natürlichsprachliche Prosa. Ignoriere JSON-Schlüssel, Bezeichner, Code, "
        "Produkt- und Markennamen sowie englische Fachbegriffe, die deutsche Ingenieure üblicherweise "
        "auf Englisch schreiben. Formelles Geschäftsdeutsch ist korrekt, kein Fehler. "
        "Gib nur JSON zurück: {\"score\": 1-5, \"issue\": \"wichtigstes Problem oder leer\"}"
    ),
    "en": (
        "You are an English copy editor. Rate the short text for a native reader: "
        "naturalness, awkward phrasing, grammar, register. "
        "1 = clearly non-native or wrong, 3 = understandable but stiff in places, 5 = what a native writer would write.\n"
        "Judge only the natural-language prose. Ignore JSON keys, identifiers, code, product and brand names, "
        "and technical terms that engineers normally write in English. Formal business register is correct, not an error. "
        "Return only JSON: {\"score\": 1-5, \"issue\": \"main problem or empty\"}"
    ),
}


def rate(texts: list[str], lang: str, *, base_url: str, model: str, key_env: str, extra: dict | None = None, delay: float = 0.0) -> dict:
    """Rate each text; returns mean score, distribution and the issues the judge named."""
    key = os.environ[key_env]
    scores, issues = [], []
    for text in texts:
        body = {"model": model, "temperature": 0, "messages": [{"role": "system", "content": RUBRIC[lang]}, {"role": "user", "content": text}], **(extra or {})}
        req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(), headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
        content = json.load(urllib.request.urlopen(req, timeout=120))["choices"][0]["message"]["content"]
        match = re.search(r"\{.*\}", content, re.S)
        try:
            parsed = json.loads(match.group(0)) if match else {}
            scores.append(int(parsed["score"]))
            if parsed.get("issue"):
                issues.append(parsed["issue"])
        except (ValueError, KeyError, TypeError):
            continue
        time.sleep(delay)
    dist = {s: scores.count(s) for s in range(1, 6)}
    return {"rubric": RUBRIC_VERSION, "judge": model, "lang": lang, "n": len(scores), "mean": round(sum(scores) / max(len(scores), 1), 3), "distribution": dist, "issues": issues[:25]}
