from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_metadata.models.schemas.blood_type import MaleoMetadataBloodTypeSchemas


class BloodTypeMixin(
    MaleoMetadataBloodTypeSchemas.Name,
    MaleoMetadataBloodTypeSchemas.Key,
    BaseGeneralSchemas.Order,
    BaseGeneralSchemas.DataMixin,
):
    pass


class BloodTypeTransfers(BloodTypeMixin):
    pass
