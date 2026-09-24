# Prompt Optimizer

Strumento a riga di comando in Python che riscrive un prompt applicando una knowledge base di tecniche di prompt engineering, costruita a partire da paper e guide ufficiali.

L'idea risale al 2024, ai primi mesi di uso degli LLM; questa versione, con la knowledge base attuale e il codice, è di marzo–maggio 2026.

## Cosa fa

- Prende un prompt, passato come argomento o incollato nel terminale, e lo manda a un modello insieme alla knowledge base.
- La knowledge base descrive 7 tecniche prioritarie, ognuna con i segnali che la rendono necessaria, le regole di trasformazione e un esempio prima/dopo: Clear Instructions & Constraints, Context Engineering (RTFC), Structured Formatting (XML/Markdown), Chain-of-Thought (CoT) Prompting, Few-Shot Prompting, Role Prompting, Iterative Refinement & Testing.
- Stampa il prompt riscritto.
- Sceglie il modello in base alla chiave presente nell'ambiente: Anthropic, OpenAI o Gemini. Senza chiavi usa un modello locale con Ollama.
- Usa solo la libreria standard di Python, quindi non c'è niente da installare.

`update_kb.py` scarica paper recenti da arXiv e le guide ufficiali di Anthropic e OpenAI, poi rigenera la knowledge base con un modello.

## Uso

```bash
export ANTHROPIC_API_KEY=...    # oppure OPENAI_API_KEY o GEMINI_API_KEY; senza chiavi usa Ollama
python3 ai_optimizer.py "Scrivi un piano marketing"    # stampa il prompt riscritto
python3 ai_optimizer.py                                 # chiede il prompt nel terminale
python3 -m unittest discover -s tests                   # test della knowledge base
```

Il modello si cambia con `ANTHROPIC_MODEL`, `OPENAI_MODEL`, `GEMINI_MODEL` o `OLLAMA_MODEL`.

## File

| File | Contenuto |
|---|---|
| `ai_optimizer.py` | lo strumento |
| `prompt_optimizer_knowledge_base.json` | le 7 tecniche, con principi, anti-pattern, checklist, albero decisionale e note per modello |
| `prompt_engineering_summary_table.md` | tabella di riepilogo delle tecniche |
| `update_kb.py` | aggiornamento della knowledge base da arXiv e guide ufficiali |
| `docs/ricerca-prompt-engineering-2026-03.md` | la ricerca da cui nasce la knowledge base |
| `docs/esempio-piano-marketing.md` | un esempio completo prima/dopo |

## Come l'ho costruito

Ho progettato lo strumento e guidato lo sviluppo; il codice l'ha scritto un coding agent.

Nella revisione per la pubblicazione è emerso un errore: il caricamento della knowledge base passava al modello solo i nomi delle tecniche, perché cercava due campi che il file non contiene. Ora passa anche le regole, e un test lo verifica.

## Limiti

- `update_kb.py` è sperimentale: nell'ultima esecuzione registrata il download delle fonti è fallito per un problema di certificati SSL di Python su macOS.
- Il test copre il caricamento della knowledge base, non la chiamata al modello.
