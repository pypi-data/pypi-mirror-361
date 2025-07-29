import logging
from typing import Any, Optional, Union
from pydantic import Field, field_validator

from carestack.document_linking.encounter_dto.target_dto.diagnostic_report_imaging_dto import (
    DiagnosticReportImaging,
)
from carestack.document_linking.encounter_dto.target_dto.diagnostic_report_lab_dto import (
    DiagnosticReportLab,
)
from carestack.document_linking.encounter_dto.target_dto.document_reference_dto import (
    DocumentReference,
)
from carestack.document_linking.encounter_dto.target_dto.snomed_code_dto import (
    SnomedCode,
)


logger = logging.getLogger(__name__)


class DiagnosticReportRecordDTO(SnomedCode):
    """Represents a record of diagnostic reports."""

    reports: Optional[
        list[Union[DiagnosticReportLab, DiagnosticReportImaging, DocumentReference]]
    ] = Field(
        None,
        alias="reports",
    )

    # @field_validator("reports")
    # @classmethod
    # def _validate_reports(
    #     cls, v: Optional[list[dict[str, Any]]]
    # ) -> Optional[
    #     list[Union[DiagnosticReportLab, DiagnosticReportImaging, DocumentReference]]
    # ]:
    #     """
    #     Validates and transforms the reports list.
    #     """
    #     if v is None:
    #         return None

    #     transformed_reports: list[
    #         Union[DiagnosticReportLab, DiagnosticReportImaging, DocumentReference]
    #     ] = []
    #     for item in v:
    #         if not isinstance(item, dict):
    #             logger.warning(
    #                 "Invalid item type encountered in reports list: %s. Skipping this item.",
    #                 type(item),
    #             )
    #             continue
    #         if "imaging" in item:
    #             try:
    #                 transformed_reports.append(DiagnosticReportImaging(**item))
    #             except Exception as e:
    #                 logger.error(
    #                     "Error creating DiagnosticReportImaging object: %s. Data: %s",
    #                     e,
    #                     item,
    #                 )
    #         elif "observations" in item:
    #             try:
    #                 transformed_reports.append(DiagnosticReportLab(**item))
    #             except Exception as e:
    #                 logger.error(
    #                     "Error creating DiagnosticReportLab object: %s. Data: %s",
    #                     e,
    #                     item,
    #                 )
    #         elif "data" in item:
    #             try:
    #                 transformed_reports.append(DocumentReference(**item))
    #             except Exception as e:
    #                 logger.error(
    #                     "Error creating DocumentReference object: %s. Data: %s",
    #                     e,
    #                     item,
    #                 )
    #         else:
    #             # Handle cases where the item doesn't match any known type
    #             logger.warning(
    #                 "Unknown report type encountered: %s. Skipping this item.", item
    #             )

    #     return transformed_reports
