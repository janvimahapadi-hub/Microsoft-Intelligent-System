from retrieval.hybrid_retriever import HybridRetriever
from llm.ollama_client import generate_response
from llm.prompts import (
    FAST_CEO_SYSTEM_PROMPT,
    CEO_SYSTEM_PROMPT,
    build_ceo_prompt,
    CHATBOT_SYSTEM_PROMPT,
    build_chat_prompt
)


COMPETITOR_NAMES = [
    "aws",
    "amazon",
    "google",
    "google cloud",
    "openai",
    "nvidia",
    "anthropic"
]


def get_company_name(item):
    company = (
        item.get("company")
        or item.get("competitor")
        or item.get("source")
        or "Unknown"
    )

    source = item.get("source", "").lower()

    if company and company != "Unknown":
        return company

    if "aws" in source:
        return "AWS"
    if "google" in source:
        return "Google Cloud"
    if "openai" in source:
        return "OpenAI"
    if "nvidia" in source:
        return "NVIDIA"
    if "anthropic" in source:
        return "Anthropic"

    return "Microsoft"


def question_mentions_competitor(question):
    question_lower = question.lower()
    return any(name in question_lower for name in COMPETITOR_NAMES)


def build_strategic_queries(company_name, question):
    question_lower = question.lower()

    queries = [
        question,
        f"{company_name} AI strategy opportunities Azure Copilot Foundry",
        f"{company_name} AI risks security governance regulation competition",
        f"{company_name} partner ecosystem AI transformation enterprise customers",
        f"{company_name} developer platform GitHub AI productivity opportunity",
    ]

    if "cloud" in question_lower or "azure" in question_lower:
        queries.extend([
            f"{company_name} cloud opportunities Azure AI infrastructure enterprise cloud",
            f"{company_name} Azure AI infrastructure cloud security governance enterprise",
            "AWS cloud AI infrastructure enterprise generative AI security",
            "Google Cloud AI infrastructure enterprise Gemini cloud security",
        ])

    if "aws" in question_lower:
        queries.extend([
            "AWS cloud AI infrastructure enterprise generative AI security",
            "AWS machine learning cloud infrastructure Bedrock enterprise AI",
        ])

    if "google" in question_lower or "google cloud" in question_lower:
        queries.extend([
            "Google Cloud AI infrastructure enterprise Gemini cloud security",
            "Google Cloud enterprise AI agents Gemini infrastructure",
        ])

    if "openai" in question_lower:
        queries.extend([
            "OpenAI enterprise AI partner network Microsoft competition",
            "OpenAI model deployment enterprise AI risk partnership",
        ])

    if "nvidia" in question_lower:
        queries.extend([
            "NVIDIA AI infrastructure GPU enterprise cloud competition",
            "NVIDIA AI platform enterprise infrastructure opportunity",
        ])

    if "security" in question_lower or "cyber" in question_lower:
        queries.extend([
            f"{company_name} cybersecurity AI security Defender governance",
            "AWS security AI cloud security threat investigation",
            "Google Cloud security digital sovereignty cloud governance",
        ])

    return queries


def deduplicate_evidence(evidence_items, max_items=5):
    seen = set()
    unique_items = []

    for item in evidence_items:
        key = item.get("url") or item.get("title") or str(item.get("chunk_id"))

        if key in seen:
            continue

        seen.add(key)
        unique_items.append(item)

    unique_items = sorted(
        unique_items,
        key=lambda x: x.get("score", 999999)
    )

    return unique_items[:max_items]


