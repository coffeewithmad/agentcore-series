# AgentCore, One Piece at a Time

Working examples from the [**Coffee with MaD**](https://www.youtube.com/@CoffeewithMaD)
series on **Amazon Bedrock AgentCore** — one interesting idea at a time: one
video, one concept, one small working example.

> Your framework builds the agent. AgentCore runs it.

| # | Video | Concept | Example |
|---|-------|---------|---------|
| 1 | The Map | What AgentCore provides around an agent | *no code — by design* |
| 2 | The CLI | create → dev → deploy → invoke | *no code — the video is the commands* |
| 3 | The Harness | Define the agent; the platform runs the loop | [`03-harness/researchagent`](03-harness/) — zero-code agent: a JSON config + a prompt, with browser + code-interpreter tools |
| 4 | Memory | Let the agent remember across conversations | [`04-memory/barista`](04-memory/) — LangGraph agent with short-term (checkpointer) + long-term (strategy-distilled) memory |
| 5 | Gateway | Your APIs become MCP tools; the platform holds the keys | [`05-gateway/orderhelper`](05-gateway/) — Lambda behind a Gateway + built-in code interpreter |
| 6 | Observability | See what the agent did | [`06-observability`](06-observability/) — no new agent: the series' own traces, on by default |
| 7 | Evaluations | Measure whether it did it well | [`07-evaluations/policyassistant`](07-evaluations/) — gold dataset + batch evaluation with built-in judges |

The [`diagrams/`](diagrams/) folder holds the visual references used across the series.

## Prerequisites (once)

- An AWS account with **Bedrock model access** enabled for the Anthropic models
  (the examples use Claude Haiku 4.5 / Sonnet 4.5 via `us.` inference profiles —
  first use of a model your account hasn't enabled fails at *invoke* time, not deploy time)
- **Node.js 20+** and the AgentCore CLI: `npm install -g @aws/agentcore`
- **Python 3.10+** and [`uv`](https://docs.astral.sh/uv/)
- AWS credentials configured (`aws configure`)
- For videos 6–7: enable **CloudWatch Transaction Search** (one-time, per account —
  CloudWatch console → Application Signals → Transaction search; 1% span indexing is free)

## Using an example

Each folder is a self-contained AgentCore project:

```bash
cd 0X-topic/project
agentcore deploy     # creates a CloudFormation stack in YOUR account
agentcore invoke "hello"
```

Where a script contains an ARN with `YOUR_AWS_ACCOUNT_ID`, replace it with the
ARN printed by `agentcore deploy` (or `agentcore status`).

## ⚠️ Costs and teardown

These examples create real AWS resources (runtimes, memories, gateways, a Lambda)
and every invocation calls a real model. Idle costs are small but not zero.
When you're done with an example:

```bash
aws cloudformation delete-stack --stack-name AgentCore-<project>-default
```

## License

MIT — see [LICENSE](LICENSE).
