# Gemini Judge (LLM-as-Judge) Evaluation Outputs

This directory contains the structured evaluation data generated using **Gemini** as an automated judge (LLM-as-judge). These outputs correspond to **Metric 1** of the thesis evaluation framework: **Rubric Alignment (RAS)** and **Justification Quality (JJS)**.

## Overview

The purpose of these evaluations is to assess the quality and legal alignment of the compliance justifications produced by the primary models (GPT-5.2 and Grok). 

- **Rubric Alignment Score (RAS)**: Measures how well the model's reasoning matches the "Golden Standard" rubric developed by a legal expert. Gemini compares model justifications against five specific compliance questions per GDPR principle.
- **Justification Quality Score (JJS)**: Evaluates the model's reasoning on four dimensions: traceability (linking to policy clauses), principle correctness, calibration (handling uncertainty), and no overreach.

## Directory Structure

The outputs are organized by the primary model being evaluated:

- **`gpt5.2/`**: Evaluations of GPT-5.2's compliance assessments.
  - **`zero_shot/`**: Results for baseline and structured zero-shot prompt versions.
  - **`few_shot/`**: Results for 1st, 2nd, and 3rd few-shot prompt versions, including extended thinking modes.
- **`grok/`**: Evaluations of Grok's compliance assessments.
  - **`zero_shot/`**: Results for baseline and structured zero-shot prompt versions.
  - **`few_shot/`**: Results for 1st, 2nd, and 3rd few-shot prompt versions, including expert mode runs.

## Methodology Note

As discussed in the thesis (**Section 3.5.2**), while Gemini serves as an efficient automated evaluator, its judgments were subjected to a manual **Judge Failure Probe (JFB)**. This identified cases where the judge was influenced by surface-level lexical similarities rather than substantive legal reasoning. The final scores reported in the thesis results include manual corrections to ensure reliability.
