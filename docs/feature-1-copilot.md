# PatentIQ — Feature 1: AI Research Copilot Documentation
## NLP Query Understanding, Session Context, Grounded Reasoning, and Voice Interaction

---

## 1. Overview

The **PatentIQ AI Research Copilot** is a specialized conversational patent research assistant integrated into the PatentIQ enterprise platform. It enables engineers, patent attorneys, and R&D researchers to discover prior art, inspect concept coverage, explore technology whitespace, compare competing patent documents, and analyze invention differentiation using conversational natural language and voice interaction.

Unlike generic conversational chatbots, the PatentIQ Copilot is deeply wired into the existing PatentIQ retrieval, intelligence, and federated knowledge expansion pipeline (Phases 1 through 6B), enforcing deterministic prior-art grounding, strict anti-hallucination policies, and legal disclaimers.

---

## 2. Architecture

```
User (Text / Voice Input)
         |
  [Speech-to-Text] (Web Speech API)
         |
   User Message
         |
+-----------------------------------------------------------+
|               Copilot Intelligence Layer                  |
|                                                           |
| 1. Intent Classification (8 Canonical Intents)            |
| 2. Entity & Reference Resolver (Ordinals, IDs, Pronouns)  |
| 3. Session Context Manager (UUID-keyed Session State)     |
+-----------------------------------------------------------+
         |
         +--------------------------------------------------+
         |                                                  |
         v                                                  v
 [PRIOR_ART_SEARCH]                                 [Contextual Follow-Up]
         |                                                  |
 [Orchestrator: NL Retrieval]                        [Reference Resolution]
         |                                                  |
 +-----------------------+                          +-----------------------+
 | Local ChromaDB Store  |                          | Resolved Patent Text  |
 | EPO EPS Live Provider |                          | Grounded Synthesis    |
 | Result Fusion (6B)    |                          | Anti-Hallucination    |
 +-----------------------+                          +-----------------------+
         |                                                  |
         +------------------------+-------------------------+
                                  |
                                  v
                      Grounded Copilot Response
                                  |
                      +-----------+-----------+
                      |                       |
                 Chat Bubble          [Text-to-Speech]
              & Patent Cards        (Web SpeechSynthesis)
```

---

## 3. NLP & Intent Understanding Layer

The Copilot utilizes a lightweight intent classification taxonomy:

| Intent | Purpose | Trigger Examples |
|---|---|---|
| `PRIOR_ART_SEARCH` | Retrieve patents using natural language | *"Find patents related to AI forest fire detection using satellite images"* |
| `EXPLAIN` | Plain-language technical breakdown | *"Explain the closest patent in simple words"*, *"How does it work?"* |
| `COMPARE` | Side-by-side technical comparison | *"Compare the top two patents"*, *"What are the differences between them?"* |
| `SUMMARIZE` | Executive landscape synthesis | *"Summarize the patents you found"*, *"Give me an overview of results"* |
| `WHITESPACE` | Evaluate concept coverage gaps | *"What areas are not well covered?"*, *"What concepts are missing?"* |
| `IMPROVE_IDEA` | Technical differentiation avenues | *"How can I make my idea more differentiated?"*, *"How to avoid prior art?"* |
| `FOLLOW_UP` | Contextual follow-up question | *"Which one is closest?"*, *"Why?"*, *"Does it use CNN?"*, *"Is my idea different?"* |
| `REPORT` | Structured intelligence export | *"Generate a research report"*, *"Export report"* |

---

## 4. Conversation Context & Reference Resolution

The Copilot maintains an in-memory session store (`CopilotSession`) keyed by a session UUID.
- **Reference Resolution**:
  - Ordinal: "the second patent", "patent 1", "top 2" map to indices in `session.retrieved_patents`.
  - Relative: "closest", "most relevant", "best match" resolve to index 0 (top-ranked candidate).
  - Anaphora: "it", "that", "this patent" resolve to `session.selected_patent`.
  - Specific technical inquiry extraction: "Does it use CNN?" extracts `CNN` and validates against retrieved patent text.
- **Session Isolation**: Each session maintains its own query, concept set, retrieved candidates, and turn history.

---

## 5. Grounded Answering & Anti-Hallucination Policy

PatentIQ enforces strict anti-hallucination constraints:
1. **Never Guess Technical Details**:
   - If the user asks whether a patent uses a specific algorithm or technique and the retrieved document does not state it, the Copilot responds:
     > *"The retrieved patent information for [ID] does not provide enough evidence for me to confirm whether it uses [Technology]."*
2. **Never Fabricate Metadata**:
   - Patent numbers, publication dates, and applicants are strictly sourced from verified corpus records or EPO EPS XML.
3. **Novelty Disclaimer & Terminology**:
   - The Copilot exclusively uses `"AI-Estimated Novelty Indicator"` or `"AI Prior-Art Novelty Indicator"`.
   - Never states that an invention is "patentable" or "legally novel".
   - Every response includes the disclaimer:
     > *"This is an automated prior-art similarity indicator and is not a legal determination of patentability or novelty."*

---

## 6. Voice Interaction

- **Speech-to-Text (STT)**: Uses browser-native Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`). Zero third-party cloud bills, zero API key exposure. Real-time visual feedback: pulsating red indicator during listening, transcribing state, and fallback messages.
- **Text-to-Speech (TTS)**: Optional `🔊 Listen` button on Copilot messages using `window.speechSynthesis`.

---

## 7. API Reference

### `POST /api/copilot/chat`
**Request Payload**:
```json
{
  "message": "Find patents related to AI wildfire detection using satellite imagery",
  "session_id": "session_abc123",
  "source_mode": "hybrid",
  "top_k": 5
}
```

**Response Payload**:
```json
{
  "session_id": "session_abc123",
  "message": "I found 5 relevant patents matching your research query...",
  "intent": "PRIOR_ART_SEARCH",
  "query_understanding": {
    "technical_concepts": ["wildfire detection", "satellite imagery"]
  },
  "patents": [...],
  "selected_patent": {...},
  "research_context": {
    "current_query": "Find patents related to AI wildfire detection using satellite imagery",
    "intent": "PRIOR_ART_SEARCH",
    "patents_count": 5,
    "source_mode": "hybrid",
    "selected_patent_id": "IN201941048032"
  },
  "suggested_followups": [
    "Which one is closest to my idea?",
    "Explain the closest patent in simple words",
    "Compare the top 2 patents",
    "What areas are not well covered?"
  ],
  "disclaimer": "This is an automated prior-art similarity indicator and is not a legal determination of patentability or novelty."
}
```

---

## 8. Verification & Testing

The test suite in `backend/tests/test_feature1_copilot.py` covers 20 discrete scenarios:
1. Intent classification across all 8 intents
2. Query understanding and entity extraction
3. Prior art search federated retrieval flow
4. Plain-language patent explanation
5. Side-by-side comparative analysis
6. Grounded synthesis summarization
7. Semantic concept coverage & whitespace analysis
8. Research differentiation direction generation
9. Follow-up "Which one is closest?" resolution
10. Follow-up "Why?" explanation
11. Ordinal reference resolution
12. Empty and whitespace-only query handling
13. Zero-match resilience
14. VectorDB retrieval timeout fallback
15. Substantiated technical feature verification
16. Unsubstantiated technical feature rejection (anti-hallucination)
17. Novelty terminology & legal disclaimer protection
18. Source provenance preservation (`LOCAL`, `EPO_EPS`, `LOCAL + EPO`)
19. Multi-user session isolation
20. Pydantic request/response schema validation
