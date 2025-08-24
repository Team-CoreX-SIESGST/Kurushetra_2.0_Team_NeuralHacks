"""
Prompt templates for OmniSearch AI.
Contains templates for model routing, reranking, and final summarization.
"""

# Routing Fallback Template
ROUTING_FALLBACK_TEMPLATE = """You are a lightweight router that selects the most appropriate model intent.
Intents: code_generation, research_longform, factual_short_answer, table_query, image_analysis, summarize.

Task: {task_description}

Rules:
- Reply with only the chosen intent key.
- If ambiguous, choose 'research_longform'.
"""

# Cross-encoder Reranker Template
RERANKER_TEMPLATE = """You are a relevance scorer. Score snippets 0–100 by query match.

Query:
{query}

Snippets:
[SNIP_1] id:{id1}
{text1}
...

Return JSON:
[
  {{"id":"id1","score":87,"justification":"matches keywords"}},
  ...
]"""

# Final Summarizer Template
FINAL_SUMMARIZER_TEMPLATE = """You are an evidence-based summarizer. Use ONLY provided sources.

User query:
{user_query}

Sources:
{sources_block}

Rules:
1. Concise answer (2–6 sentences).
2. Cite sources [SRC_n].
3. Confidence 0.0–1.0.
4. Sources list with src_id, quote, url_or_file.
5. Include code only if requested.
6. If insufficient → {{"answer":"INSUFFICIENT_EVIDENCE","confidence":0.0,"sources":[]}}

Return JSON only:
{{
  "answer":"...",
  "confidence":0.8,
  "sources":[{{"src_id":"SRC_1","quote":"...","url_or_file":"..."}}],
  "code":{{"language":"python","content":"..."}} // optional
}}"""

def format_routing_prompt(task_description: str) -> str:
    """Format the routing fallback prompt with task description."""
    return ROUTING_FALLBACK_TEMPLATE.format(task_description=task_description)

def format_reranker_prompt(query: str, snippets: list) -> str:
    """Format the reranker prompt with query and snippets."""
    snippets_text = ""
    for i, snippet in enumerate(snippets):
        snippets_text += f"[SNIP_{i+1}] id:{snippet['id']}\n{snippet['text']}\n\n"
    
    return RERANKER_TEMPLATE.format(query=query, id1=snippets[0]['id'] if snippets else "", text1=snippets[0]['text'] if snippets else "")

def format_summarizer_prompt(user_query: str, sources: list) -> str:
    """Format the final summarizer prompt with user query and sources."""
    sources_block = ""
    for i, source in enumerate(sources):
        sources_block += f"SRC_{i+1}: {source.get('text', '')}\n"
    
    return FINAL_SUMMARIZER_TEMPLATE.format(user_query=user_query, sources_block=sources_block)
