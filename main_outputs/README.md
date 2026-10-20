# Main Model Outputs (GDPR Compliance Assessments)

This directory contains the raw JSON outputs of **GPT-5.2** and **Grok 4.1**: their assessments of the Ada Health
GmbH privacy policy (November 2025 version) against the seven principles of GDPR Article 5. These files are the
evidence for the paper and are kept exactly as the models produced them.

Each file is one run: one model under one condition, in a fresh chat. Run dates, interfaces and other details are
in the [Study details](../README.md#study-details) section of the main README.

## Conditions and files

"Ext" is GPT-5.2's extended thinking mode and Grok's expert mode.

| Condition | Prompt | GPT-5.2 (`gpt5.2/`) | Grok (`grok/`) |
|---|---|---|---|
| ZS | `prompts/3rd_version_zero_shot.md` | `zero_shot/3rd_output.json` | `zero_shot/3rd_output.json` |
| ZS-Ext | `prompts/3rd_version_zero_shot.md` | `zero_shot/3rd_output_extended_thinking.json` | `zero_shot/3rd_output_expert.json` |
| FS1 | `prompts/1st_version_few_shot.md` | `few_shot/1st_output.json` | `few_shot/1st_output.json` |
| FS2 | `prompts/2nd_version_few_shot.md` | `few_shot/2nd_output.json` | `few_shot/2nd_output.json` |
| FS3 | `prompts/3rd_version_few_shot.md` | `few_shot/3rd_output.json` | `few_shot/3rd_output.json` |
| FS3-Ext | `prompts/3rd_version_few_shot.md` | `few_shot/3rd_output_extended_thinking.json` | `few_shot/3rd_output_expert.json` |

The few-shot prompts (FS1–FS3) include the same four annotated examples based on the CLAUDETTE project.

## Contents of the JSON files

Each file is a list with one entry per principle, following the schema requested in the prompts:
- `principle`: the Article 5 principle being assessed
- `article_5_text`: the model's reproduction of the Article 5 wording
- `recital_39_reference`: the part of Recital 39 the model relates to the principle
- `policy_clauses`: the policy passages the model cites (`quote` and `section`); these are the citations checked
  in the grounding analysis (EER)
- `rating`: the compliance label (**Compliant**, **Partially compliant** or **Non-compliant**)
- `justification`: the model's reasoning linking the policy text to the principle

## Analysis

`scripts/analyze_gdpr_outputs.py` parses these files and checks the reproduced Article 5 text. The figures reported
in the paper are reproduced by `scripts/compute_paper_metrics.py`; see
[`docs/evaluation_protocol.md`](../docs/evaluation_protocol.md) for the definitions.
