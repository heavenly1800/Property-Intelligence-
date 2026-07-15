from app.infrastructure.database.property_repository import PropertyRepository
from app.services.research.orchestrator import ResearchAggregator
from app.services.research.quality_service import ResearchQualityService
from app.services.research.providers.census_provider import CensusProvider
from app.services.research.providers.county_gis_provider import CountyGISProvider
from app.services.research.providers.fema_provider import FEMAProvider
from app.services.research.providers.tax_assessor_provider import TaxAssessorProvider
from app.services.research.providers.utilities_provider import UtilitiesProvider


class ResearchService:
    @staticmethod
    async def run(property_id: str):
        property_data = PropertyRepository.get(property_id)

        if not property_data:
            return None

        aggregator = ResearchAggregator(
            providers=[
                CensusProvider(),
                FEMAProvider(),
                CountyGISProvider(),
                TaxAssessorProvider(),
                UtilitiesProvider(),
            ]
        )

        result = await aggregator.execute(property_data)

        persisted_fields = {
            "latitude": "latitude",
            "longitude": "longitude",
            "county": "county",
            "census_tract": "census_tract",
            "block_group": "block_group",
            "flood_zone": "flood_zone",
            "flood_zone_subtype": "flood_zone_subtype",
            "special_flood_hazard_area": "special_flood_hazard_area",
            "flood_risk_level": "flood_risk_level",
            "source": "flood_source",
            "apn": "apn",
            "parcel_acres": "parcel_acres",
            "zoning": "zoning",
            "jurisdiction": "jurisdiction",
            "land_use": "land_use",
            "parcel_source": "parcel_source",
            "owner_name": "owner_name",
            "owner_mailing_address": "owner_mailing_address",
            "assessed_land_value": "assessed_land_value",
            "assessed_improvement_value": "assessed_improvement_value",
            "assessed_total_value": "assessed_total_value",
            "tax_year": "tax_year",
            "tax_status": "tax_status",
            "last_transfer_date": "last_transfer_date",
            "last_transfer_price": "last_transfer_price",
            "assessor_source": "assessor_source",
            "electric_provider": "electric_provider",
            "electric_service_evidence": "electric_service_evidence",
            "gas_provider": "gas_provider",
            "gas_service_evidence": "gas_service_evidence",
            "water_provider": "water_provider",
            "water_service_evidence": "water_service_evidence",
            "sewer_provider": "sewer_provider",
            "sewer_service_evidence": "sewer_service_evidence",
            "broadband_summary": "broadband_summary",
            "broadband_evidence": "broadband_evidence",
            "utilities_source": "utilities_source",
        }
        research_data = {
            persisted_fields[key]: value
            for provider in result.providers
            if provider.status.value == "completed"
            for key, value in provider.data.items()
            if (
                key in persisted_fields
                and value is not None
                and (not isinstance(value, str) or value.strip())
            )
        }

        if research_data:
            PropertyRepository.update(property_id, research_data)

        final_property_data = {**property_data, **research_data}
        quality_summary = ResearchQualityService.evaluate(final_property_data)
        PropertyRepository.update(property_id, quality_summary.model_dump())
        result.quality_summary = quality_summary

        return result
