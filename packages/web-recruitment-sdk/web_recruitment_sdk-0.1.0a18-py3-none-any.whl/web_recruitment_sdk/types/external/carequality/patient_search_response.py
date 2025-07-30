# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["PatientSearchResponse"]


class PatientSearchResponse(BaseModel):
    patient_id: Optional[str] = FieldInfo(alias="patientId", default=None)
    """The patient ID"""

    detail: Optional[str] = None
    """The detail of the response"""
