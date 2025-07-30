# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["CriterionRetrieveMatchingProgressResponse", "SiteBreakdown"]


class SiteBreakdown(BaseModel):
    patients_matched: int = FieldInfo(alias="patientsMatched")

    site_id: int = FieldInfo(alias="siteId")

    site_name: str = FieldInfo(alias="siteName")

    total_patients: int = FieldInfo(alias="totalPatients")


class CriterionRetrieveMatchingProgressResponse(BaseModel):
    patients_matched: int = FieldInfo(alias="patientsMatched")

    total_patients: int = FieldInfo(alias="totalPatients")

    site_breakdown: Optional[List[SiteBreakdown]] = FieldInfo(alias="siteBreakdown", default=None)
