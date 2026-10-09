"""Batch-evaluate the Policy Assistant against the gold dataset.

Invokes every scenario in dataset.json against the deployed runtime, lets the
service collect the spans from CloudWatch, and runs Builtin.Correctness +
Builtin.ResponseRelevance over them. Prints aggregate scores, then per-turn
scores with judge explanations.
"""

import json
import sys
import uuid

import boto3
from bedrock_agentcore.evaluation import (
    AgentInvokerInput,
    AgentInvokerOutput,
    BatchEvaluationRunConfig,
    BatchEvaluationRunner,
    BatchEvaluatorConfig,
    CloudWatchDataSourceConfig,
    FileDatasetProvider,
)

REGION = "us-east-1"
RUNTIME_ARN = (
    "arn:aws:bedrock-agentcore:us-east-1:YOUR_AWS_ACCOUNT_ID:"
    "runtime/policyassistant_PolicyAssistant-fe3RdtAVXY"
)
SERVICE_NAME = "policyassistant_PolicyAssistant.DEFAULT"
LOG_GROUP = "/aws/bedrock-agentcore/runtimes/policyassistant_PolicyAssistant-fe3RdtAVXY-DEFAULT"

client = boto3.client("bedrock-agentcore", region_name=REGION)


def agent_invoker(inp: AgentInvokerInput) -> AgentInvokerOutput:
    prompt = inp.payload if isinstance(inp.payload, str) else inp.payload.get("content", str(inp.payload))
    resp = client.invoke_agent_runtime(
        agentRuntimeArn=RUNTIME_ARN,
        runtimeSessionId=inp.session_id,
        payload=json.dumps({"prompt": prompt}),
        qualifier="DEFAULT",
    )
    body = resp["response"].read()
    try:
        out = json.loads(body)
    except Exception:
        out = body.decode()
    return AgentInvokerOutput(agent_output=out)


dataset = FileDatasetProvider("dataset.json").get_dataset()
runner = BatchEvaluationRunner(region=REGION)

config = BatchEvaluationRunConfig(
    batch_evaluation_name=(
        sys.argv[1] if len(sys.argv) > 1
        else f"policy_assistant_gold_{uuid.uuid4().hex[:8]}"
    ),
    description="Policy Assistant vs 10-question gold dataset",
    evaluator_config=BatchEvaluatorConfig(
        evaluator_ids=["Builtin.Correctness", "Builtin.ResponseRelevance"]
    ),
    data_source=CloudWatchDataSourceConfig(
        service_names=[SERVICE_NAME],
        log_group_names=[LOG_GROUP],
    ),
)

print(f"Running {len(dataset.scenarios)} scenarios...", flush=True)
result = runner.run_dataset_evaluation(config, dataset, agent_invoker)
m = result.model_dump()

print("\n=== AGGREGATE ===", flush=True)
print(json.dumps(m, indent=2, default=str))


def _find(d, key):
    if isinstance(d, dict):
        for k, v in d.items():
            if k == key:
                return v
            got = _find(v, key)
            if got is not None:
                return got
    elif isinstance(d, list):
        for v in d:
            got = _find(v, key)
            if got is not None:
                return got
    return None


print("\n=== PER-TURN SCORES (judge explanations) ===", flush=True)
lg = _find(m, "log_group_name") or _find(m, "logGroupName")
ls = _find(m, "log_stream_name") or _find(m, "logStreamName")
if lg and ls:
    logs = boto3.client("logs", region_name=REGION)
    evs = logs.get_log_events(logGroupName=lg, logStreamName=ls, startFromHead=True, limit=50)
    for e in evs["events"]:
        a = json.loads(e["message"]).get("attributes", {})
        sid = str(a.get("session.id", "?")).rsplit("-", 5)[0]
        print(f"{sid:32s} {a.get('gen_ai.evaluation.name','?'):28s} "
              f"{a.get('gen_ai.evaluation.score.value','?')}  "
              f"{str(a.get('gen_ai.evaluation.explanation',''))[:160]}")
else:
    print("(results log location not found in result object — see CloudWatch "
          "log group /aws/bedrock-agentcore/evaluations/batch-evaluations/results/default)")
