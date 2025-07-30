from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_metadata.models.schemas.organization_type import (
    MaleoMetadataOrganizationTypeSchemas,
)


class OrganizationTypeMixin(
    MaleoMetadataOrganizationTypeSchemas.Name,
    MaleoMetadataOrganizationTypeSchemas.Key,
    BaseGeneralSchemas.Order,
    BaseGeneralSchemas.DataMixin,
):
    pass


class OrganizationTypeTransfers(OrganizationTypeMixin):
    pass