def calculate_confidence(evidence_items):
    """
    Realistic retrieval confidence.

    Confidence should not become 1.00 just because five chunks were retrieved.
    It should consider evidence count, unique URLs, source diversity,
    and company diversity.
    """

    if not evidence_items:
        return 0.0

    sources = set()
    source_types = set()
    urls = set()
    companies = set()

    for item in evidence_items:
        if item.get("source"):
            sources.add(item.get("source"))

        if item.get("source_type"):
            source_types.add(item.get("source_type"))

        if item.get("url"):
            urls.add(item.get("url"))

        companies.add(get_company_name(item))

    evidence_count = len(evidence_items)
    source_count = len(sources)
    source_type_count = len(source_types)
    url_count = len(urls)
    company_count = len(companies)

    confidence = 0.0

    confidence += min(evidence_count / 5, 1.0) * 0.25
    confidence += min(source_count / 4, 1.0) * 0.25
    confidence += min(url_count / 5, 1.0) * 0.20
    confidence += min(company_count / 3, 1.0) * 0.20
    confidence += min(source_type_count / 2, 1.0) * 0.10

    if source_count < 3:
        confidence -= 0.10

    if company_count < 2:
        confidence -= 0.15

    if url_count < evidence_count:
        confidence -= 0.05

    confidence = max(min(confidence, 0.95), 0.0)

    return round(confidence, 2)


def build_fallback_playbook(company_name, strategic_question, evidence_items, error_message):
    evidence_titles = []

    for item in evidence_items:
        title = item.get("title", "Unknown title")
        source = item.get("source", "Unknown source")
        company = get_company_name(item)
        evidence_titles.append(f"- {title} ({source}, {company})")

    evidence_text = "\n".join(evidence_titles)

    return f"""
## 1. Executive diagnosis

The system retrieved evidence for the question: **{strategic_question}**.

The local LLM was too slow, unavailable, or returned an incomplete response, so this fallback playbook was created using retrieved evidence metadata. Treat this as structured decision support, not a final strategic decision.

## 2. Strategic meaning

The retrieved evidence indicates that {company_name} should evaluate this topic through business impact, execution feasibility, competitive positioning, and strategic risk. The key management challenge is to convert broad AI and cloud momentum into measurable initiatives with clear owners, KPIs, and risk controls.

## 3. Priority opportunities

1. **Scale enterprise AI infrastructure**
   - Focus on Azure AI, Microsoft Foundry, enterprise agents, and secure AI deployment.
   - KPI: production AI workloads, adoption rate, deployment speed.

2. **Strengthen ecosystem and partner-led adoption**
   - Use partners, developers, and enterprise channels to accelerate market reach.
   - KPI: partner-led pipeline, enterprise deployments, customer retention.

3. **Improve governance and security differentiation**
   - Make trust, security, compliance, and governance core differentiators.
   - KPI: secure deployment rate, governance coverage, incident reduction.

## 4. 90-day execution plan

### First 30 days
- Identify the top two evidence-backed opportunity themes.
- Assign owners from Azure, AI Platform, Security, Product Strategy, and Partner teams.
- Define measurable success criteria.

### Days 31-60
- Launch focused pilots for the highest-value cloud or AI opportunity.
- Validate technical feasibility, customer demand, cost impact, and security requirements.
- Compare Microsoft positioning against competitor evidence where available.

### Days 61-90
- Scale the strongest pilot.
- Publish KPI results.
- Decide whether to expand, refine, or stop the initiative.

## 5. Owners and KPIs

- **Owners:** Azure leadership, AI Platform, Microsoft Foundry, Security, Product Strategy, Sales, Partner Ecosystem.
- **KPIs:** Azure AI workload growth, Foundry adoption, customer pipeline impact, deployment speed, governance coverage, risk reduction.

## 6. Main risks and mitigations

- **Risk:** Evidence may be concentrated in limited sources.  
  **Mitigation:** Add more competitor, market, and customer evidence.

- **Risk:** Recommendations may be too broad.  
  **Mitigation:** Require every recommendation to include owner, KPI, timeline, and evidence.

- **Risk:** Local LLM may be slow during demo.  
  **Mitigation:** Use fast mode, cached retrieval, smaller model, and fallback output.

## 7. Evidence used

{evidence_text}

---

Fallback reason: {error_message}
"""


