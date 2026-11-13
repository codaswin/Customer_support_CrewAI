# Customer Support

A multi-agent system that answers customer questions from a company's own documents, falls back to the web when those documents don't cover the question, and records what was missing.

## Language

**Query**:
A single question a customer asks the system.
_Avoid_: Inquiry, ticket, request, message

**Knowledge Base**:
The company's own documents, indexed so Queries can be answered from them.
_Avoid_: Docs, corpus, vector DB

**Fallback**:
A Query the Knowledge Base cannot answer, sent to web search instead.
_Avoid_: Escalation, handoff

**Gap Log**:
The record of every Fallback Query with its timestamp, showing what the Knowledge Base is missing.
_Avoid_: Query log, unanswered log
