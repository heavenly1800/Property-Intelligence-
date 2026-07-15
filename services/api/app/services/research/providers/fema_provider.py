from typing import Any

import httpx

from .base import ResearchProvider
from .models import ResearchProviderResult, ResearchProviderStatus


class FEMAProvider(ResearchProvider):
    NFHL_SERVICE_URL = (
        "https://hazards.fema.gov/arcgis/rest/services/"
        "public/NFHL/MapServer"
    )
    FLOOD_HAZARD_LAYER_NAME = "Flood Hazard Zones"
    SOURCE = "FEMA National Flood Hazard Layer (NFHL)"

    async def execute(self, property_data: dict[str, Any]) -> ResearchProviderResult:
        latitude = property_data.get("latitude")
        longitude = property_data.get("longitude")

        if latitude is None or longitude is None:
            return ResearchProviderResult(
                provider="FEMA",
                status=ResearchProviderStatus.SKIPPED,
                message="Property coordinates are unavailable.",
            )

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                metadata_response = await client.get(
                    self.NFHL_SERVICE_URL,
                    params={"f": "json"},
                )
                metadata_response.raise_for_status()
                layer_id = self._flood_hazard_layer_id(
                    metadata_response.json()
                )

                response = await client.get(
                    f"{self.NFHL_SERVICE_URL}/{layer_id}/query",
                    params={
                        "where": "1=1",
                        "geometry": f"{longitude},{latitude}",
                        "geometryType": "esriGeometryPoint",
                        "inSR": "4326",
                        "spatialRel": "esriSpatialRelIntersects",
                        "outFields": "FLD_ZONE,ZONE_SUBTY,SFHA_TF",
                        "returnGeometry": "false",
                        "f": "json",
                    },
                )

            response.raise_for_status()
            payload = response.json()

            if not isinstance(payload, dict):
                raise ValueError("FEMA returned an invalid response payload.")

            if payload.get("error"):
                raise ValueError(payload["error"].get("message", "FEMA query failed."))

            features = payload.get("features", [])

            if not isinstance(features, list) or not features:
                return ResearchProviderResult(
                    provider="FEMA",
                    status=ResearchProviderStatus.FAILED,
                    message="No FEMA NFHL flood hazard zone was found for these coordinates.",
                )

            feature = features[0]

            if not isinstance(feature, dict):
                raise ValueError("FEMA returned an invalid flood feature.")

            attributes = feature.get("attributes", {})

            if not isinstance(attributes, dict):
                raise ValueError("FEMA returned invalid flood attributes.")
            flood_zone = attributes.get("FLD_ZONE")

            if not flood_zone:
                return ResearchProviderResult(
                    provider="FEMA",
                    status=ResearchProviderStatus.FAILED,
                    message="FEMA returned a flood feature without a flood zone.",
                )

            sfha = str(attributes.get("SFHA_TF", "")).upper() in {"T", "TRUE", "Y", "YES"}

            return ResearchProviderResult(
                provider="FEMA",
                status=ResearchProviderStatus.COMPLETED,
                confidence=1.0,
                data={
                    "flood_zone": flood_zone,
                    "flood_zone_subtype": attributes.get("ZONE_SUBTY"),
                    "special_flood_hazard_area": sfha,
                    "flood_risk_level": self._risk_level(flood_zone, sfha),
                    "source": self.SOURCE,
                },
            )
        except (
            httpx.HTTPError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
        ) as error:
            return ResearchProviderResult(
                provider="FEMA",
                status=ResearchProviderStatus.FAILED,
                message=f"FEMA NFHL request failed: {error}",
            )

    @staticmethod
    def _flood_hazard_layer_id(metadata: Any) -> int:
        if not isinstance(metadata, dict):
            raise ValueError("FEMA returned invalid NFHL service metadata.")

        layers = metadata.get("layers")

        if not isinstance(layers, list):
            raise ValueError("FEMA NFHL metadata does not include layers.")

        for layer in layers:
            if (
                isinstance(layer, dict)
                and layer.get("name") == FEMAProvider.FLOOD_HAZARD_LAYER_NAME
                and layer.get("geometryType") == "esriGeometryPolygon"
                and isinstance(layer.get("id"), int)
            ):
                return layer["id"]

        raise ValueError("FEMA NFHL Flood Hazard Zones layer is unavailable.")

    @staticmethod
    def _risk_level(flood_zone: str, sfha: bool) -> str:
        zone = flood_zone.upper()

        if sfha or zone.startswith(("A", "V")):
            return "high"

        if zone == "D":
            return "undetermined"

        if zone == "X":
            return "moderate" if sfha else "low"

        return "moderate"
