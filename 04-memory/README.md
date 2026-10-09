# Video 4 — Memory

**Barista Bot**: a plain LangGraph agent (`app/barista/barista_graph.py` — no
AgentCore in that file) wrapped for the Runtime (`main.py`), with two-tier memory:

- **Short-term (the tape)**: the LangGraph checkpointer backed by AgentCore
  Memory — `AgentCoreMemorySaver(MEMORY_ID)`, one line, no database.
- **Long-term (the notes)**: a `USER_PREFERENCE` strategy (declared in
  `agentcore/agentcore.json`) distills each customer's "usual" from the
  transcript your code writes with `create_event`. You write the transcript;
  AWS writes the memory.

```bash
agentcore deploy
agentcore invoke --user-id you "I'll have a large oat-milk latte, extra hot."
# wait 2–5 minutes — long-term extraction is a background process
agentcore invoke --user-id you "I'll have the usual."
```

Notes
- Memory belongs to a *person*: always pass `--user-id`. A new session with the
  same user id is how you see long-term memory work.
- Teardown: `aws cloudformation delete-stack --stack-name AgentCore-barista-default`
