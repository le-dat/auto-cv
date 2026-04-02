"""Rewrite node — rewrites CV optimized for the job description."""

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.models.schemas import MatchResult

REWRITE_PROMPT = """You are a professional CV writer. Rewrite the provided CV to be optimized for the job description.

IMPORTANT RULES:
- NEVER fabricate experience, skills, or achievements not in the original CV
- Only highlight and emphasize existing skills and experience that match the JD
- Reorder bullet points to prioritize most relevant achievements first
- Use ATS-friendly keywords from the job description naturally
- Maintain the CV in the same format (markdown)
- Keep all information truthful and accurate

CV:
{cv_text}

Job Description:
{jd_text}

Match Analysis:
{match_analysis}

Context (optional knowledge):
{context}

Return ONLY the rewritten CV text in markdown format.
"""


class RewriteNode:
    """Node responsible for rewriting the CV to match the JD."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def run(self, state: dict) -> dict[str, Any]:
        """Rewrite CV optimized for the job description."""
        updates: dict[str, Any] = {}
        cv_data = state.get("cv_data")
        jd_data = state.get("jd_data")
        match_result = state.get("match_result")
        context_chunks = state.get("context_chunks") or []

        if not cv_data or not jd_data:
            updates["error"] = "Cannot rewrite: missing CV or JD data"
            return updates

        try:
            # Build CV text from structured data
            cv_text = self._build_cv_text(cv_data)

            # Perform rewrite
            rewritten_cv = await self._rewrite_cv(
                cv_text=cv_text,
                jd_text=jd_data.description or str(jd_data),
                match_analysis=self._format_match(match_result),
                context="\n\n".join(context_chunks[:3]),  # Limit context
            )
            updates["rewritten_cv"] = rewritten_cv

            # Generate match report
            match_report = await self._generate_match_report(match_result)
            updates["match_report"] = match_report

        except Exception as e:
            updates["error"] = f"Rewrite failed: {str(e)}"

        return updates

    def _build_cv_text(self, cv_data) -> str:
        """Build plain text CV from structured data."""
        lines = []

        if cv_data.name:
            lines.append(f"# {cv_data.name}")
        if cv_data.email:
            lines.append(f"Email: {cv_data.email}")
        if cv_data.phone:
            lines.append(f"Phone: {cv_data.phone}")
        if cv_data.location:
            lines.append(f"Location: {cv_data.location}")
        if cv_data.summary:
            lines.append(f"\n## Summary\n{cv_data.summary}")

        if cv_data.skills:
            lines.append(f"\n## Skills\n{', '.join(cv_data.skills)}")

        if cv_data.experience:
            lines.append("\n## Experience")
            for exp in cv_data.experience:
                lines.append(f"\n### {exp.title} at {exp.company}")
                if exp.start_date:
                    end = exp.end_date or "Present"
                    lines.append(f"{exp.start_date} - {end}")
                if exp.description:
                    lines.append(exp.description)

        if cv_data.education:
            lines.append("\n## Education")
            for edu in cv_data.education:
                lines.append(f"\n### {edu.degree} in {edu.field_of_study}")
                lines.append(f"{edu.institution}")
                if edu.graduation_date:
                    lines.append(f"Graduated: {edu.graduation_date}")

        return "\n".join(lines)

    def _format_match(self, match_result: MatchResult | None) -> str:
        """Format match result for prompt."""
        if not match_result:
            return "No match analysis available."

        lines = [
            f"Match Score: {match_result.skill_match_score:.0%}",
            f"Matched Skills: {', '.join(match_result.matched_skills) or 'None'}",
            f"Missing Skills: {', '.join(match_result.missing_skills) or 'None'}",
            f"Weak Skills: {', '.join(match_result.weak_skills) or 'None'}",
        ]
        if match_result.suggestions:
            lines.append("Suggestions:")
            lines.extend(f"- {s}" for s in match_result.suggestions)
        return "\n".join(lines)

    async def _rewrite_cv(
        self,
        cv_text: str,
        jd_text: str,
        match_analysis: str,
        context: str,
    ) -> str:
        """Call LLM to rewrite CV."""
        prompt = REWRITE_PROMPT.format(
            cv_text=cv_text,
            jd_text=jd_text,
            match_analysis=match_analysis,
            context=context,
        )

        messages = [
            SystemMessage(content="You are a professional CV writer."),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        return content.strip()

    async def _generate_match_report(self, match_result: MatchResult | None) -> str:
        """Generate a human-readable match report."""
        if not match_result:
            return "No match analysis available."

        lines = [
            "# Match Analysis Report",
            "",
            "## Overall Match Score",
            f"{match_result.skill_match_score:.0%}",
            "",
            "## Matched Skills",
        ]
        if match_result.matched_skills:
            lines.extend(f"- {s}" for s in match_result.matched_skills)
        else:
            lines.append("No matching skills found.")

        lines.extend(["", "## Missing Skills (Gaps)"])
        if match_result.missing_skills:
            lines.extend(f"- {s}" for s in match_result.missing_skills)
        else:
            lines.append("No missing skills.")

        if match_result.suggestions:
            lines.extend(["", "## Suggestions for Improvement"])
            lines.extend(f"- {s}" for s in match_result.suggestions)

        return "\n".join(lines)


def create_rewrite_node(llm: BaseChatModel):
    """Factory to create a rewrite node with the given LLM."""
    return RewriteNode(llm)
