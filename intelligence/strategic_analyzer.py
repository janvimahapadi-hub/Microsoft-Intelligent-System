from retrieval.retriever import Retriever
from llm.ollama_client import generate_response
from llm.prompts import (
    FAST_CEO_SYSTEM_PROMPT,
    CEO_SYSTEM_PROMPT,
    build_ceo_prompt,
    CHATBOT_SYSTEM_PROMPT,
    build_chat_prompt
)

def normalize_text(text):
    return text.lower().strip()


def question_contains_any(question, keywords):
    question = normalize_text(question)

    return any(
        keyword.lower() in question
        for keyword in keywords
    )


def detect_question_domain(question):
    """
    Detects the strategic domain of the CEO question.
    This helps the system retrieve evidence for Windows, Xbox, GitHub, Azure,
    Copilot, security, regulation, partners, or general Microsoft strategy.
    """

    domains = []

    if question_contains_any(question, ["windows", "pc", "device", "surface"]):
        domains.append("windows")

    if question_contains_any(question, ["xbox", "gaming", "game pass", "activision", "minecraft"]):
        domains.append("gaming")

    if question_contains_any(question, ["github", "developer", "developers", "devops", "code"]):
        domains.append("developer")

    if question_contains_any(question, ["azure", "cloud", "infrastructure", "datacenter", "data center"]):
        domains.append("cloud")

    if question_contains_any(question, ["copilot", "microsoft 365", "office", "teams", "outlook", "productivity"]):
        domains.append("productivity")

    if question_contains_any(question, ["security", "defender", "entra", "identity", "cyber", "threat"]):
        domains.append("security")

    if question_contains_any(question, ["ai", "artificial intelligence", "agent", "agents", "foundry", "model"]):
        domains.append("ai")

    if question_contains_any(question, ["regulation", "regulatory", "privacy", "compliance", "governance", "law"]):
        domains.append("regulation")

    if question_contains_any(question, ["partner", "partners", "ecosystem", "channel"]):
        domains.append("partners")

    if question_contains_any(question, ["competitor", "competition", "aws", "google", "nvidia", "apple", "meta", "anthropic"]):
        domains.append("competition")

    if not domains:
        domains.append("general")

    return domains


def build_domain_queries(company_name, domain):
    """
    Returns domain-specific retrieval queries.
    These are strategic lenses, not final answers.
    """

    domain_queries = {
        "windows": [
            f"{company_name} Windows strategy product adoption enterprise security",
            f"{company_name} Windows AI devices user experience productivity",
            f"{company_name} Windows risks competition security adoption"
        ],
        "gaming": [
            f"{company_name} Xbox gaming Game Pass strategy growth",
            f"{company_name} gaming competition consumer engagement cloud gaming",
            f"{company_name} Activision Xbox risks opportunities"
        ],
        "developer": [
            f"{company_name} GitHub developer ecosystem AI productivity",
            f"{company_name} developer platform tools APIs opportunity",
            f"{company_name} GitHub Copilot risks adoption competition"
        ],
        "cloud": [
            f"{company_name} Azure cloud growth enterprise AI infrastructure",
            f"{company_name} cloud competition AWS Google risk",
            f"{company_name} Azure opportunity security compliance customers"
        ],
        "productivity": [
            f"{company_name} Copilot Microsoft 365 productivity adoption",
            f"{company_name} Teams Outlook Office AI workflow opportunity",
            f"{company_name} productivity risk customer adoption governance"
        ],
        "security": [
            f"{company_name} cybersecurity Defender Entra identity threat risk",
            f"{company_name} security opportunity trust compliance enterprise",
            f"{company_name} AI security governance cyberattack mitigation"
        ],
        "ai": [
            f"{company_name} AI strategy Copilot Foundry agents opportunity",
            f"{company_name} AI risks governance security competition",
            f"{company_name} enterprise AI adoption productivity transformation"
        ],
        "regulation": [
            f"{company_name} AI regulation privacy compliance governance",
            f"{company_name} regulatory risk data protection trust",
            f"{company_name} responsible AI compliance enterprise customers"
        ],
        "partners": [
            f"{company_name} partner ecosystem transformation customer adoption",
            f"{company_name} partners AI cloud opportunity enterprise",
            f"{company_name} partner risk dependency integration channel"
        ],
        "competition": [
            f"{company_name} competitors AWS Google NVIDIA Apple AI cloud",
            f"{company_name} competitive pressure cloud AI productivity",
            f"{company_name} market position competitors strategic risk"
        ],
        "general": [
            f"{company_name} strategic opportunities risks market trends",
            f"{company_name} competitors customers product strategy",
            f"{company_name} growth risk innovation enterprise adoption"
        ]
    }

    return domain_queries.get(domain, domain_queries["general"])


