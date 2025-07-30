from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_metadata.models.schemas.system_role import MaleoMetadataSystemRoleSchemas


class SystemRoleMixin(
    MaleoMetadataSystemRoleSchemas.Name,
    MaleoMetadataSystemRoleSchemas.Key,
    BaseGeneralSchemas.Order,
    BaseGeneralSchemas.DataMixin,
):
    pass


class SystemRoleTransfers(SystemRoleMixin):
    pass
