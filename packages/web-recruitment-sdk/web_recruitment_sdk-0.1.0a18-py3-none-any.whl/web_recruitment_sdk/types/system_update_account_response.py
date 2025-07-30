# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SystemUpdateAccountResponse"]


class SystemUpdateAccountResponse(BaseModel):
    id: int

    name: str

    tenant: str

    has_carequality_sites: Optional[bool] = FieldInfo(alias="hasCarequalitySites", default=None)