def build_strategic_queries(company_name, question):
    """
    Builds dynamic strategic search queries from the user's actual question.

    The retrieval plan always includes:
    1. Original user question
    2. Topic-specific queries
    3. Opportunity lens
    4. Risk lens
    5. Competitor / market lens
    """

    domains = detect_question_domain(question)

    queries = []

    # Always keep the original CEO question as the strongest query.
    queries.append(question)

    # Add domain-specific retrieval lenses.
    for domain in domains:
        queries.extend(
            build_domain_queries(company_name, domain)
        )

    # Add generic strategic lenses based on the actual question.
    queries.extend([
        f"{company_name} opportunity related to {question}",
        f"{company_name} risk related to {question}",
        f"{company_name} competitors market trend related to {question}",
        f"{company_name} customer impact execution plan related to {question}"
    ])

    # Deduplicate while preserving order.
    unique_queries = []
    seen = set()

    for query in queries:
        normalized = query.lower().strip()

        if normalized in seen:
            continue

        seen.add(normalized)
        unique_queries.append(query)

    # Limit query count for speed.
    return unique_queries[:8]


def deduplicate_evidence(evidence_items, max_items=5):
    """
    Remove duplicate or near-duplicate evidence by URL/title/chunk ID.
    FAISS often returns multiple chunks from the same article.
    """

    seen = set()
    unique_items = []

    for item in evidence_items:
        key = (
            item.get("url")
            or item.get("title")
            or str(item.get("chunk_id"))
        )

        if key in seen:
            continue

        seen.add(key)
        unique_items.append(item)

    # FAISS L2 distance normally means lower score = closer match.
    unique_items = sorted(
        unique_items,
        key=lambda x: x.get("score", 999999)
    )

    return unique_items[:max_items]


def calculate_confidence(evidence_items):
    """
    Confidence is based on:
    - number of retrieved evidence items
    - source diversity
    - source type diversity
    - URL diversity

    This is not model confidence. It is retrieval/evidence confidence.
    """

    if not evidence_items:
        return 0.0

    evidence_count = len(evidence_items)

    sources = set(
        item.get("source", "unknown") for item in evidence_items
    )

    source_types = set(
        item.get("source_type", "unknown") for item in evidence_items
    )

    urls = set(
        item.get("url", "") for item in evidence_items if item.get("url")
    )

    confidence = 0.3

    if evidence_count >= 3:
        confidence += 0.2

    if evidence_count >= 5:
        confidence += 0.1

    if len(sources) >= 2:
        confidence += 0.15

    if len(sources) >= 3:
        confidence += 0.1

    if len(source_types) >= 2:
        confidence += 0.1

    if len(urls) >= 3:
        confidence += 0.05

    return min(round(confidence, 2), 1.0)


