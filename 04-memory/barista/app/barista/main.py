"""Barista agent wrapped for AgentCore, with two-tier memory.

STM: LangGraph checkpointer backed by AgentCore Memory (survives across a thread).
LTM: a user_preferences strategy distills each customer's "usual" from the
conversation, retrieved by actor and injected before the next chat — so a NEW
conversation still knows the returning customer's usual.
"""

import os
from datetime import datetime, timezone

import boto3
from bedrock_agentcore import BedrockAgentCoreApp

from barista_graph import build_graph

app = BedrockAgentCoreApp()

MEMORY_ID = os.getenv("MEMORY_BARISTA_MEM_ID") or os.getenv("BEDROCK_AGENTCORE_MEMORY_ID")
REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"

if MEMORY_ID:
    from langgraph_checkpoint_aws import AgentCoreMemorySaver
    checkpointer = AgentCoreMemorySaver(MEMORY_ID)
    memory_client = boto3.client("bedrock-agentcore", region_name=REGION)
else:
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()
    memory_client = None

graph = build_graph(checkpointer)


def load_usual(actor_id: str, query: str) -> str:
    """Fetch this customer's distilled preferences (their 'usual')."""
    if not memory_client:
        return ""
    try:
        r = memory_client.retrieve_memory_records(
            memoryId=MEMORY_ID,
            namespace=f"/customers/{actor_id}",
            searchCriteria={"searchQuery": query, "topK": 5},
        )
        return "\n".join(
            rec["content"]["text"]
            for rec in r.get("memoryRecordSummaries", [])
            if rec.get("content", {}).get("text")
        )
    except Exception:
        return ""


def log_exchange(actor_id: str, thread_id: str, prompt: str, reply: str) -> None:
    """Write the exchange as a conversational event for LTM extraction."""
    if not memory_client:
        return
    try:
        memory_client.create_event(
            memoryId=MEMORY_ID,
            actorId=actor_id,
            sessionId=f"{thread_id}-transcript",
            eventTimestamp=datetime.now(timezone.utc),
            payload=[
                {"conversational": {"role": "USER", "content": {"text": prompt}}},
                {"conversational": {"role": "ASSISTANT", "content": {"text": reply}}},
            ],
        )
    except Exception:
        pass


@app.entrypoint
def serve(payload, context):
    prompt = payload.get("prompt", "")
    # Identity: explicit payload wins; DEV_ACTOR_ID pins the customer for
    # inspector demos (its chat sends only a prompt); session id is last resort.
    actor_id = payload.get("user_id") or os.getenv("DEV_ACTOR_ID") or context.session_id or "guest"
    thread_id = payload.get("thread_id") or context.session_id or actor_id

    # Only the user message goes into state (the checkpointer persists this).
    # System prompt + the customer's "usual" are applied inside the node per call.
    usual = load_usual(actor_id, prompt)
    config = {"configurable": {"thread_id": thread_id, "actor_id": actor_id}}
    result = graph.invoke({"messages": [("user", prompt)], "usual": usual}, config)
    reply = result["messages"][-1].content
    log_exchange(actor_id, thread_id, prompt, reply)
    return reply


if __name__ == "__main__":
    app.run(port=int(os.environ.get("AGENT_PORT", "8080")))
