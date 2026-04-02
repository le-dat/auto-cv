"""Format node — assembles final GenerateResult."""

from typing import Any

from app.core.exceptions import CVOptimizerError
from app.models.schemas import GenerateResult


class FormatNode:
    """Node responsible for assembling the final result."""

    def __init__(self):
        pass

    async def run(self, state: dict) -> dict[str, Any]:
        """Assemble final GenerateResult from all prior steps."""
        updates: dict[str, Any] = {}

        try:
            # Validate required fields
            if not state.get("rewritten_cv"):
                raise CVOptimizerError("Missing rewritten_cv in format step")

            # Build match report if not generated
            match_report = state.get("match_report")
            if not match_report and state.get("match_result"):
                match_report = self._format_match_report(state["match_result"])

            # Create final result
            result = GenerateResult(
                rewritten_cv=state["rewritten_cv"],
                match_report=match_report or "No match analysis available.",
                match_result=state.get("match_result"),
            )

            updates["result"] = result

        except Exception as e:
            updates["error"] = f"Format failed: {str(e)}"

        return updates

    def _format_match_report(self, match_result) -> str:
        """Format match result into a report string."""
        lines = [
            "# Match Analysis",
            "",
            f"**Score:** {match_result.skill_match_score:.0%}",
            "",
            "## Matched",
        ]
        matched = [f"- {s}" for s in match_result.matched_skills] if match_result.matched_skills else ["None"]
        lines.extend(matched)
        lines.extend(["", "## Missing"])
        missing = [f"- {s}" for s in match_result.missing_skills] if match_result.missing_skills else ["None"]
        lines.extend(missing)
        lines.extend(["", "## Suggestions"])
        suggestions = [f"- {s}" for s in match_result.suggestions] if match_result.suggestions else ["None"]
        lines.extend(suggestions)
        return "\n".join(lines)


def create_format_node():
    """Factory to create a format node."""
    return FormatNode()
