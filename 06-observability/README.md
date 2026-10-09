# Video 6 — Observability

No new agent — that's the point. Every example in this repo is traced
automatically: logs, OTel spans (every tool call, token counts, latency), and
metrics, with **zero instrumentation code**. The only artifact is the
`aws-opentelemetry-distro` line the CLI already put in each project's
requirements.

To see it:
1. One-time: enable **CloudWatch Transaction Search** (console → Application
   Signals → Transaction search).
2. Invoke any example agent.
3. CloudWatch console → **GenAI Observability → Bedrock AgentCore** →
   Agents View → your agent → Sessions → open a trace → the timeline.
4. Metrics live in the `AWS/Bedrock-AgentCore` and `bedrock-agentcore`
   namespaces — including token cost per trace and per-tool latency.

Gotchas worth knowing
- Agent lists in the dashboard are telemetry-derived: an idle agent outside the
  selected time window shows nothing. Invoke first, then look.
- The "All spans" table default-filters to spans with events (the conversation
  layer); open the trace timeline to see every span.
