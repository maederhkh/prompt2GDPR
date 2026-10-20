# Gemini Judge (LLM-as-Judge) Outputs

This directory contains the evaluations produced by **Gemini 3 Flash** (thinking mode) acting as judge, on
25–27 February 2026, for each of the 12 runs in [`main_outputs/`](../main_outputs/README.md). The judge prompt is
[`prompts/LLM_as_judge.md`](../prompts/LLM_as_judge.md).

- **RAS (rubric alignment):** for each principle, the judge labels each of the five expert rubric questions as
  `ENTAILS`, `NOT_ADDRESSED` or `CONTRADICTS` against the model's justification.
- **JJS (justification quality):** for each principle, the judge scores traceability, principle correctness,
  calibration and no overreach, each 1–5.

## Directory structure

Files mirror [`main_outputs/`](../main_outputs/README.md): `gpt5.2/` and `grok/`, each with `zero_shot/` and
`few_shot/`. GPT-5.2's extended thinking runs (ZS-Ext, FS3-Ext) are named `3rd_output_thinking_extended.json`;
Grok's expert-mode runs are named `3rd_output_expert.json`. The mapping to the paper's condition names (ZS, ZS-Ext,
FS1, FS2, FS3, FS3-Ext) is in the [Terminology mapping](../README.md#terminology-mapping).

## Fields

Each file is a list with one entry per principle:
- `judge_ras.bullets[]`: one item per rubric question, with the judge's `label` and `rationale`, and a `human` block
  holding the author's review (`override`, `final_label`, `note`)
- `jjs`: the four dimension scores, `jjs_principle_score` and `brief_notes`

## Human correction

The author reviewed all 420 RAS judgements (12 runs × 7 principles × 5 questions) and corrected 37 of them (8.8%);
see [`docs/evaluation_protocol.md`](../docs/evaluation_protocol.md#6-judge-validation).

These files are kept as produced, with the author's review added in the `human` blocks. Two fields should not be
used as reported values:
- `ras_principle_score` was computed by the judge from its own labels, i.e. **before** human correction. Reported
  RAS uses `human.final_label`.
- `jjs_principle_score` is the judge's own rounding to one decimal (e.g. 4.8 for 4.75). Reported JJS is the exact
  mean of the four dimension scores, which is always a quarter value.

`scripts/compute_paper_metrics.py` recomputes both from the fields above.
