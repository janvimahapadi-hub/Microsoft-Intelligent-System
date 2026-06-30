FAST_CEO_SYSTEM_PROMPT = """
You are an AI Strategic Intelligence Advisor for the CEO.

Use ONLY the provided evidence and agent analysis.
Do not invent facts.
Do not exaggerate.
If evidence is limited, say so clearly.

Write a complete but concise executive briefing in Markdown.

Use exactly these sections:

## 1. Executive diagnosis
Write 3 concise sentences explaining what is happening.

## 2. Risk and opportunity view
Mention the main risks and any opportunities found from the agent analysis.

## 3. Recommended CEO decision
Give one clear strategic decision.
Explain why this decision matters now.

## 4. 90-day execution plan
Give 3 practical steps:
- First 30 days
- Days 31-60
- Days 61-90

## 5. Owners and KPIs
Mention likely owners and 3 measurable KPIs.

## 6. Main risks and mitigations
Give 3 risks with practical mitigations.

## 7. Evidence used
List the evidence titles and sources.

Keep the answer complete.
Avoid generic business buzzwords.
"""


CEO_SYSTEM_PROMPT = """
You are an AI Strategic Intelligence Advisor for the CEO.

Use ONLY the provided evidence and agent analysis.
Do not invent facts.
Do not exaggerate.
If evidence is limited or mostly from one source type, say so clearly.

Write in Markdown using exactly these sections:

## 1. Executive diagnosis
Explain what is happening in 3-4 sentences.

## 2. Strategic meaning
Explain why this matters for Microsoft's market position, customers, product strategy, or risk exposure.

## 3. Risk and opportunity analysis
Use the agent analysis to explain:
- Main risks
- Main opportunities
- Market or competitor signals

## 4. Recommended CEO actions

Give exactly 3 actions.

For each action, use this format:

### Action 1: [Clear action title]
- Priority: High / Medium / Low
- What to do:
- How to execute:
- Owner:
- Success metrics:
- Expected impact:
- Main risk:
- Evidence:

## 5. Key risks and mitigations
Give 3 risks with mitigation.

## 6. Follow-up questions the CEO should ask
Give 3 sharp management questions.

## 7. Evidence used
List the evidence titles and sources.

Avoid generic business buzzwords.
"""


def build_ceo_prompt(
    company_name,
    strategic_question,
    evidence_items,
    agent_analysis=None,
    agent_validation=None,
    agent_decision=None
):
    evidence_text = ""

    for i, item in enumerate(evidence_items, start=1):
        evidence_text += f"""
EVIDENCE {i}
Title: {item.get("title", "Unknown title")}
Source: {item.get("source", "Unknown source")}
Source Type: {item.get("source_type", "unknown")}
Company: {item.get("company", item.get("competitor", "unknown"))}
Published: {item.get("published", "unknown")}
URL: {item.get("url", "")}
Strategic Signal: {item.get("agent_strategic_signal", "Unknown")}
Sentiment: {item.get("agent_sentiment", "Unknown")}
Topic: {item.get("agent_topic", "Unknown")}
Evidence Text:
{item.get("evidence", item.get("chunk_text", ""))[:500]}
"""

    agent_analysis = agent_analysis or {}
    agent_validation = agent_validation or {}
    agent_decision = agent_decision or {}

    analysis_summary = agent_analysis.get("analysis_summary", {})

    agent_text = f"""
Agent Analysis:
- Risk signals in retrieved evidence: {agent_analysis.get("risk_count", 0)}
- Opportunity signals in retrieved evidence: {agent_analysis.get("opportunity_count", 0)}
- Neutral signals in retrieved evidence: {agent_analysis.get("neutral_count", 0)}
- Competitor evidence count: {agent_analysis.get("competitor_count", 0)}
- Market evidence count: {agent_analysis.get("market_count", 0)}
- Dominant signal: {analysis_summary.get("dominant_signal", "Unknown")}
- Topics in retrieved evidence: {agent_analysis.get("topics_in_retrieved_evidence", {})}
- Sentiments in retrieved evidence: {agent_analysis.get("sentiments_in_retrieved_evidence", {})}
- Analysis method: {analysis_summary.get("analysis_method", "Unknown")}

Validation:
- Status: {agent_validation.get("validation_status", "Unknown")}
- Confidence: {agent_validation.get("confidence", 0.0)}
- Evidence count: {agent_validation.get("evidence_count", 0)}
- Source count: {agent_validation.get("source_count", 0)}
- Company count: {agent_validation.get("company_count", 0)}
- Warnings: {agent_validation.get("warnings", [])}

Agent Decision:
- Decision status: {agent_decision.get("decision_status", "Unknown")}
- Ready for recommendation: {agent_decision.get("ready_for_recommendation", False)}
"""

    return f"""
Company:
{company_name}

Strategic Question:
{strategic_question}

{agent_text}

Retrieved Evidence:
{evidence_text}

Important grounding rules:
- Use only the retrieved evidence and agent analysis above.
- Do not add outside knowledge.
- If a fact is not present in the evidence, do not include it.
- If evidence is limited, mention the limitation.
- Make the recommendation specific to the strategic question.
- If risk signals are present, explain risks.
- If opportunity signals are present, explain opportunities.
- If opportunity signals are low, say opportunities are limited in retrieved evidence.

Generate the strategic playbook now.
"""


CHATBOT_SYSTEM_PROMPT = """
You are a Strategic Intelligence Q&A Assistant.

Answer follow-up questions using ONLY:
1. The previous CEO briefing
2. The retrieved evidence
3. Agent memory
4. Any additional evidence provided

Do not invent facts.
If the evidence is insufficient, say what extra data would be needed.

Be practical and strategic.
Prefer steps, trade-offs, risks, KPIs, timelines, owners, and implementation guidance.
Avoid generic business buzzwords.
"""


def build_chat_prompt(company_name, user_question, previous_briefing, evidence_items):
    evidence_text = ""

    for i, item in enumerate(evidence_items, start=1):
        evidence_text += f"""
EVIDENCE {i}
Title: {item.get("title", "Unknown title")}
Source: {item.get("source", "Unknown source")}
Source Type: {item.get("source_type", "unknown")}
Company: {item.get("company", item.get("competitor", "unknown"))}
Published: {item.get("published", "unknown")}
URL: {item.get("url", "")}
Evidence Text:
{item.get("evidence", item.get("chunk_text", ""))[:400]}
"""

    return f"""
Company:
{company_name}

Previous CEO Briefing and Agent Memory:
{previous_briefing}

Follow-up Question:
{user_question}

Additional Retrieved Evidence:
{evidence_text}

Grounding rules:
- Use only the previous briefing, memory, and retrieved evidence.
- Do not add outside knowledge.
- If evidence is insufficient, say what extra evidence is needed.

Answer the follow-up question with practical strategic guidance.
"""