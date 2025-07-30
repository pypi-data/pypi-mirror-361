from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_metadata.models.schemas.service import MaleoMetadataServiceSchemas


class ServiceMixin(
    MaleoMetadataServiceSchemas.Name,
    MaleoMetadataServiceSchemas.Key,
    MaleoMetadataServiceSchemas.Category,
    MaleoMetadataServiceSchemas.Type,
    BaseGeneralSchemas.Order,
    BaseGeneralSchemas.DataMixin,
):
    pass


class ServiceTransfers(ServiceMixin):
    pass
