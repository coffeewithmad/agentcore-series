"""A plain LangGraph barista agent — no AgentCore in this file.

The system prompt (and the returning customer's "usual") are applied at model-call
time inside the node, NOT stored in the message history. That keeps them out of the
checkpointer, so resuming a thread never accumulates duplicate system messages.
"""

from typing import Annotated, TypedDict

from langchain_core.messages import SystemMessage
from langchain_aws import ChatBedrock
from langchain_core.tools import tool
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
model = ChatBedrock(model_id=MODEL_ID, provider="anthropic")

SYSTEM = (
    "You are a friendly barista taking coffee orders. Keep replies short. "
    "When a customer states a drink, confirm it back warmly. If a customer asks "
    "for 'the usual' and you have been told their usual below, make it; if you have "
    "no record of their usual, cheerfully ask what they'd like."
)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    usual: str          # the returning customer's usual (per-request, not persisted as a message)


@tool
def make_drink(drink: str) -> str:
    """Ring up and prepare a drink order."""
    return f"Order in: {drink}. Ready at the bar shortly!"


model_with_tools = model.bind_tools([make_drink])


def barista(state: State):
    system_text = SYSTEM
    if state.get("usual"):
        system_text += f"\n\nThis returning customer's usual: {state['usual']}"
    # System prepended only for THIS model call — never written back to state.
    model_input = [SystemMessage(content=system_text)] + state["messages"]
    return {"messages": [model_with_tools.invoke(model_input)]}


def build_graph(checkpointer=None):
    g = StateGraph(State)
    g.add_node("barista", barista)
    g.add_node("tools", ToolNode([make_drink]))
    g.set_entry_point("barista")
    g.add_conditional_edges("barista", tools_condition)
    g.add_edge("tools", "barista")
    return g.compile(checkpointer=checkpointer)
