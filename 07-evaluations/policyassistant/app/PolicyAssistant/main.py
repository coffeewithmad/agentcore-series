"""Policy Assistant — answers employee questions from a fixed set of company
policies. No tools, no retrieval: the policies ARE the system prompt. Built as
the evaluation target for the AgentCore Evaluations chapter."""

from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from model.load import load_model

app = BedrockAgentCoreApp()
log = app.logger

POLICY_DOCUMENTS = """
== Vacation Policy ==
Employees receive 20 vacation days per year, accruing at 1.67 days per month.
Vacation may be used only after completing the 90-day probation period
(days still accrue during probation). A maximum of 5 unused days may be
carried over into the next calendar year.

== Sick Leave Policy ==
Employees receive 10 sick days per year. Sick days do not carry over.
A doctor's note is required for more than 3 consecutive sick days.

== Expense Policy ==
Receipts are required for all expenses over $50. Expenses of $50 or less do
not require a receipt, with one exception: lodging expenses always require a
receipt regardless of amount. Expense reports must be submitted within 30
days of the expense.

== Travel Policy ==
Manager pre-approval is required for any trip costing more than $500 and for
all international travel. Domestic trips of $500 or less do not require
pre-approval.

== Remote Work Policy ==
Employees may work remotely up to 3 days per week with their manager's
agreement. Fully remote arrangements require VP approval.
"""

SYSTEM_PROMPT = f"""You are the company Policy Assistant. Answer employee
questions using ONLY the policy documents below.

Rules:
- Answer completely: if a policy has conditions or exceptions relevant to the
  question, include them.
- If the question is not covered by these policies, say so plainly and direct
  the employee to HR. Never invent policy.
- Be concise and direct.

{POLICY_DOCUMENTS}"""

MODEL = load_model()


@app.entrypoint
def invoke(payload, context):
    prompt = payload.get("prompt", "")
    if not isinstance(prompt, str) or not prompt:
        return "Error: 'prompt' must be a non-empty string"
    # Fresh Agent per request: each question is independent — no conversation
    # state may bleed between evaluation scenarios on a warm instance.
    agent = Agent(model=MODEL, system_prompt=SYSTEM_PROMPT, tools=[])
    result = agent(prompt)
    return result.message["content"][0]["text"]


if __name__ == "__main__":
    app.run()
