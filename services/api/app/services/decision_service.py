import sys
from pathlib import Path

from app.infrastructure.database.property_repository import PropertyRepository

# Add the decision-engine project to Python's import path
decision_engine_path = (
    Path(__file__).resolve().parents[3] / "decision-engine"
)

if str(decision_engine_path) not in sys.path:
    sys.path.append(str(decision_engine_path))

from strategies.assignment_strategy import AssignmentStrategy  # noqa: E402


class DecisionService:
    @staticmethod
    def evaluate(property_id: str):
        property_data = PropertyRepository.get(property_id)

        if not property_data:
            return None

        strategy = AssignmentStrategy()

        return strategy.evaluate(property_data)