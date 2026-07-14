from __future__ import annotations

from .models import BuyerScore

# ---------------------------------------------------------------------
# Weight Configuration
# ---------------------------------------------------------------------

DISTANCE_WEIGHT = 0.25
COUNTY_WEIGHT = 0.20
PURCHASE_WEIGHT = 0.15
RECENCY_WEIGHT = 0.15
PROPERTY_TYPE_WEIGHT = 0.15
ACREAGE_WEIGHT = 0.10


def score_buyer(
    buyer: dict,
    property_data: dict,
) -> BuyerScore:
    """
    Calculates an overall Buyer Intelligence score.

    Initial implementation uses simple heuristics.

    Future versions will replace each helper with
    richer market intelligence without changing
    the public contract.
    """

    distance = score_distance(buyer, property_data)
    county = score_county(buyer, property_data)
    purchases = score_purchase_frequency(buyer)
    recency = score_recency(buyer)
    property_type = score_property_type(
        buyer,
        property_data,
    )
    acreage = score_acreage(
        buyer,
        property_data,
    )

    overall = (
        distance * DISTANCE_WEIGHT
        + county * COUNTY_WEIGHT
        + purchases * PURCHASE_WEIGHT
        + recency * RECENCY_WEIGHT
        + property_type * PROPERTY_TYPE_WEIGHT
        + acreage * ACREAGE_WEIGHT
    )

    return BuyerScore(
        overall_score=round(overall, 1),
        distance_score=distance,
        county_score=county,
        purchase_frequency_score=purchases,
        recency_score=recency,
        property_type_score=property_type,
        acreage_score=acreage,
    )


# ---------------------------------------------------------------------
# Individual Signals
# ---------------------------------------------------------------------


def score_distance(
    buyer: dict,
    property_data: dict,
) -> float:
    """
    Placeholder.

    Future:
    Distance between subject parcel
    and buyer purchase history.
    """
    return 75.0


def score_county(
    buyer: dict,
    property_data: dict,
) -> float:
    """
    Placeholder.

    Future:
    County purchasing preference.
    """
    return 80.0


def score_purchase_frequency(
    buyer: dict,
) -> float:
    purchases = buyer.get("purchase_count", 0)

    if purchases >= 25:
        return 100

    if purchases >= 10:
        return 85

    if purchases >= 5:
        return 70

    if purchases >= 1:
        return 55

    return 25


def score_recency(
    buyer: dict,
) -> float:
    """
    Placeholder.

    Future:
    Days since latest purchase.
    """
    return 80.0


def score_property_type(
    buyer: dict,
    property_data: dict,
) -> float:
    """
    Placeholder.

    Future:
    Compare purchased property types.
    """
    return 75.0


def score_acreage(
    buyer: dict,
    property_data: dict,
) -> float:
    """
    Placeholder.

    Future:
    Compare acreage preferences.
    """
    return 70.0