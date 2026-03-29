# Prompt Templates

This directory contains the precise prompt templates used throughout the experimental phases of the master's thesis: **"Assessing Privacy Policy Compliance with GDPR Article 5 Using Large Language Models: The Role of Prompt Design"**.

The research focuses on how the design and structure of prompts influence the legal reasoning and stability of Large Language Models (LLMs) when evaluating privacy policies.

## Prompt Categories

### 1. Comparative Versions (Evolutionary Phases)
These prompts represent the iterative refinement of the instructions given to the LLMs (GPT-5.2 and Grok).

*   **[`1st_version_few_shot.md`](1st_version_few_shot.md)**: The initial attempt at structured compliance assessment using a few-shot approach.
*   **[`2nd_version_few_shot.md`](2nd_version_few_shot.md)**: Refined instructions based on preliminary results to improve focus on specific GDPR principles.
*   **[`3rd_version_few_shot.md`](3rd_version_few_shot.md)**: The most advanced few-shot prompt. It incorporates:
    *   **Expert Personas**: Assigning the role of a "GDPR compliance expert".
    *   **Legal Anchors**: Verbatim text from GDPR Article 5 and Recital 39.
    *   **Interpretative Guidance**: References to EDPB Guidelines (e.g., 4/2019).
    *   **Contextual Examples**: Real-world few-shot examples from policies like Uber, WhatsApp, and Airbnb to demonstrate the required reasoning depth and tone.
    *   **JSON Schema**: Strict output formatting to ensure consistency and facilitate automated analysis.
*   **[`3rd_version_zero_shot.md`](3rd_version_zero_shot.md)**: A zero-shot variant of the 3rd version, used to measure the "Few-Shot Gain"—the performance improvement attributable to providing examples rather than just instructions.

### 2. Evaluation Prompts
*   **[`LLM_as_judge.md`](LLM_as_judge.md)**: Used by Gemini to evaluate the outputs of GPT-5.2 and Grok. This prompt instructs the "Judge" to score the primary models on:
    *   **RAS (Rubric Alignment Score)**: Correctness against the legally defined "Golden Standard".
    *   **JJS (Justification Quality Score)**: The quality of the legal reasoning (traceability, lack of overreach, and calibration).

## Key Design Principles
As detailed in **`thesis.pdf`**, the prompt design follows several core strategies:
1.  **Chain-of-Thought (CoT)**: Encouraging the model to quote policy clauses before providing a rating.
2.  **Legal Contextualization**: Embedding specific legal texts (Articles and Recitals) to reduce hallucinations.
3.  **Consistency**: Using standardized JSON outputs to enable the "Flip Rate" analysis.

For more details on the experimental setup and the results of these prompting strategies, please refer to the [root README.md](../README.md).
