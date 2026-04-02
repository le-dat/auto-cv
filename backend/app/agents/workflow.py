"""LangGraph workflow builder for CV optimization."""


from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, StateGraph

from app.agents.nodes import (
    context_node,
    format_node,
    match_node,
    parse_node,
    rewrite_node,
    validate_node,
)
from app.agents.state import WorkflowState


def build_workflow(llm: BaseChatModel) -> StateGraph:
    """Build and return the LangGraph workflow.

    Flow: parse → validate → context → match → rewrite → format → END
          ↓ (error)           ↓ (error)  ↓ (error)  ↓ (error)
         END                 END        END        END

    Args:
        llm: The chat model to use for LLM calls in nodes.
    """
    # Create node instances with the LLM
    parse = parse_node.create_parse_node(llm)
    validate = validate_node.create_validate_node()
    context = context_node.create_context_node(llm)
    match = match_node.create_match_node(llm)
    rewrite = rewrite_node.create_rewrite_node(llm)
    fmt = format_node.create_format_node()

    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("parse", parse.run)
    workflow.add_node("validate", validate.run)
    workflow.add_node("context", context.run)
    workflow.add_node("match", match.run)
    workflow.add_node("rewrite", rewrite.run)
    workflow.add_node("format", fmt.run)

    # Set entry point
    workflow.set_entry_point("parse")

    # Normal flow
    workflow.add_edge("parse", "validate")
    workflow.add_edge("validate", "context")
    workflow.add_edge("context", "match")
    workflow.add_edge("match", "rewrite")
    workflow.add_edge("rewrite", "format")
    workflow.add_edge("format", END)

    # Conditional edge from parse on error
    def parse_error(state: WorkflowState) -> str:
        if state.get("error"):
            return "end_parse"
        return "validate"

    workflow.add_conditional_edges(
        "parse",
        parse_error,
        {"end_parse": END, "validate": "validate"},
    )

    # Conditional edge from validate on error
    def validate_error(state: WorkflowState) -> str:
        if state.get("error") or state.get("validation_errors"):
            return "end_validate"
        return "context"

    workflow.add_conditional_edges(
        "validate",
        validate_error,
        {"end_validate": END, "context": "context"},
    )

    # Conditional edge from match on error
    def match_error(state: WorkflowState) -> str:
        if state.get("error"):
            return "end_match"
        return "rewrite"

    workflow.add_conditional_edges(
        "match",
        match_error,
        {"end_match": END, "rewrite": "rewrite"},
    )

    # Conditional edge from rewrite on error
    def rewrite_error(state: WorkflowState) -> str:
        if state.get("error"):
            return "end_rewrite"
        return "format"

    workflow.add_conditional_edges(
        "rewrite",
        rewrite_error,
        {"end_rewrite": END, "format": "format"},
    )

    return workflow


def compile_workflow(llm: BaseChatModel):
    """Build and compile the workflow for a given LLM."""
    return build_workflow(llm).compile()
