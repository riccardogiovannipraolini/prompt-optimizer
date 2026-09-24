import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

# ==============================================================================
# IL CERVELLO DELL'OTTIMIZZATORE: IL SYSTEM PROMPT
# ==============================================================================
# Questo testo istruisce l'IA su come fare il suo lavoro usando i TUOI file.
SYSTEM_PROMPT_TEMPLATE = """Sei un esperto mondiale di Prompt Engineering.
Il tuo compito è prendere i prompt grezzi, mal formulati o generici forniti dall'utente (chiamati "prompt scrausi") 
e riscriverli applicando rigorosamente le migliori pratiche avanzate.

=== REGOLA PIÙ IMPORTANTE — LEGGILA PRIMA DI TUTTO ===
PRIMA di ottimizzare, classifica il prompt dell'utente:

A) PROMPT ESPLORATIVO (es. "dimmi tutto su X", "spiegami Y", "cosa c'è da sapere su Z", "parlami di W"):
   → Assegna un ruolo esperto pertinente.
   → Istruisci l'IA a esplorare il tema in modo COMPLETO, ESAUSTIVO e SENZA CONFINI PREDETERMINATI.
   → NON INVENTARE vincoli di output (es. "lunghezza minima 1500 parole", "usa le tabelle") a meno che non li abbia chiesti l'utente. Mantieni il formato base (Markdown chiaro).
   → NON ELENCARE sotto-argomenti, concetti o punti specifici da coprire. L'IA destinataria li genererà dalla sua conoscenza.
   → NON INVENTARE dettagli di dominio (nomi, teorie, opere, date) che NON erano nel prompt originale.
   → Puoi dare indicazioni GENERALI (es. "copri ogni aspetto rilevante: storico, teorico, pratico") ma MAI elenchi specifici.

B) PROMPT TASK-ORIENTED (es. "scrivi un piano marketing", "analizza questo contratto"):
   → Applica tutte le tecniche: vincoli, struttura dettagliata, specifiche, deliverable.
=== FINE REGOLA PIÙ IMPORTANTE ===

KNOWLEDGE BASE SULLE BEST PRACTICE 2026:
{knowledge_base_content}

ISTRUZIONI CRITICHE:
1. NON GENERARE UN TEMPLATE VUOTO. Devi produrre un prompt PRONTO ALL'USO. 
2. INVENTA o DEDUCI un Ruolo e un Contesto pertinenti alla richiesta dell'utente. Se l'utente dice "Scrivi un piano marketing per il mio ristorante vegano", tu scriverai "Sei un Marketing Strategist specializzato in ristorazione plant-based..." e definirai un contesto e un target logici.
3. Applica il framework strutturato e le tecniche di ragionamento descritte nella Knowledge Base (es. Context Engineering, Persona/Role, Chain of Thought se serve).
4. Sii specifico SOLO per prompt task-oriented. Per prompt esplorativi, mantieni l'apertura come descritto nella REGOLA PIÙ IMPORTANTE sopra.
5. Rispondi *SOLO* con il nuovo prompt ottimizzato. Non aggiungere introduzioni, non dire "Ecco il prompt". Sputa fuori solo il codice/testo del prompt formattato in Markdown chiaro.
"""

def load_knowledge_base(folder_path):
    """Carica i file della directory per usarli come contesto per l'IA."""
    kb_text = ""
    
    # Proviamo a caricare il JSON della knowledge base
    json_path = os.path.join(folder_path, "prompt_optimizer_knowledge_base.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                kb_text += "### REGOLE E TECNICHE CHIAVE ESTRATTE DAL JSON ###\n"
                for tech in data.get('techniques', []):
                    # Accetta sia when_to_use/transformation_rules (JSON incluso) sia description/pattern.
                    description = tech.get('description') or tech.get('when_to_use', '')
                    rules = tech.get('pattern') or '; '.join(str(v) for v in (tech.get('transformation_rules') or {}).values())
                    kb_text += f"- {tech.get('name', '')}: {description}\n"
                    kb_text += f"  Regole: {rules}\n"
        except Exception as e:
            pass

    # Carichiamo la tabella di riepilogo in Markdown se esiste
    md_path = os.path.join(folder_path, "prompt_engineering_summary_table.md")
    if os.path.exists(md_path):
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                kb_text += "\n### TABELLA DELLE BEST PRACTICE ###\n"
                kb_text += f.read()[:3000] # Limitiamo a 3000 caratteri per non intagliare l'IA
        except:
            pass
            
    return kb_text

import ssl

_SSL_CTX = ssl.create_default_context()


def _post_json(url, payload, headers, timeout=180):
    """POST JSON con verifica TLS attiva e errori HTTP leggibili."""
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code} da {url}: {detail}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Connessione fallita a {url}: {e.reason}") from None


