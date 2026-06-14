# Human-LLM-Collaborative-Thematic-Analysis-HLCTA
Human–LLM Collaborative Thematic Analysis (HLCTA) can be used to conduct thematic analysis of qualitative data. It enables researchers to identify, analyze, organize, and report themes within the data. Its main advantages lie in substantially reducing labor costs and mitigating subjective bias across researchers.

## Methodology

HLCTA follows a six-phase collaborative workflow that integrates human analytical judgment with large language model capabilities:

**Phase 1: Data Familiarization**  
Researchers and the LLM jointly explore the data structure and review content. Background information—including research objectives, context, data type, and theoretical framework—is provided to the model via structured prompts to establish shared understanding.

**Phase 2: Initial Coding**  
Leveraging the LLM's semantic comprehension, the system assigns preliminary labels to meaningful segments within the data. A few-shot prompting strategy with 15 sample exemplars ensures stable and accurate initial codes.

**Phase 3: Generating Initial Themes**  
Dispersed codes are consolidated into potential themes. After evaluating few-shot, one-shot, and zero-shot approaches, we deploy one-shot prompting to provide illustrative exemplars, balancing thematic accuracy with richness.

**Phase 4: Developing and Reviewing Themes**  
The LLM merges similar themes and subsumed categories into higher-order meanings. We construct a base theme pool using review texts SFB-0001 through SFB-0053 as reference anchors. The model evaluates each remaining theme against this pool—assigning it to an existing base theme or generating a new one. Researchers then manually inspect and revise the consolidated themes, iterating until consensus is reached.

**Phase 5: Refining and Defining Themes**  
Researchers incorporate LLM input to distill themes into final thematic categories and affective events, establishing clear conceptual definitions.

**Phase 6: Report Production**  
Researchers independently synthesize the analytical results and draft the final manuscript.

This human-in-the-loop design ensures that thematic outputs remain grounded in textual evidence, internally coherent, and mutually distinct while benefiting from LLM-assisted processing efficiency.

[Diagram of the HLCTA Method.tif](https://github.com/user-attachments/files/28925835/Diagram.of.the.HLCTA.Method.tif)

