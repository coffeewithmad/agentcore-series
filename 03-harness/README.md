# Video 3 — The Harness

A complete agent with **zero lines of agent code**: a JSON declaration
(`harness.json` — model, tools, memory) and a prompt (`system-prompt.md`).
AgentCore runs the reasoning loop, the browser sandbox, and the code
interpreter for you.

```bash
cd researchagent
agentcore dev        # deploys (a harness only exists in the cloud) + opens the inspector
# or: agentcore deploy && agentcore invoke "Research three open-weight models that run on a single GPU"
```

Notes
- `dev` for a harness = deploy + a local cockpit. There is no local run mode.
- Config edits (model, tools, prompt) need a redeploy — restart `dev` or run `deploy`.
- Teardown: `aws cloudformation delete-stack --stack-name AgentCore-researchagent-default`
