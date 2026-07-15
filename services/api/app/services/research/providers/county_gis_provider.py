from dataclasses import dataclass
from math import cos, radians, sqrt
from typing import Any

import httpx

from .base import ResearchProvider
from .models import ResearchProviderResult, ResearchProviderStatus


@dataclass(frozen=True)
class CountyParcelService:
    query_url: str
    source: str
    fields: str


class CountyGISProvider(ResearchProvider):
    NEARBY_PARCEL_TOLERANCE_METERS = 25
    SAN_BERNARDINO_SERVICE = CountyParcelService(
        query_url=(
            "https://services.arcgis.com/aA3snZwJfFkVyDuP/arcgis/rest/"
            "services/Parcels_for_San_Bernardino_County/FeatureServer/0/query"
        ),
        source="San Bernardino County Public Parcel Viewer",
        fields=(
            "ParcelNumber,Acreage,Zoning,ZoningDescription,"
            "Jurisdiction,AssessDescription"
        ),
    )
    SERVICES = {
        ("CA", "SAN BERNARDINO"): SAN_BERNARDINO_SERVICE,
    }

    async def execute(
        self, property_data: dict[str, Any]
    ) -> ResearchProviderResult:
        latitude = property_data.get("latitude")
        longitude = property_data.get("longitude")
        county = self._normalize_county(property_data.get("county"))
        state = self._normalize_state(property_data.get("state"))

        if latitude is None or longitude is None:
            return self._skipped("Property coordinates are unavailable.")

        if not county or not state:
            return self._skipped(
                "Property county and state are required for County GIS research."
            )

        service = self.SERVICES.get((state, county))

        if service is None:
            return self._skipped(
                f"County GIS is not yet supported for {county.title()} County, {state}."
            )

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                exact_payload = await self._query_parcels(
                    client,
                    service,
                    latitude,
                    longitude,
                )
                feature = self._first_feature(exact_payload)

                if feature is None:
                    nearby_payload = await self._query_parcels(
                        client,
                        service,
                        latitude,
                        longitude,
                        distance=self.NEARBY_PARCEL_TOLERANCE_METERS,
                    )
                    feature = self._nearest_feature(
                        nearby_payload,
                        latitude,
                        longitude,
                        self.NEARBY_PARCEL_TOLERANCE_METERS,
                    )

            attributes = (
                self._feature_attributes(feature)
                if feature is not None
                else None
            )
        except (
            httpx.HTTPError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
        ) as error:
            return ResearchProviderResult(
                provider="County GIS",
                status=ResearchProviderStatus.FAILED,
                message=f"County GIS request failed: {error}",
            )

        if attributes is None:
            return ResearchProviderResult(
                provider="County GIS",
                status=ResearchProviderStatus.FAILED,
                message=(
                    "No county parcel was found within "
                    f"{self.NEARBY_PARCEL_TOLERANCE_METERS} meters of these coordinates."
                ),
            )

        apn = self._value(attributes, "ParcelNumber")

        if apn is None:
            return ResearchProviderResult(
                provider="County GIS",
                status=ResearchProviderStatus.FAILED,
                message="County GIS returned a parcel without an APN.",
            )

        return ResearchProviderResult(
            provider="County GIS",
            status=ResearchProviderStatus.COMPLETED,
            confidence=1.0,
            data={
                "apn": apn,
                "parcel_acres": self._value(attributes, "Acreage"),
                "zoning": self._value(attributes, "Zoning"),
                "jurisdiction": self._value(attributes, "Jurisdiction"),
                "land_use": self._value(attributes, "AssessDescription"),
                "parcel_source": service.source,
            },
        )

    @staticmethod
    async def _query_parcels(
        client: httpx.AsyncClient,
        service: CountyParcelService,
        latitude: float,
        longitude: float,
        distance: int | None = None,
    ) -> Any:
        params = {
            "where": "1=1",
            "geometry": f"{longitude},{latitude}",
            "geometryType": "esriGeometryPoint",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": service.fields,
            "returnGeometry": "true" if distance is not None else "false",
            "outSR": "4326",
            "f": "json",
        }

        if distance is not None:
            params["distance"] = str(distance)
            params["units"] = "esriSRUnit_Meter"

        response = await client.get(service.query_url, params=params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _features(payload: Any) -> list[dict[str, Any]]:
        if not isinstance(payload, dict):
            raise ValueError("County GIS returned an invalid response payload.")

        if payload.get("error"):
            raise ValueError(
                payload["error"].get("message", "County GIS query failed.")
            )

        features = payload.get("features")

        if not isinstance(features, list):
            raise ValueError("County GIS returned invalid parcel features.")

        return [feature for feature in features if isinstance(feature, dict)]

    @classmethod
    def _first_feature(cls, payload: Any) -> dict[str, Any] | None:
        features = cls._features(payload)
        return features[0] if features else None

    @classmethod
    def _nearest_feature(
        cls,
        payload: Any,
        latitude: float,
        longitude: float,
        maximum_distance_meters: int,
    ) -> dict[str, Any] | None:
        closest: tuple[float, dict[str, Any]] | None = None

        for feature in cls._features(payload):
            attributes = cls._feature_attributes(feature)

            if not attributes or not cls._value(attributes, "ParcelNumber"):
                continue

            distance = cls._feature_distance_meters(
                feature,
                latitude,
                longitude,
            )

            if distance is None:
                continue

            if closest is None or distance < closest[0]:
                closest = (distance, feature)

        if closest is None or closest[0] > maximum_distance_meters:
            return None

        return closest[1]

    @staticmethod
    def _feature_attributes(feature: dict[str, Any]) -> dict[str, Any] | None:
        attributes = feature.get("attributes")

        if not isinstance(attributes, dict):
            raise ValueError("County GIS returned invalid parcel attributes.")

        return attributes

    @classmethod
    def _feature_distance_meters(
        cls,
        feature: dict[str, Any],
        latitude: float,
        longitude: float,
    ) -> float | None:
        geometry = feature.get("geometry")

        if not isinstance(geometry, dict):
            return None

        rings = geometry.get("rings")

        if not isinstance(rings, list):
            return None

        distances = [
            cls._ring_distance_meters(ring, latitude, longitude)
            for ring in rings
            if isinstance(ring, list)
        ]
        valid_distances = [distance for distance in distances if distance is not None]
        return min(valid_distances) if valid_distances else None

    @staticmethod
    def _ring_distance_meters(
        ring: list[Any],
        latitude: float,
        longitude: float,
    ) -> float | None:
        points = [
            point for point in ring
            if (
                isinstance(point, list)
                and len(point) >= 2
                and isinstance(point[0], (int, float))
                and isinstance(point[1], (int, float))
            )
        ]

        if len(points) < 2:
            return None

        if points[0] != points[-1]:
            points.append(points[0])

        longitude_scale = 111_320 * cos(radians(latitude))
        latitude_scale = 110_574
        distances = []

        for start, end in zip(points, points[1:]):
            start_x = (start[0] - longitude) * longitude_scale
            start_y = (start[1] - latitude) * latitude_scale
            end_x = (end[0] - longitude) * longitude_scale
            end_y = (end[1] - latitude) * latitude_scale
            segment_x = end_x - start_x
            segment_y = end_y - start_y
            segment_length_squared = segment_x ** 2 + segment_y ** 2

            if segment_length_squared == 0:
                distances.append(sqrt(start_x ** 2 + start_y ** 2))
                continue

            projection = max(
                0,
                min(
                    1,
                    -(start_x * segment_x + start_y * segment_y)
                    / segment_length_squared,
                ),
            )
            nearest_x = start_x + projection * segment_x
            nearest_y = start_y + projection * segment_y
            distances.append(sqrt(nearest_x ** 2 + nearest_y ** 2))

        return min(distances) if distances else None

    @staticmethod
    def _value(attributes: dict[str, Any], field: str) -> Any:
        value = attributes.get(field)
        return value.strip() if isinstance(value, str) else value

    @staticmethod
    def _normalize_county(value: Any) -> str | None:
        if not isinstance(value, str) or not value.strip():
            return None

        return value.upper().removesuffix(" COUNTY").strip()

    @staticmethod
    def _normalize_state(value: Any) -> str | None:
        if not isinstance(value, str):
            return None

        normalized = value.strip().upper()
        return "CA" if normalized in {"CA", "CALIFORNIA"} else normalized or None

    @staticmethod
    def _skipped(message: str) -> ResearchProviderResult:
        return ResearchProviderResult(
            provider="County GIS",
            status=ResearchProviderStatus.SKIPPED,
            message=message,
        )