def optimize_with_anthropic(api_key, system_prompt, user_prompt, model):
    data = _post_json(
        "https://api.anthropic.com/v1/messages",
        {
            "model": model,
            "max_tokens": 4096,
            "temperature": 0.3,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        },
        {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
    )
    return data["content"][0]["text"]


def optimize_with_openai(api_key, system_prompt, user_prompt, model):
    data = _post_json(
        "https://api.openai.com/v1/chat/completions",
        {
            "model": model,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        {"Authorization": f"Bearer {api_key}"},
    )
    return data["choices"][0]["message"]["content"]


def optimize_with_gemini(api_key, system_prompt, user_prompt, model):
    data = _post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
        {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": 0.3},
        },
        {},
    )
    return data["candidates"][0]["content"]["parts"][0]["text"]


def optimize_with_ollama(model_name, system_prompt, user_prompt):
    data = _post_json(
        "http://localhost:11434/api/chat",
        {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.3},
        },
        {},
    )
    return data["message"]["content"]

def main():
    # Se passiamo argomenti da riga di comando, entriamo in "modalità silenziosa"
    # per restituire SOLO il testo (ideale per Automator e scorciatoie)
    quiet_mode = len(sys.argv) > 1

    if not quiet_mode:
        print("=====================================================")
        print(" 🧠 AI PROMPT OPTIMIZER CLI TOOL (Con Knowledge Base) 🧠")
        print("=====================================================\n")
        print("📚 Caricamento file dalla Knowledge Base locale...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    kb_content = load_knowledge_base(current_dir)
    
    if not quiet_mode:
        if not kb_content.strip():
            print("⚠️  Attenzione: non sono riuscito a trovare o leggere bene i file della KB. Userò le conoscenze generali.")
        else:
            print("✅ Knowledge Base caricata con successo!")
        
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(knowledge_base_content=kb_content)
    
    # Modelli configurabili via ambiente: aggiornarli non richiede toccare il codice.
    anthropic_model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-5")
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    ollama_model = os.environ.get("OLLAMA_MODEL", "qwen3:14b")

    # Default: Ollama locale (offline, gratuito). I provider cloud si attivano
    # solo se la rispettiva API key è in ambiente; Anthropic ha priorità perché
    # la knowledge base è tarata su Claude (tag XML, <thinking>).
    provider = "ollama"
    model_name = ollama_model
    api_key = None

    if os.environ.get("ANTHROPIC_API_KEY"):
        provider, api_key, model_name = "anthropic", os.environ["ANTHROPIC_API_KEY"], anthropic_model
    elif os.environ.get("OPENAI_API_KEY"):
        provider, api_key, model_name = "openai", os.environ["OPENAI_API_KEY"], openai_model
    elif os.environ.get("GEMINI_API_KEY"):
        provider, api_key, model_name = "gemini", os.environ["GEMINI_API_KEY"], gemini_model

    if not quiet_mode:
        label = "OLLAMA (Locale)" if provider == "ollama" else provider.upper()
        print(f"✅ Utilizzo provider: {label} - Modello: {model_name}")
    
    if quiet_mode:
        user_prompt = " ".join(sys.argv[1:]).strip()
    else:
        print("\n📝 Scrivi il tuo 'prompt scrauso'. (Premi Invio su una riga vuota per finire)")
        print("-----------------------------------------------------")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "": break
                lines.append(line)
            except EOFError: break
                
        user_prompt = "\n".join(lines).strip()
        
    if not user_prompt: sys.exit(0)
        
    if not quiet_mode:
        print(f"\n⏳ Ottimizzazione in corso tramite l'Intelligenza Artificiale...\n")
        
    try:
        if provider == "anthropic":
            optimized = optimize_with_anthropic(api_key, system_prompt, user_prompt, model_name)
        elif provider == "openai":
            optimized = optimize_with_openai(api_key, system_prompt, user_prompt, model_name)
        elif provider == "gemini":
            optimized = optimize_with_gemini(api_key, system_prompt, user_prompt, model_name)
        else:
            optimized = optimize_with_ollama(model_name, system_prompt, user_prompt)
            
        if not quiet_mode:
            print("✨ ECCO IL TUO PROMPT OTTIMIZZATO E PRONTO ALL'USO: ✨")
            print("=====================================================\n")
            
        print(optimized)
        
        if not quiet_mode:
            print("\n=====================================================")
    except Exception as e:
        if not quiet_mode:
            print(f"❌ Errore durante l'ottimizzazione: {e}")
        else:
            print(f"Errore: {e}")

if __name__ == "__main__":
    main()
