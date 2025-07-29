from __future__ import annotations
from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_metadata.models.schemas.medical_role import MaleoMetadataMedicalRoleSchemas


class MedicalRoleMixin(
    MaleoMetadataMedicalRoleSchemas.Name,
    MaleoMetadataMedicalRoleSchemas.Key,
    MaleoMetadataMedicalRoleSchemas.Code,
    BaseGeneralSchemas.Order,
    MaleoMetadataMedicalRoleSchemas.OptionalParentId,
    BaseGeneralSchemas.DataMixin,
):
    pass


class MedicalRoleTransfers(MedicalRoleMixin):
    pass


# class StructuredMedicalRoleTransfers(MedicalRoleTransfers):
#     specializations:List["StructuredMedicalRoleTransfers"] = Field(..., description="Role specializations")

# # this is required for forward reference resolution
# StructuredMedicalRoleTransfers.model_rebuild()
