from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_metadata.models.schemas.user_type import MaleoMetadataUserTypeSchemas


class UserTypeMixin(
    MaleoMetadataUserTypeSchemas.Name,
    MaleoMetadataUserTypeSchemas.Key,
    BaseGeneralSchemas.Order,
    BaseGeneralSchemas.DataMixin,
):
    pass


class UserTypeTransfers(UserTypeMixin):
    pass
