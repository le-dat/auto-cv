"""Validate node — validates extracted CV/JD data with Pydantic."""

from typing import Any

from app.models.schemas import CVData, JDData


class ValidateNode:
    """Node responsible for validating parsed CV and JD data."""

    def __init__(self):
        pass

    async def run(self, state: dict) -> dict[str, Any]:
        """Validate CV and JD data using Pydantic models."""
        errors: list[str] = []
        updates: dict[str, Any] = {}

        # Validate CV data if present
        if state.get("cv_data"):
            cv_data = state["cv_data"]
            if isinstance(cv_data, dict):
                try:
                    cv_data = CVData.model_validate(cv_data)
                    updates["cv_data"] = cv_data
                except Exception as e:
                    errors.append(f"CV validation error: {str(e)}")
            elif not isinstance(cv_data, CVData):
                errors.append("CV data is not a valid CVData instance")

        # Validate JD data if present
        if state.get("jd_data"):
            jd_data = state["jd_data"]
            if isinstance(jd_data, dict):
                try:
                    jd_data = JDData.model_validate(jd_data)
                    updates["jd_data"] = jd_data
                except Exception as e:
                    errors.append(f"JD validation error: {str(e)}")
            elif not isinstance(jd_data, JDData):
                errors.append("JD data is not a valid JDData instance")

        # Store validation errors if any
        if errors:
            updates["validation_errors"] = errors
            # Only fail completely if critical fields are missing
            if not state.get("cv_data") or not state.get("jd_data"):
                updates["error"] = "; ".join(errors)

        return updates


def create_validate_node():
    """Factory to create a validate node."""
    return ValidateNode()
