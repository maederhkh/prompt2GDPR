# Prompts

This directory contains the prompts used in the paper *Evaluating Reasoning, Grounding, and Stability in LLM-Based
GDPR Compliance Assessment*. In each run, the Ada Health privacy policy (November 2025 version) was supplied after
the prompt; the policy text is not included here.

| File | Condition(s) | Contents |
|---|---|---|
| `3rd_version_zero_shot.md` | ZS, ZS-Ext | Final zero-shot prompt ("Zero-shot.3rd" / "1st zero-shot" in older files). Excerpts of Article 5 and key interpretive points from Recital 39. |
| `1st_version_few_shot.md` | FS1 | Excerpts of Article 5, Recital 39 points, and the four CLAUDETTE-based examples |
| `2nd_version_few_shot.md` | FS2 | Principle names only, Recital 39 points, and the same four examples |
| `3rd_version_few_shot.md` | FS3, FS3-Ext | As FS2, plus WP260 rev.01 (Guidelines on Transparency) and EDPB Guidelines 4/2019 on Article 25 |
| `LLM_as_judge.md` | — | Prompt for the Gemini 3 Flash judge (RAS and JJS) |

The four examples cover lawfulness/fairness/transparency, purpose limitation, storage limitation and accuracy.
"Ext" is GPT-5.2's extended thinking mode and Grok's expert mode; the prompt is the same as in the standard run.
