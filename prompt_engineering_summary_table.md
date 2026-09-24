# Prompt Engineering 2026: Tabella Riassuntiva Pareto

## 7 Tecniche Vitali (80% Risultati)

| # | Tecnica | Impatto | Metriche Evidence-Based | Quando Usare | Esempio Trigger |
|---|---------|---------|-------------------------|--------------|-----------------|
| **1** | **Clear Instructions & Constraints** ⭐⭐⭐ | Fondamento universale | • -31% errori<br>• +30% relevance<br>• Base per tutto | **SEMPRE** | Prompt vago, no vincoli, formato ambiguo |
| **2** | **Context Engineering (RTFC)** ⭐⭐⭐ | +30% accuracy | • +30% accuracy<br>• -42% output generici<br>• +35% multi-turn | Task complessi, writing, decisioni | "Scrivi email" senza background cliente |
| **3** | **Structured Format (XML/MD)** ⭐⭐⭐ | Parsing + consistenza | • +20% instruction adherence<br>• Migliora parsing<br>• Claude: XML native | Prompt >200 token, multi-section | Dati + istruzioni + vincoli misti |
| **4** | **Chain-of-Thought (CoT)** ⭐⭐⭐ | +45% reasoning | • +19.1 punti MMLU<br>• +30-50% reasoning<br>• +50% math tasks | Reasoning, logica, matematica | "Calcola", "Risolvi", multi-step |
| **5** | **Few-Shot Prompting** ⭐⭐⭐ | +33% accuracy | • +25-40% vs zero-shot<br>• +30% performance<br>• +20% consistency | Formatting, classificazione | SKU codes, medical coding, patterns |
| **6** | **Role Prompting** ⭐⭐ | +20% domain accuracy | • +15-25% domain tasks<br>• Migliora quality<br>• Professional output | Domain-specific (legal, medical) | "Analizza contratto", expertise richiesta |
| **7** | **Iterative Testing** ⭐⭐⭐ | +22% per cycle | • +22% accuracy/cycle<br>• -75% debug time<br>• 90%+ reliability | **PRODUCTION sempre** | High-stakes, usati 1000+ volte |

---

## Quick Decision Matrix

| Task Type | Priorità 1 | Priorità 2 | Priorità 3 |
|-----------|-----------|-----------|-----------|
| **Reasoning/Math** | CoT | Context | Iterate |
| **Classification** | Few-shot | Format | Clear |
| **Writing** | Context | Role | Constraints |
| **Analysis** | Context | CoT | Role |
| **Production** | Iterate | Context | CoT |
| **Prototype** | Clear | Zero-shot step-by-step | - |

---

## Applicabilità & ROI

```
Applicabilità (% prompt che beneficiano):
Clear Instructions  ████████████████████ 100%
Context Engineering ████████████████     80%
Structured Format   ██████████████       70%
Few-Shot            ██████████           50%
CoT                 ████████             40%
Role Prompting      ██████               30%
Iterative Testing   ████████████████████ 100% (production)

ROI (improvement / effort):
Context Engineering ████████████████████ Highest
Clear Instructions  ███████████████████  Highest
Few-Shot            █████████████████    High
CoT                 ████████████████     High
Structured Format   ███████████████      High
Role Prompting      ████████████         Medium
Iterative Testing   ███████████████████  High (compounding)
```

---

## Model-Specific Notes

| Model | Preferenze | Evitare | Best Practice |
|-------|-----------|---------|---------------|
| **Claude** | XML tags, explicit instructions | Aggressive language (NEVER, ALL CAPS) | Usa `<thinking>` tags per reasoning |
| **GPT** | Markdown/XML, conversational | N/A | Pin model snapshots, zero-shot first |
| **Gemini** | Markdown, few-shot preferred | Zero-shot | Place critical info at end (2M context) |

---

## Improvement Ranges (Evidence-Based)

### Top Performers
- **Chain-of-Thought**: +19.1 a +50% accuracy (source: arXiv, MMLU benchmarks)
- **Few-Shot**: +25-40% vs zero-shot (source: multiple studies)
- **Context Engineering**: +30% accuracy, -42% genericità (source: SQ Magazine stats)

### Foundation Layer
- **Clear Instructions**: -31% errors, +30% relevance (universal)
- **Structured Format**: +20% instruction adherence (Claude 4.x)

### Compounding Value
- **Iterative Testing**: +22% per cycle, -75% debug time
  - Example: 17% → 91% accuracy attraverso refinement sistematico (W&B case study)

---

## Cost-Benefit Quick Guide

### Low Cost, High Impact (Start Here)
1. Clear Instructions & Constraints
2. Structured Format (XML/Markdown)
3. Zero-shot + "Let's think step by step"

### Medium Cost, Very High Impact
4. Context Engineering (RTFC)
5. Few-Shot (2-3 examples)

### Higher Cost, Specialized Impact
6. Chain-of-Thought (più token)
7. Iterative Testing (tempo + compute)

---

## Formula Pratica

```
Prompt Base → +Clear Instructions (must) → +Context (se complesso) 
→ +Format (se lungo) → +CoT/Few-shot (se reasoning/pattern)
→ +Role (se domain) → Test & Iterate (se production)

Expected: 50-200% improvement da baseline generic a optimized
```

---

## Anti-Patterns da Evitare

❌ Prompt >500 parole senza struttura  
❌ Info critiche sepolte nel mezzo (lost in middle)  
❌ Nessun constraint su output  
❌ Deploy senza testing  
❌ ALL CAPS AGGRESSIVE LANGUAGE  
❌ Copy-paste prompt senza customizzazione  

---

## Fonti Chiave (2026)

**Papers:**
- Schulhoff et al. "The Prompt Report" (arXiv:2406.06608)
- Liu et al. "Lost in the Middle" (arXiv:2307.03172)
- Wei et al. "Chain-of-Thought Prompting" (NeurIPS 2022)

**Official Guides:**
- Anthropic Claude Best Practices (2026)
- OpenAI GPT-5 Prompting Guide (2025)

**Data:**
- SQ Magazine Prompt Engineering Statistics (2025)
- W&B Case Studies (2026)

---

*Last Updated: March 2026*  
*Next Review: September 2026*
