from enum import Enum
from pydantic import BaseModel


class ResearchStage(str, Enum):
    QUEUED = "Queued"
    ADDRESS = "Verifying Address"
    PARCEL = "Locating Parcel"
    OWNER = "Finding Owner"
    ZONING = "Analyzing Zoning"
    FLOOD = "Checking Flood Zone"
    UTILITIES = "Checking Utilities"
    COMPS = "Finding Comparable Sales"
    BUYERS = "Finding Buyers"
    AI = "Generating AI Summary"
    COMPLETE = "Complete"


class ResearchStatus(BaseModel):
    stage: ResearchStage
    progress: int
    message: str