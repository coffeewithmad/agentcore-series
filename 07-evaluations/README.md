# Video 7 — Evaluations

Measure whether the agent did the right thing — against a gold dataset.

- `policyassistant/app/PolicyAssistant/main.py` — a Strands agent whose system
  prompt contains five fictional company policies. No tools, no retrieval.
- `policyassistant/dataset.json` — 10 scenarios with expected answers:
  5 straightforward, 2 exception-handling, 2 multi-policy, 1 deliberately
  unsupported (does the agent admit ignorance or invent policy?).
- `policyassistant/run_batch_eval.py` — the AgentCore SDK's
  `BatchEvaluationRunner`: invokes every scenario, waits for span ingestion
  (~3 min, deliberate), then the service judges the sessions with
  `Builtin.Correctness` + `Builtin.ResponseRelevance` and prints scores with
  the judges' written explanations.

```bash
cd policyassistant
agentcore deploy
# put your runtime ARN (from deploy output) into run_batch_eval.py, then:
uv run --project app/PolicyAssistant python run_batch_eval.py
```

Results also land in the AgentCore console: **Assess → Evaluations → Batch
evaluations** — per-session judge feedback, and a Compare view to watch scores
move across runs. That's the point: not the score, the *repeatable measurement*.

Teardown: `aws cloudformation delete-stack --stack-name AgentCore-policyassistant-default`
