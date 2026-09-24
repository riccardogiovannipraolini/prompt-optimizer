#!/usr/bin/env python3
"""
Aggiornamento mensile della Knowledge Base del Prompt Optimizer.

Flusso:
  1. Scarica abstract dei paper più recenti da arXiv (gratis, no API key)
  2. Recupera estratti dalle guide ufficiali Anthropic / OpenAI
  3. Passa tutto all'LLM configurato per riscrivere KB JSON e tabella MD
  4. Salva i file aggiornati con backup automatico

Provider (stesse env var di ai_optimizer.py):
  ANTHROPIC_API_KEY → Claude (priorità, KB ottimizzata per esso)
  OPENAI_API_KEY    → OpenAI
  GEMINI_API_KEY    → Gemini
  (nessuna)         → Ollama locale (default)

Modelli override: ANTHROPIC_MODEL, OPENAI_MODEL, GEMINI_MODEL, OLLAMA_MODEL
"""

import os
import re
import sys
import json
import ssl
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
KB_JSON  = BASE_DIR / "prompt_optimizer_knowledge_base.json"
SUMMARY_MD = BASE_DIR / "prompt_engineering_summary_table.md"
LOG_FILE = BASE_DIR / "update_kb.log"

_SSL_CTX = ssl.create_default_context()


# ── Rete ─────────────────────────────────────────────────────────────────────

def _fetch(url, timeout=30):
    """GET con TLS verificato. Restituisce testo o None se fallisce."""
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-optimizer/2.0"})
    try:
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        _log(f"  ⚠️  Fetch fallito {url}: {e}")
        return None


def _post_json(url, payload, headers, timeout=240):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code}: {detail}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Connessione fallita: {e.reason}") from None


# ── Logging ───────────────────────────────────────────────────────────────────

def _log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── Raccolta dati web ─────────────────────────────────────────────────────────

def fetch_arxiv_papers(max_results=15):
    """Paper più recenti su arXiv (API pubblica, no key)."""
    query = urllib.parse.quote("prompt engineering large language model")
    url = (
        f"http://export.arxiv.org/api/query?"
        f"search_query=all:{query}"
        f"&start=0&max_results={max_results}"
        f"&sortBy=submittedDate&sortOrder=descending"
    )
    _log("  arXiv: scaricando paper recenti...")
    text = _fetch(url)
    if not text:
        return []

    papers = []
    try:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(text)
        for entry in root.findall("atom:entry", ns):
            title   = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            pub     = entry.find("atom:published", ns)
            if title is not None and summary is not None:
                papers.append({
                    "title":    title.text.strip().replace("\n", " "),
                    "abstract": summary.text.strip()[:600],
                    "date":     pub.text[:10] if pub is not None else "",
                })
    except ET.ParseError as e:
        _log(f"  arXiv parse error: {e}")

    _log(f"  arXiv: {len(papers)} paper trovati.")
    return papers


def fetch_official_guides():
    """Estratti (testo grezzo) dalle guide ufficiali di Anthropic e OpenAI."""
    sources = [
        ("Anthropic Prompt Engineering",
         "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview"),
        ("OpenAI Prompt Engineering Guide",
         "https://platform.openai.com/docs/guides/prompt-engineering"),
    ]
    extracts = []
    for name, url in sources:
        _log(f"  Guide: {name}...")
        html = _fetch(url)
        if html:
            text = re.sub(r"<[^>]+>", " ", html)
            text = re.sub(r"\s+", " ", text).strip()
            extracts.append(f"=== {name} ({url}) ===\n{text[:3000]}")
        else:
            _log(f"  Guide: {name} non recuperata, skip.")
    return "\n\n".join(extracts)


# ── LLM ──────────────────────────────────────────────────────────────────────

def call_llm(system_prompt, user_prompt):
    anthropic_model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    openai_model    = os.environ.get("OPENAI_MODEL",    "gpt-5")
    gemini_model    = os.environ.get("GEMINI_MODEL",    "gemini-2.5-flash")
    ollama_model    = os.environ.get("OLLAMA_MODEL",    "qwen3:14b")

    if os.environ.get("ANTHROPIC_API_KEY"):
        key = os.environ["ANTHROPIC_API_KEY"]
        _log(f"  LLM: Claude {anthropic_model}")
        data = _post_json(
            "https://api.anthropic.com/v1/messages",
            {"model": anthropic_model, "max_tokens": 8192, "temperature": 0.2,
             "system": system_prompt,
             "messages": [{"role": "user", "content": user_prompt}]},
            {"x-api-key": key, "anthropic-version": "2023-06-01"},
        )
        return data["content"][0]["text"]

    elif os.environ.get("OPENAI_API_KEY"):
        key = os.environ["OPENAI_API_KEY"]
        _log(f"  LLM: OpenAI {openai_model}")
        data = _post_json(
            "https://api.openai.com/v1/chat/completions",
            {"model": openai_model, "temperature": 0.2,
             "messages": [{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_prompt}]},
            {"Authorization": f"Bearer {key}"},
        )
        return data["choices"][0]["message"]["content"]

    elif os.environ.get("GEMINI_API_KEY"):
        key = os.environ["GEMINI_API_KEY"]
        _log(f"  LLM: Gemini {gemini_model}")
        data = _post_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={key}",
            {"contents": [{"parts": [{"text": user_prompt}]}],
             "systemInstruction": {"parts": [{"text": system_prompt}]},
             "generationConfig": {"temperature": 0.2}},
            {},
        )
        return data["candidates"][0]["content"]["parts"][0]["text"]

    else:
        _log(f"  LLM: Ollama {ollama_model} (locale)")
        data = _post_json(
            "http://localhost:11434/api/chat",
            {"model": ollama_model,
             "messages": [{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_prompt}],
             "stream": False, "options": {"temperature": 0.2}},
            {},
        )
        return data["message"]["content"]