def build_fallback_chat_answer(company_name, user_question, evidence_items, error_message):
    evidence_titles = []

    for item in evidence_items:
        title = item.get("title", "Unknown title")
        source = item.get("source", "Unknown source")
        company = get_company_name(item)
        evidence_titles.append(f"- {title} ({source}, {company})")

    evidence_text = "\n".join(evidence_titles)

    return f"""
## Follow-up answer

The system retrieved evidence for the follow-up question: **{user_question}**.

The local LLM was too slow, unavailable, or returned an incomplete response. This fallback answer is based on retrieved evidence metadata.

### Practical next step

Use the retrieved evidence to create a focused execution plan with:

1. A clear business owner
2. A 30-60-90 day timeline
3. 2-3 measurable KPIs
4. Main risks and mitigations
5. Additional evidence needed before final decision

### Evidence retrieved

{evidence_text}

### Limitation

This fallback response does not include full LLM reasoning. To improve the answer, use a smaller local model, reduce top_k, or shorten evidence text.

Fallback reason: {error_message}
"""


def is_incomplete_answer(answer):
    if not answer or len(answer.strip()) < 120:
        return True

    required_keywords = [
        "Executive diagnosis",
        "Recommended CEO decision",
        "90-day",
        "KPI",
        "risk",
        "Evidence"
    ]

    answer_lower = answer.lower()
    found = 0

    for keyword in required_keywords:
        if keyword.lower() in answer_lower:
            found += 1

    return found < 3


def is_bad_evidence(item):
    title = item.get("title", "").lower()
    source = item.get("source", "").lower()
    evidence = item.get("evidence", "").lower()

    bad_terms = [
        "weekly employment",
        "employment q&a",
        "job search",
        "resume",
        "interview",
        "hiring",
        "study buddy",
        "open to work"
    ]

    if any(term in title or term in evidence for term in bad_terms):
        return True

    if "reddit" in source and any(term in title for term in bad_terms):
        return True

    return False


class StrategicAnalyzer:
    def __init__(self, company_name="Microsoft"):
        self.company_name = company_name
        self.retriever = HybridRetriever()

    def retrieve_strategic_evidence(self, strategic_question, top_k=5):
        all_evidence = []

        queries = build_strategic_queries(
            self.company_name,
            strategic_question
        )

        for query in queries:
            results = self.retriever.search(query, top_k=4)
            all_evidence.extend(results)

        clean_evidence = [
            item for item in all_evidence
            if not is_bad_evidence(item)
        ]

        selected_evidence = deduplicate_evidence(
            clean_evidence,
            max_items=top_k
        )

        return selected_evidence

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
            selected_prompt = (
                FAST_CEO_SYSTEM_PROMPT
                if mode == "fast"
                else CEO_SYSTEM_PROMPT
            )

            answer = generate_response(
                system_prompt=selected_prompt,
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
        followup_query = (
            user_question
            + " Microsoft AI strategy Azure Copilot Foundry partner ecosystem execution roadmap"
        )

        raw_evidence = self.retriever.search(
            followup_query,
            top_k=top_k * 4
        )

        evidence_items = [
            item for item in raw_evidence
            if not is_bad_evidence(item)
        ]

        evidence_items = deduplicate_evidence(
            evidence_items,
            max_items=top_k
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

            if not answer or len(answer.strip()) < 50:
                raise RuntimeError(
                    "LLM follow-up response was empty or incomplete."
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

    question = "What cloud opportunities should Microsoft prioritize?"

    result = analyzer.analyze(
        strategic_question=question,
        top_k=5,
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
        print("Company:", get_company_name(item))
        print("Source Type:", item.get("source_type"))
        print("Published:", item.get("published"))
        print("URL:", item.get("url"))
        print("Evidence Preview:")
        print(item.get("evidence", "")[:400])