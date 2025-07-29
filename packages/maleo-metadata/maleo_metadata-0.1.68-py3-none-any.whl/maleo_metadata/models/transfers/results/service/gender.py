from __future__ import annotations
from pydantic import Field
from maleo_foundation.models.transfers.results.service.general import (
    BaseServiceGeneralResultsTransfers,
)
from maleo_metadata.models.transfers.general.gender import GenderTransfers


class MaleoMetadataGenderServiceResultsTransfers:
    class Fail(BaseServiceGeneralResultsTransfers.Fail):
        pass

    class NoData(BaseServiceGeneralResultsTransfers.NoData):
        pass

    class SingleData(BaseServiceGeneralResultsTransfers.SingleData):
        data: GenderTransfers = Field(..., description="Single gender data")

    class MultipleData(BaseServiceGeneralResultsTransfers.UnpaginatedMultipleData):
        data: list[GenderTransfers] = Field(..., description="Multiple genders data")
