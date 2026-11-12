import sys
from pathlib import Path

from app.infrastructure.database.property_repository import PropertyRepository
from app.services.research.providers.models import ResearchResult


def _decision_engine_path(module_path: Path = Path(__file__)) -> Path:
    """Locate the decision engine in repository and Docker layouts."""
    resolved_path = module_path.resolve()

    for parent_index in (2, 3):
        candidate = resolved_path.parents[parent_index] / "decision-engine"

        if candidate.is_dir():
            return candidate

    raise ModuleNotFoundError(
        "The decision-engine package is missing from the API runtime."
    )


decision_engine_path = _decision_engine_path()

if str(decision_engine_path) not in sys.path:
    sys.path.append(str(decision_engine_path))

from strategies.assignment_strategy import AssignmentStrategy  # noqa: E402


class DecisionService:
    @staticmethod
    def evaluate(
        property_id: str,
        research_result: ResearchResult | None = None,
    ):
        property_data = PropertyRepository.get(property_id)

        if not property_data:
            return None

        if research_result is not None:
            property_data = DecisionService._with_research(
                property_data,
                research_result,
            )

        return AssignmentStrategy().evaluate(property_data)

    @staticmethod
    def _with_research(
        property_data: dict,
        research_result: ResearchResult,
    ) -> dict:
        """Provides the strategy a single aggregate research input."""
        researched_data = {
            key: value
            for provider in research_result.providers
            if provider.status.value == "completed"
            for key, value in provider.data.items()
        }
        return {**property_data, **researched_data}
