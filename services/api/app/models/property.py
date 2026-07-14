from dataclasses import dataclass
from typing import Literal, Optional

WorkflowStage = Literal[
    "NEW_LEAD",
    "RESEARCH",
    "READY_TO_OFFER",
    "OFFER_SENT",
    "NEGOTIATING",
    "UNDER_CONTRACT",
    "MARKETING",
    "SOLD",
    "ARCHIVED",
]


@dataclass
class Property:
    property_id: str

    apn: Optional[str]

    address: str

    city: str

    county: str

    state: str

    zip_code: str

    property_type: str

    acres: Optional[float]

    square_feet: Optional[int]

    zoning: Optional[str]

    workflow_stage: Optional[WorkflowStage] = None