def build_fallback_playbook(company_name, strategic_question, evidence_items, error_message):
    """
    If Ollama fails or times out, the dashboard still returns a useful,
    evidence-aware strategic playbook instead of crashing.
    """

    evidence_titles = []

    for item in evidence_items:
        title = item.get("title", "Unknown title")
        source = item.get("source", "Unknown source")
        evidence_titles.append(f"- {title} ({source})")

    evidence_text = "\n".join(evidence_titles)

    return f"""
## 1. Executive diagnosis

The system retrieved relevant evidence for the question: **{strategic_question}**.

The local LLM was too slow or unavailable during generation, so this fallback playbook was created using the retrieved evidence metadata. The recommendation should be treated as a structured decision-support output rather than a final strategic decision.

## 2. Strategic meaning

The retrieved evidence indicates that {company_name} should evaluate this topic through three lenses: business impact, execution feasibility, and strategic risk. The key management challenge is to move from broad AI interest into measurable initiatives with clear ownership, KPIs, and risk controls.

## 3. Recommended CEO actions

### Action 1: Validate the strongest opportunity with evidence-backed use cases
- Priority: High
- What to do: Identify the most commercially relevant use cases from the retrieved evidence.
- How to execute:
  1. Group evidence into opportunity, risk, customer impact, and technology themes.
  2. Select the top 2 themes with the clearest business value.
  3. Assign owners to test each theme through a 30-90 day initiative.
- Who should own it: Product Strategy, Azure, Security, Sales, and Partner teams.
- Success metrics: Adoption rate, customer pipeline impact, deployment speed.
- Expected impact: Better prioritization and reduced strategic guesswork.
- Main risk: Acting on evidence that is too narrow or biased.
- Evidence: See evidence list below.

### Action 2: Convert the recommendation into an execution roadmap
- Priority: High
- What to do: Turn the strategic recommendation into a phased action plan.
- How to execute:
  1. Define 30-day validation tasks.
  2. Define 60-day pilot implementation.
  3. Define 90-day measurement and scaling criteria.
- Who should own it: Business unit leadership with support from data, product, and compliance teams.
- Success metrics: Pilot completion, measurable customer value, risk reduction.
- Expected impact: Moves the recommendation from idea to execution.
- Main risk: Weak coordination between technical and business teams.
- Evidence: See evidence list below.

### Action 3: Improve confidence through wider evidence collection
- Priority: Medium
- What to do: Add competitor, market, and community sources before making a major strategic commitment.
- How to execute:
  1. Add competitor source tracking.
  2. Add market/news signals.
  3. Add customer/community sentiment signals.
- Who should own it: Market Intelligence, Strategy, and Data teams.
- Success metrics: Source diversity, confidence score, evidence freshness.
- Expected impact: Stronger and more balanced recommendations.
- Main risk: Slower decision-making if evidence collection becomes too broad.
- Evidence: See evidence list below.

## 4. Key risks and mitigations

- Risk: Evidence may be concentrated in limited sources.  
  Mitigation: Add competitor, market, and public sentiment sources.

- Risk: Recommendation may be too generic.  
  Mitigation: Require every recommendation to include owner, KPI, timeline, and risk.

- Risk: Local LLM may be slow during live demos.  
  Mitigation: Use cached retrieval, streaming generation, smaller models, and fallback output.

## 5. Follow-up questions the CEO should ask

1. Which business unit should own the first 90-day execution plan?
2. What KPI would prove this recommendation is working?
3. What competitor or market evidence is missing?

## 6. Evidence used

{evidence_text}

---

Fallback reason: {error_message}
"""


def build_fallback_chat_answer(company_name, user_question, evidence_items, error_message):
    evidence_titles = []

    for item in evidence_items:
        title = item.get("title", "Unknown title")
        source = item.get("source", "Unknown source")
        evidence_titles.append(f"- {title} ({source})")

    evidence_text = "\n".join(evidence_titles)

    return f"""
## Follow-up answer

The system retrieved evidence for the follow-up question: **{user_question}**.

The local LLM was too slow or unavailable, so this fallback answer is based on the retrieved evidence metadata.

### Practical next step

Use the retrieved evidence to create a short execution plan with:

1. A clear owner
2. A 30-60-90 day timeline
3. 2-3 measurable KPIs
4. Known risks and mitigations
5. Additional evidence needed before final decision

### Evidence retrieved

{evidence_text}

### Limitation

This fallback response does not include full LLM reasoning. To improve the answer, use a smaller local model, reduce top_k, or shorten evidence text.

Fallback reason: {error_message}
"""

def is_incomplete_answer(answer):
    if not answer:
        return True

    required_markers = [
        "## 1.",
        "## 2.",
        "## 3.",
        "## 4.",
        "## 5.",
        "## 6."
    ]

    missing_sections = [
        marker for marker in required_markers if marker not in answer
    ]

    if missing_sections:
        return True

    unfinished_endings = [
        "but",
        "and",
        "or",
        "because",
        "while",
        "however,"
    ]

    last_words = answer.strip().lower().split()[-3:]
    last_text = " ".join(last_words)

    return any(last_text.endswith(word) for word in unfinished_endings)


