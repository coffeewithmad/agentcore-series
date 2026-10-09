"""Invoke the order_helper harness and print the tool calls — the Gateway receipt.

The CLI's `agentcore invoke` prints only the final answer; the invoke_harness
stream also carries each tool round. The target___tool name (order-lookup___get_order)
is the proof the call went through the Gateway.

Usage:  python invoke_with_trace.py "Refund for order 123?"
"""

import sys
import uuid

import boto3

HARNESS_ARN = (
    "arn:aws:bedrock-agentcore:us-east-1:YOUR_AWS_ACCOUNT_ID:"
    "harness/orderhelper_order_helper-jJRv73B2y2"
)

prompt = sys.argv[1] if len(sys.argv) > 1 else "Refund for order 123?"

client = boto3.client("bedrock-agentcore", region_name="us-east-1")
result = client.invoke_harness(
    harnessArn=HARNESS_ARN,
    runtimeSessionId=str(uuid.uuid4()),
    messages=[{"role": "user", "content": [{"text": prompt}]}],
)

tools, text = [], []
for event in result["stream"]:
    if "contentBlockStart" in event:
        tool_use = event["contentBlockStart"].get("start", {}).get("toolUse")
        if tool_use:
            tools.append(tool_use.get("name"))
    if "contentBlockDelta" in event:
        delta = event["contentBlockDelta"].get("delta", {})
        if "text" in delta:
            text.append(delta["text"])

print(f"PROMPT: {prompt}\n")
print("TOOLS CALLED:")
for name in tools:
    print(f"  → {name}")
print()
print("".join(text))
