from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReportSection:
    """
    Generic report section.

    Every section of the Property Intelligence Report
    is represented consistently.
    """

    completed: bool = False

    confidence: int = 0

    data: dict[str, Any] = field(
        default_factory=dict
    )

    evidence: list[str] = field(
        default_factory=list
    )


@dataclass
class PropertyIntelligenceReport:
    """
    The master intelligence object produced by
    Property Intelligence.

    Every engine contributes to this report.

    The UI consumes this report.

    AI consumes this report.

    PDF generation consumes this report.
    """

    identity: ReportSection = field(
        default_factory=ReportSection
    )

    ownership: ReportSection = field(
        default_factory=ReportSection
    )

    parcel: ReportSection = field(
        default_factory=ReportSection
    )

    market: ReportSection = field(
        default_factory=ReportSection
    )

    physical: ReportSection = field(
        default_factory=ReportSection
    )

    demographics: ReportSection = field(
        default_factory=ReportSection
    )

    infrastructure: ReportSection = field(
        default_factory=ReportSection
    )

    legal: ReportSection = field(
        default_factory=ReportSection
    )

    acquisition: ReportSection = field(
        default_factory=ReportSection
    )

    workflow: ReportSection = field(
        default_factory=ReportSection
    )