# ── Prompt per l'LLM ─────────────────────────────────────────────────────────

UPDATE_SYSTEM = """\
Sei un esperto di Prompt Engineering con aggiornamento continuo sulla ricerca.
Riscrivi la Knowledge Base JSON del Prompt Optimizer tenendo conto delle ricerche recenti.

Regole:
1. Mantieni la struttura JSON esatta (campi: id, name, priority, pareto_core, applicability,
   metrics, detection_triggers, transformation_rules, example, when_to_use).
2. Aggiorna o aggiungi tecniche solo se i paper lo giustificano con dati concreti.
3. Non rimuovere tecniche consolidate senza una ragione esplicita nella ricerca.
4. Aggiorna model_specific_notes con i modelli attualmente disponibili.
5. Rispondi SOLO con il JSON valido. Nessun markdown, nessuna spiegazione."""

SUMMARY_SYSTEM = """\
Sei un esperto di Prompt Engineering. Genera una tabella Markdown sintetica.
Rispondi SOLO con la tabella, nessun altro testo."""


def build_update_prompt(papers, extra_resources, current_kb_text):
    paper_block = "\n".join(
        f"[{p['date']}] {p['title']}\n{p['abstract']}"
        for p in papers
    ) or "Nessun paper recuperato."

    return f"""\
Aggiorna la Knowledge Base. Data odierna: {datetime.now().strftime('%Y-%m-%d')}

=== PAPER RECENTI (arXiv) ===
{paper_block}

=== GUIDE UFFICIALI ===
{extra_resources or 'Non recuperate.'}

=== KB ATTUALE (da aggiornare) ===
{current_kb_text}

Riscrivi il JSON aggiornato. Solo JSON, nessun altro testo."""


def build_summary_prompt(kb_json_text):
    return f"""\
Genera la tabella Markdown riassuntiva delle tecniche di questa KB:

{kb_json_text}

Formato:
| Tecnica | Quando usarla | Impatto stimato | Costo |
|---|---|---|---|
[una riga per tecnica]

Solo la tabella Markdown."""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    _log("=" * 60)
    _log(f" AGGIORNAMENTO KB — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    _log("=" * 60)

    # 1. Backup
    bak_json = KB_JSON.with_suffix(".json.bak")
    bak_md   = SUMMARY_MD.with_suffix(".md.bak")
    if KB_JSON.exists():
        KB_JSON.rename(bak_json)
    if SUMMARY_MD.exists():
        SUMMARY_MD.rename(bak_md)
    _log("Backup creati (.bak)")

    # 2. Ricerca web
    _log("\nRecupero ricerche recenti...")
    papers = fetch_arxiv_papers(max_results=15)
    extra  = fetch_official_guides()

    # 3. KB attuale dal backup
    current_kb = bak_json.read_text(encoding="utf-8") if bak_json.exists() else "{}"

    # 4. Riscrittura KB JSON
    _log("\nRigenerazione JSON knowledge base...")
    raw = call_llm(UPDATE_SYSTEM, build_update_prompt(papers, extra, current_kb))

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        _log("ERRORE: LLM non ha restituito JSON. Ripristino backup.")
        if bak_json.exists(): bak_json.rename(KB_JSON)
        if bak_md.exists():   bak_md.rename(SUMMARY_MD)
        return 1

    try:
        new_kb = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        _log(f"ERRORE: JSON non valido: {e}. Ripristino backup.")
        if bak_json.exists(): bak_json.rename(KB_JSON)
        if bak_md.exists():   bak_md.rename(SUMMARY_MD)
        return 1

    # Aggiorna metadata
    new_kb.setdefault("metadata", {}).update({
        "updated":          datetime.now().strftime("%Y-%m-%d"),
        "update_frequency": "mensile",
        "version":          "2.0",
    })

    KB_JSON.write_text(
        json.dumps(new_kb, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    _log(f"OK: {KB_JSON.name} aggiornato ({len(new_kb.get('techniques', []))} tecniche)")

    # 5. Rigenera tabella MD
    _log("\nRigenerazione tabella riepilogativa...")
    summary = call_llm(SUMMARY_SYSTEM, build_summary_prompt(
        json.dumps(new_kb, indent=2, ensure_ascii=False)
    ))
    SUMMARY_MD.write_text(summary, encoding="utf-8")
    _log(f"OK: {SUMMARY_MD.name} aggiornata")

    # 6. Rimuovi backup
    for bak in [bak_json, bak_md]:
        if bak.exists():
            bak.unlink()

    _log(f"\nAGGIORNAMENTO COMPLETATO — {len(papers)} paper arXiv elaborati.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