class StrategicAnalyzer:
    def __init__(self, company_name="Microsoft"):
        self.company_name = company_name
        self.retriever = Retriever()

    def retrieve_strategic_evidence(self, strategic_question, top_k=5):
        all_evidence = []

        strategic_queries = build_strategic_queries(
        self.company_name,
        strategic_question
       )
        
        print("\nStrategic retrieval queries:")
        for query in strategic_queries:
            print("-", query)

        for query in strategic_queries:
            try:
                results = self.retriever.search(query, top_k=2)
                all_evidence.extend(results)

            except Exception as error:
                 print(f"Retrieval failed for query: {query}")
                 print(error)

        return deduplicate_evidence(
            all_evidence,
            max_items=top_k
       )

    def analyze(self, strategic_question, top_k=5, mode="playbook"):
        evidence_items = self.retrieve_strategic_evidence(
            strategic_question,
            top_k=top_k
        )

        confidence = calculate_confidence(evidence_items)

        user_prompt = build_ceo_prompt(
            company_name=self.company_name,
            strategic_question=strategic_question,
            evidence_items=evidence_items
        )

        try:
            if mode == "fast":
               selected_prompt = FAST_CEO_SYSTEM_PROMPT
            else:
               selected_prompt = CEO_SYSTEM_PROMPT
            answer = generate_response(
                system_prompt=CEO_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                mode=mode
            )

            if is_incomplete_answer(answer):
               raise RuntimeError(
               "LLM response was incomplete. Using fallback playbook."
            )

            llm_status = "LLM generation successful"

        except Exception as error:
            answer = build_fallback_playbook(
                company_name=self.company_name,
                strategic_question=strategic_question,
                evidence_items=evidence_items,
                error_message=str(error)
            )

            llm_status = f"Fallback used because LLM failed: {error}"

        return {
            "company": self.company_name,
            "question": strategic_question,
            "retrieval_confidence": confidence,
            "answer": answer,
            "evidence": evidence_items,
            "llm_status": llm_status
        }

    def answer_followup(self, user_question, previous_briefing="", top_k=3, mode="chat"):
        evidence_items = self.retriever.search(
            user_question,
            top_k=top_k
        )

        user_prompt = build_chat_prompt(
            company_name=self.company_name,
            user_question=user_question,
            previous_briefing=previous_briefing,
            evidence_items=evidence_items
        )

        try:
            answer = generate_response(
                system_prompt=CHATBOT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                mode=mode
            )

            llm_status = "LLM follow-up generation successful"

        except Exception as error:
            answer = build_fallback_chat_answer(
                company_name=self.company_name,
                user_question=user_question,
                evidence_items=evidence_items,
                error_message=str(error)
            )

            llm_status = f"Fallback used because LLM failed: {error}"

        return {
            "question": user_question,
            "answer": answer,
            "evidence": evidence_items,
            "llm_status": llm_status
        }


if __name__ == "__main__":
    analyzer = StrategicAnalyzer(company_name="Microsoft")

    question = (
        "Based on the retrieved evidence, what AI strategy should Microsoft prioritize next?"
    )

    result = analyzer.analyze(
        strategic_question=question,
        top_k=4,
        mode="fast"
    )

    print("\n" + "=" * 120)
    print("AI CEO STRATEGIC BRIEFING")
    print("=" * 120)
    print(result["answer"])

    print("\n" + "=" * 120)
    print("RETRIEVAL CONFIDENCE:", result["retrieval_confidence"])
    print("LLM STATUS:", result["llm_status"])
    print("=" * 120)

    print("\nEVIDENCE USED")
    print("=" * 120)

    for item in result["evidence"]:
        print("\n" + "-" * 100)
        print("Title:", item.get("title"))
        print("Source:", item.get("source"))
        print("Source Type:", item.get("source_type"))
        print("Published:", item.get("published"))
        print("URL:", item.get("url"))
        print("Evidence Preview:")
        print(item.get("evidence", "")[:400])