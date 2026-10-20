# Evaluation Protocol

This document describes how the model outputs in [`main_outputs/`](../main_outputs/) were evaluated for the paper
*Evaluating Reasoning, Grounding, and Stability in LLM-Based GDPR Compliance Assessment*.
For the mapping between file names in this repository and the condition names used in the paper, see the
[Terminology mapping](../README.md#terminology-mapping) in the README.

## 1. Expert rubric and reference labels

The rubric was written by the author **before the model runs**. For each of the seven principles of GDPR
Article 5 it contains five questions, each scored 0–2 against the Ada Health privacy policy, giving a principle
score out of 10. The score is mapped to a reference label:

| Score | Reference label |
|---|---|
| 8–10 | Compliant |
| 4–7 | Partially compliant |
| 0–3 | Non-compliant |

| ID | Principle | Score | Reference label |
|---|---|---|---|
| P1 | Lawfulness, fairness and transparency | 8/10 | Compliant |
| P2 | Purpose limitation | 9/10 | Compliant |
| P3 | Data minimisation | 8/10 | Compliant |
| P4 | Accuracy | 7/10 | Partially compliant |
| P5 | Storage limitation | 8/10 | Compliant |
| P6 | Integrity and confidentiality | 9/10 | Compliant |
| P7 | Accountability | 7/10 | Partially compliant |

- Full rubric with the expert's reasoning: [`golden_standard_bullet_points.md`](../golden_standard_bullet_points.md)
- Machine-readable version (questions, per-question scores, reference labels): [`data/rubric.csv`](../data/rubric.csv)

## 2. Rubric Alignment Score (RAS)

For each principle, the judge (Gemini 3 Flash, thinking mode) labels each of the five rubric questions as
`ENTAILS`, `NOT_ADDRESSED` or `CONTRADICTS`, according to whether the model's justification reaches the
expert's conclusion on that question.

- **Principle RAS** = number of questions labelled `ENTAILS` / 5
- **Run RAS** = mean of the seven principle RAS values

Reported RAS uses the human-corrected label (`human.final_label`). The field `ras_principle_score` in the judge
files was computed by the judge from its own labels, so it is the value **before** correction.

The judge prompt is in [`prompts/LLM_as_judge.md`](../prompts/LLM_as_judge.md) and its outputs are in
[`gemini_judge_output/`](../gemini_judge_output/).

## 3. Justification score (JJS)

For each principle, the judge scores the justification on four dimensions, each on a 1–5 scale:

| Dimension | What it checks |
|---|---|
| Traceability | Whether the rating is linked to the specific passages the output cites, through a coherent, internally consistent chain. It does **not** check whether those passages exist or are relevant; that is the grounding check (Section 4). |
| Principle correctness | Whether the correct GDPR principle logic is applied, without mixing principles |
| Calibration | Whether vagueness and conditionals are handled appropriately (hedging where needed, acknowledging uncertainty) |
| No overreach | Whether the output avoids strong conclusions not supported by what it itself presents |

The judge was instructed not to fact-check citations against the policy; it only sees the model output.

- **Principle JJS** = mean of the four dimension scores. Because each dimension is an integer, principle JJS
  values are always quarter values (x.00, x.25, x.50, x.75).
- **Run JJS** = mean of the seven principle JJS values, rounded (not truncated) to two decimals.

Note: the field `jjs_principle_score` in the judge files is the judge's own one-decimal rounding of this
mean (for example 4.8 for 4.75). The reported values are recomputed from the four dimension scores by
[`scripts/compute_paper_metrics.py`](../scripts/compute_paper_metrics.py). The judge files are left unchanged.

**Reported RAS and JJS values are after human correction** (Section 6).

## 4. Grounding check: Evidence Error Rate (EER)

Each model output cites policy passages per principle (`policy_clauses`: a quote or description plus a section
reference). The author checked every citation against the Ada Health privacy policy.

**Unit of assessment.** The unit is the cited passage (the content quoted or described from a section), not the
section number. A citation counts as erroneous if it is:

- **Non-existent (NE):** the section or the quoted/described text cannot be found in the policy.
- **Unrelated (U):** the passage exists but does not bear on the principle for which it is cited.

**EER** = erroneous citations / total citations (0 = no errors; lower is better). Overall figures are **pooled**:
total errors / total citations across the principles or runs being summarised, not a mean of per-run rates.

**Relevance rule for data minimisation.** A passage is relevant to data minimisation if it concerns:

- limiting the data collected relative to the stated purposes, or
- a minimisation measure listed in EDPB Guidelines 4/2019 on Article 25, para. 76 (for example pseudonymisation
  once identification is no longer needed, or deletion of data that is no longer necessary).

General security measures (encryption, certifications, breach procedures) and retention periods as such count as
**unrelated** when cited for data minimisation.

The per-principle results are in the `Master_Table` sheet of
[`scripts/outputs/GDPR_thesis_analysis_results.xlsx`](../scripts/outputs/GDPR_thesis_analysis_results.xlsx):
column `section_result FGS` holds `errors/citations` (or `0`), and column `SECTION-NOTE` holds the error type
(`not exist` = NE; `unrelated` or `legally misplaced` = U).

## 5. Label agreement and stability

- **Label agreement:** share of the seven principles where a run's compliance label equals the reference label.
- **Flip rate:** for each pair of conditions of the same model, the share of the seven principles whose label differs.

## 6. Judge validation

The author reviewed all **420 RAS judgements** (12 runs × 7 principles × 5 questions). In the judge files each
judgement carries a `human` block with `override`, `final_label` and `note`.

| | Count |
|---|---|
| Judgements reviewed | 420 |
| Judge errors corrected | 37 (8.8%) |
| on Grok outputs | 22 |
| on GPT-5.2 outputs | 15 |
| Over-generous (judge said `ENTAILS`) | 34 |
| `ENTAILS` → `NOT_ADDRESSED` | 31 |
| `ENTAILS` → `CONTRADICTS` | 3 |
| Too strict (`NOT_ADDRESSED` → `ENTAILS`) | 3 |

`scripts/compute_paper_metrics.py` recounts these from the judge files.
