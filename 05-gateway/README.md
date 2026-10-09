# Video 5 — Gateway

Your API becomes an MCP tool; the platform holds the credentials.

- `lambda/order_lookup.py` — the backend (hardcoded orders; stands in for a real system).
  Create it as a Lambda named `orderhelper-order-lookup` in your account first.
- `orderhelper/agentcore/agentcore.json` — the Gateway + target registration
  (Lambda ARN + `order_tool_schema.json`, the tool contract the model reads).
- `orderhelper/app/order_helper/harness.json` — the agent: a gateway pointer and
  the built-in code interpreter. Note what's missing: no tool definitions, no
  credentials, no MCP client code.

```bash
cd orderhelper
agentcore deploy          # may need two deploys when building from scratch:
                          # the gateway must exist before the harness's gateway
                          # tool can resolve its ARN
agentcore invoke "What's the refund for order 123?"
python ../invoke_with_trace.py "Refund for order 456?"   # prints the TOOLS CALLED receipt
```

Replace the `YOUR_AWS_ACCOUNT_ID` ARNs (in `agentcore.json` and
`invoke_with_trace.py`) with your own after creating the Lambda and deploying.

Teardown: `aws cloudformation delete-stack --stack-name AgentCore-orderhelper-default`
(plus the hand-made Lambda and its role).
