from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_metadata.models.schemas.gender import MaleoMetadataGenderSchemas


class GenderMixin(
    MaleoMetadataGenderSchemas.Name,
    MaleoMetadataGenderSchemas.Key,
    BaseGeneralSchemas.Order,
    BaseGeneralSchemas.DataMixin,
):
    pass


class GenderTransfers(GenderMixin):
    pass
