# import json
# from typing import Any
# from unittest.mock import AsyncMock, patch

import pytest

from carestack.base.errors import EhrApiError

# from carestack.common.enums import (
#     Gender,
#     PatientEndpoints,
#     PatientIdTypeEnum,
#     ResourceType,
#     StatesAndUnionTerritories,
#     PatientTypeEnum,
# )
# from carestack.patient.patient_dto import (
#     CreateUpdatePatientResponse,
#     GetPatientResponse,
#     PatientDTO,
#     PatientFilterResponse,
#     UpdatePatientDTO,
# )
from carestack.patient.patient_service import Patient
from carestack.base.base_types import ClientConfig
from tests.config_test import client_config


@pytest.fixture
def mock_patient_service(client_config: ClientConfig) -> Patient:
    return Patient(client_config)


# --- get_all Tests ---
# @pytest.mark.asyncio
# async def test_get_all_patients_success(mock_patient_service: Patient) -> None:
#     """Test successful retrieval of all patients."""
#     service = mock_patient_service
#     mock_response_data = {
#         "type": "success",
#         "message": "Patients Fetched",
#         "request_resource": [],
#         "total_number_of_records": 0,
#         "next_page_link": None,
#     }
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         result: GetPatientResponse = await service.get_all()

#         mock_make_request.assert_called_once_with(
#             "GET", PatientEndpoints.GET_ALL_PATIENTS, params=None
#         )
#         assert result.message == "Patients Fetched"
#         assert result.type == "success"
#         assert result.request_resource == []
#         assert result.total_number_of_records == 0
#         assert result.next_page_link is None


# @pytest.mark.asyncio
# async def test_get_all_patients_with_next_page(mock_patient_service: Patient) -> None:
#     """Test successful retrieval of all patients with next page."""
#     service = mock_patient_service
#     mock_response_data = {
#         "type": "success",
#         "message": "Patients Fetched",
#         "request_resource": [],
#         "total_number_of_records": 0,
#         "next_page_link": "next_page_token",
#     }
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data

#         next_page_token = "next_page_token"
#         result: GetPatientResponse = await service.get_all(next_page=next_page_token)

#         mock_make_request.assert_called_once_with(
#             "GET",
#             PatientEndpoints.GET_ALL_PATIENTS,
#             params={"nextPage": next_page_token},
#         )
#         assert result.message == "Patients Fetched"
#         assert result.type == "success"
#         assert result.request_resource == []
#         assert result.total_number_of_records == 0
#         assert result.next_page_link == next_page_token


# @pytest.mark.asyncio
# async def test_get_all_patients_ehr_api_error(mock_patient_service: Patient) -> None:
#     """Test get_all_patients when get raises EhrApiError."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_all()

#         mock_make_request.assert_called_once_with(
#             "GET", PatientEndpoints.GET_ALL_PATIENTS, params=None
#         )
#         assert "API error" in str(exc_info.value)
#         assert exc_info.value.status_code == 400


# @pytest.mark.asyncio
# async def test_get_all_patients_general_exception(
#     mock_patient_service: Patient,
# ) -> None:
#     """Test get_all_patients when __make_request raises a general Exception."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = Exception("General error")

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_all()
#         mock_make_request.assert_called_once_with(
#             "GET", PatientEndpoints.GET_ALL_PATIENTS, params=None
#         )
#         assert (
#             "An unexpected error occurred while fetching all patients: General error"
#             in str(exc_info.value)
#         )
#         assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_all_patients_json_decode_error(
#     mock_patient_service: Patient,
# ) -> None:
#     """Test get_all_patients when __make_request raises a JSONDecodeError."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = json.JSONDecodeError(
#             "Failed to parse JSON response", "", 0
#         )

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_all()
#         mock_make_request.assert_called_once_with(
#             "GET", PatientEndpoints.GET_ALL_PATIENTS, params=None
#         )
#         assert "Failed to parse JSON response" in str(exc_info.value)
#         assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_all_patients_value_error(mock_patient_service: Patient) -> None:
#     """Test get_all_patients when __make_request raises a ValueError."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = ValueError("Value error")

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_all()
#         mock_make_request.assert_called_once_with(
#             "GET", PatientEndpoints.GET_ALL_PATIENTS, params=None
#         )
#         assert (
#             "An unexpected error occurred while fetching all patients: Value error"
#             in str(exc_info.value)
#         )
#         assert exc_info.value.status_code == 500


# # --- get_by_id Tests ---


# @pytest.mark.asyncio
# async def test_get_patient_by_id_success(mock_patient_service: Patient) -> None:
#     """Test successful retrieval of a patient by ID."""
#     service = mock_patient_service
#     mock_response_data = {
#         "type": "success",
#         "message": "Patient Found",
#         "request_resource": [],
#         "total_number_of_records": 1,
#         "next_page_link": None,
#     }
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         result = await service.get_by_id("123")

#         mock_make_request.assert_called_once_with(
#             "GET",
#             PatientEndpoints.GET_PATIENT_BY_ID.format(patient_id="123"),
#             params=None,
#         )
#         assert isinstance(result, GetPatientResponse)
#         assert result.message == "Patient Found"


@pytest.mark.asyncio
async def test_get_patient_by_id_empty_id(mock_patient_service: Patient) -> None:
    """Test get_patient_by_id with an empty ID."""
    service = mock_patient_service
    with pytest.raises(EhrApiError) as exc_info:
        await service.get_by_id("")
    assert "Patient ID cannot be null or empty." in str(exc_info.value)
    assert exc_info.value.status_code == 400


# @pytest.mark.asyncio
# async def test_get_patient_by_id_ehr_api_error(mock_patient_service: Patient) -> None:
#     """Test get_patient_by_id when get raises EhrApiError."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_by_id("123")
#         assert "API error" in str(exc_info.value)
#         assert exc_info.value.status_code == 400
#         mock_make_request.assert_called_once_with(
#             "GET",
#             PatientEndpoints.GET_PATIENT_BY_ID.format(patient_id="123"),
#             params=None,
#         )


# @pytest.mark.asyncio
# async def test_get_patient_by_id_general_exception(
#     mock_patient_service: Patient,
# ) -> None:
#     """Test get_patient_by_id when __make_request raises a general Exception."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = Exception("General error")

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_by_id("123")
#         mock_make_request.assert_called_once_with(
#             "GET",
#             PatientEndpoints.GET_PATIENT_BY_ID.format(patient_id="123"),
#             params=None,
#         )
#         assert "General error" in str(exc_info.value)
#         assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_patient_by_id_json_decode_error(
#     mock_patient_service: Patient,
# ) -> None:
#     """Test get_patient_by_id when __make_request raises a JSONDecodeError."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = json.JSONDecodeError(
#             "Failed to parse JSON response", "", 0
#         )

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_by_id("123")
#         mock_make_request.assert_called_once_with(
#             "GET",
#             PatientEndpoints.GET_PATIENT_BY_ID.format(patient_id="123"),
#             params=None,
#         )
#         assert "Failed to parse JSON response" in str(exc_info.value)
#         assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_patient_by_id_value_error(mock_patient_service: Patient) -> None:
#     """Test get_patient_by_id when __make_request raises a ValueError."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = ValueError("Value error")

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_by_id("123")
#         mock_make_request.assert_called_once_with(
#             "GET",
#             PatientEndpoints.GET_PATIENT_BY_ID.format(patient_id="123"),
#             params=None,
#         )
#         assert (
#             "An unexpected error occurred while fetching patient by Id: Value error"
#             in str(exc_info.value)
#         )  # updated assertion
#         assert exc_info.value.status_code == 500


# # --- exists Tests ---


# @pytest.mark.asyncio
# async def test_patient_exists_true(mock_patient_service: Patient) -> None:
#     """Test patient_exists returns True when patient is found."""
#     service = mock_patient_service
#     mock_response_data = {"message": "Patient Found !!!"}
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         result = await service.exists("123")
#         mock_make_request.assert_called_once_with(
#             "GET", PatientEndpoints.PATIENT_EXISTS.format(patient_id="123"), params=None
#         )
#         assert result is True


# @pytest.mark.asyncio
# async def test_patient_exists_false(mock_patient_service: Patient) -> None:
#     """Test patient_exists returns False when patient is not found."""
#     service = mock_patient_service
#     mock_response_data = {"message": "Patient Not Found"}
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         result = await service.exists("123")
#         mock_make_request.assert_called_once_with(
#             "GET", PatientEndpoints.PATIENT_EXISTS.format(patient_id="123"), params=None
#         )
#         assert result is False


# @pytest.mark.asyncio
# async def test_patient_exists_empty_id(mock_patient_service: Patient) -> None:
#     """Test patient_exists returns False when given an empty ID."""
#     service = mock_patient_service
#     result = await service.exists("")
#     assert result is False


# @pytest.mark.asyncio
# async def test_patient_exists_ehr_api_error(mock_patient_service: Patient) -> None:
#     """Test patient_exists returns False when get raises EhrApiError."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)
#         result = await service.exists("123")
#         mock_make_request.assert_called_once_with(
#             "GET", PatientEndpoints.PATIENT_EXISTS.format(patient_id="123"), params=None
#         )
#         assert result is False


# @pytest.mark.asyncio
# async def test_patient_exists_general_exception(mock_patient_service: Patient) -> None:
#     """Test patient_exists raise EhrApiError when __make_request raises a general Exception."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = Exception("General error")

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.exists("123")
#         assert (
#             "An unexpected error occurred while fetching patient by Id: General error"
#             in str(exc_info.value)
#         )
#         assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_patient_exists_json_decode_error(mock_patient_service: Patient) -> None:
#     """Test patient_exists when __make_request raises a JSONDecodeError."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = json.JSONDecodeError(
#             "Failed to parse JSON response", "", 0
#         )
#         with pytest.raises(EhrApiError) as exc_info:
#             await service.exists("123")
#         mock_make_request.assert_called_once_with(
#             "GET", PatientEndpoints.PATIENT_EXISTS.format(patient_id="123"), params=None
#         )
#         assert "Failed to parse JSON response" in str(exc_info.value)
#         assert exc_info.value.status_code == 500


# # --- create Tests ---


# @pytest.mark.asyncio
# async def test_create_patient_success(
#     mock_patient_service: Patient, valid_patient_data: dict[str, Any]
# ) -> None:
#     """Test successful creation of a patient."""
#     service = mock_patient_service
#     mock_response_data = {
#         "type": "success",
#         "message": "Patient Created",
#         "resourceId": "123",
#     }
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         patient_dto = PatientDTO(**valid_patient_data)
#         patient_data_with_alias = patient_dto.model_dump(by_alias=True)
#         result = await service.create(patient_data_with_alias)
#         mock_make_request.assert_called_once_with(
#             "POST", PatientEndpoints.CREATE_PATIENT, data=patient_data_with_alias
#         )
#         assert isinstance(result, CreateUpdatePatientResponse)
#         assert result.message == "Patient Created"
#         assert result.resource_id == "123"


# @pytest.mark.asyncio
# async def test_create_patient_ehr_api_error(
#     mock_patient_service: Patient, valid_patient_data: dict[str, Any]
# ) -> None:
#     """Test create_patient when make_post_request raises EhrApiError."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)

#         patient_dto = PatientDTO(**valid_patient_data)
#         patient_data_with_alias = patient_dto.model_dump(by_alias=True)

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.create(patient_data_with_alias)

#         assert "API error" in str(exc_info.value)
#         assert exc_info.value.status_code == 400
#         mock_make_request.assert_called_once_with(
#             "POST", PatientEndpoints.CREATE_PATIENT, data=patient_data_with_alias
#         )


# @pytest.mark.asyncio
# async def test_create_patient_general_exception(
#     mock_patient_service: Patient, valid_patient_data: dict[str, Any]
# ) -> None:
#     """Test create_patient when make_post_request raises a general Exception."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = Exception("General error")

#         patient_dto = PatientDTO(**valid_patient_data)
#         patient_data_with_alias = patient_dto.model_dump(by_alias=True)

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.create(patient_data_with_alias)
#         assert (
#             "An unexpected error occurred while creating patient: General error"
#             in str(exc_info.value)
#         )
#         assert exc_info.value.status_code == 500
#         mock_make_request.assert_called_once_with(
#             "POST", PatientEndpoints.CREATE_PATIENT, data=patient_data_with_alias
#         )


# @pytest.mark.asyncio
# async def test_create_patient_invalid_data(
#     mock_patient_service: Patient, valid_patient_data: dict[str, Any]
# ) -> None:
#     """Test create_patient with invalid data."""
#     service = mock_patient_service
#     invalid_patient_data = valid_patient_data.copy()
#     invalid_patient_data["first_name"] = "ab"
#     with pytest.raises(EhrApiError) as exc_info:
#         await service.create(invalid_patient_data)
#     assert "Patient data validation error." in str(exc_info.value)
#     assert exc_info.value.status_code == 400


# # --- update Tests ---


# @pytest.mark.asyncio
# async def test_update_patient_success(
#     mock_patient_service: Patient, valid_update_patient_data: dict[str, Any]
# ) -> None:
#     """Test successful update of a patient."""
#     service = mock_patient_service
#     mock_response_data = {
#         "type": "success",
#         "message": "Patient Updated",
#         "resourceId": "123",
#     }
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data

#         update_patient_dto = UpdatePatientDTO(**valid_update_patient_data)
#         update_patient_data_with_alias = update_patient_dto.model_dump(by_alias=True)

#         result = await service.update(update_patient_data_with_alias)
#         mock_make_request.assert_called_once_with(
#             "PUT", PatientEndpoints.UPDATE_PATIENT, data=update_patient_data_with_alias
#         )

#         assert isinstance(result, CreateUpdatePatientResponse)
#         assert result.message == "Patient Updated"
#         assert result.resource_id == "123"


# @pytest.mark.asyncio
# async def test_update_patient_ehr_api_error(
#     mock_patient_service: Patient, valid_update_patient_data: dict[str, Any]
# ) -> None:
#     """Test update_patient when make_put_request raises EhrApiError."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)

#         update_patient_dto = UpdatePatientDTO(**valid_update_patient_data)
#         update_patient_data_with_alias = update_patient_dto.model_dump(by_alias=True)

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.update(update_patient_data_with_alias)

#         assert "API error" in str(exc_info.value)
#         assert exc_info.value.status_code == 400
#         mock_make_request.assert_called_once_with(
#             "PUT", PatientEndpoints.UPDATE_PATIENT, data=update_patient_data_with_alias
#         )


# @pytest.mark.asyncio
# async def test_update_patient_general_exception(
#     mock_patient_service: Patient, valid_update_patient_data: dict[str, Any]
# ) -> None:
#     """Test update_patient when make_put_request raises a general Exception."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = Exception("General error")

#         update_patient_dto = UpdatePatientDTO(**valid_update_patient_data)
#         update_patient_data_with_alias = update_patient_dto.model_dump(by_alias=True)

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.update(update_patient_data_with_alias)
#         assert (
#             "An unexpected error occurred while updating patient: General error"
#             in str(exc_info.value)
#         )
#         assert exc_info.value.status_code == 500
#         mock_make_request.assert_called_once_with(
#             "PUT", PatientEndpoints.UPDATE_PATIENT, data=update_patient_data_with_alias
#         )


# @pytest.mark.asyncio
# async def test_update_patient_invalid_data(
#     mock_patient_service: Patient, valid_update_patient_data: dict[str, Any]
# ) -> None:
#     """Test update_patient with invalid data."""
#     service = mock_patient_service
#     invalid_patient_data = valid_update_patient_data.copy()
#     invalid_patient_data["mobile_number"] = "1234567890"
#     with pytest.raises(EhrApiError) as exc_info:
#         await service.update(invalid_patient_data)
#     assert "Patient data validation error." in str(exc_info.value)
#     assert exc_info.value.status_code == 400


# # --- delete Tests ---


# @pytest.mark.asyncio
# async def test_delete_patient_success(mock_patient_service: Patient) -> None:
#     """Test successful deletion of a patient."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = {}
#         await service.remove("123")
#         mock_make_request.assert_called_once_with(
#             "DELETE", PatientEndpoints.DELETE_PATIENT.format(patient_id="123")
#         )


# @pytest.mark.asyncio
# async def test_delete_patient_empty_id(mock_patient_service: Patient) -> None:
#     """Test delete_patient with an empty ID."""
#     service = mock_patient_service
#     with pytest.raises(EhrApiError) as exc_info:
#         await service.remove("")
#     assert "Patient ID cannot be null or empty." in str(exc_info.value)
#     assert exc_info.value.status_code == 400


# @pytest.mark.asyncio
# async def test_delete_patient_ehr_api_error(mock_patient_service: Patient) -> None:
#     """Test delete_patient when make_delete_request raises EhrApiError."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)
#         with pytest.raises(EhrApiError) as exc_info:
#             await service.remove("123")

#         assert "API error" in str(exc_info.value)
#         assert exc_info.value.status_code == 400
#         mock_make_request.assert_called_once_with(
#             "DELETE", PatientEndpoints.DELETE_PATIENT.format(patient_id="123")
#         )


# @pytest.mark.asyncio
# async def test_delete_patient_general_exception(mock_patient_service: Patient) -> None:
#     """Test delete_patient when make_delete_request raises a general Exception."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = Exception("General error")
#         with pytest.raises(EhrApiError) as exc_info:
#             await service.remove("123")
#         assert (
#             "An unexpected error occurred while deleting patient: General error"
#             in str(exc_info.value)
#         )
#         assert exc_info.value.status_code == 500
#         mock_make_request.assert_called_once_with(
#             "DELETE", PatientEndpoints.DELETE_PATIENT.format(patient_id="123")
#         )


# # --- get_by_filters Tests ---


# @pytest.mark.asyncio
# async def test_get_patient_by_filters_success(
#     mock_patient_service: Patient, valid_patient_filters: dict[str, Any]
# ) -> None:
#     """Test successful retrieval of patients by filters."""
#     service = mock_patient_service
#     mock_response_data = {"entry": [], "link": None, "total": 1}
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         result = await service.get_by_filters(valid_patient_filters)

#         mock_make_request.assert_called_once()
#         assert isinstance(result, PatientFilterResponse)
#         assert result.total == 1
#         assert result.entry == []


# @pytest.mark.asyncio
# async def test_get_patient_by_filters_ehr_api_error(
#     mock_patient_service: Patient, valid_patient_filters: dict[str, Any]
# ) -> None:
#     """Test get_patient_by_filters when make_get_request raises EhrApiError."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)
#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_by_filters(valid_patient_filters)

#         mock_make_request.assert_called_once()
#         assert "API error" in str(exc_info.value)
#         assert exc_info.value.status_code == 400


# @pytest.mark.asyncio
# async def test_get_patient_by_filters_general_exception(
#     mock_patient_service: Patient, valid_patient_filters: dict[str, Any]
# ) -> None:
#     """Test get_patient_by_filters when make_get_request raises a general Exception."""
#     service = mock_patient_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = Exception("General error")
#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_by_filters(valid_patient_filters)

#         mock_make_request.assert_called_once()
#         assert (
#             "An unexpected error occurred while fetching patients by filters: General error"
#             in str(exc_info.value)
#         )
#         assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_patient_by_filters_invalid_filters(
#     mock_patient_service: Patient,
# ) -> None:
#     """Test get_patient_by_filters when invalid filters are passed."""
#     service = mock_patient_service
#     invalid_filters = {"first_name": "ab"}
#     with pytest.raises(EhrApiError) as exc_info:
#         await service.get_by_filters(invalid_filters)
#     assert "An unexpected error occurred while fetching patients by filters" in str(
#         exc_info.value
#     )
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_patient_by_filters_with_next_page(
#     mock_patient_service: Patient, valid_patient_filters: dict[str, Any]
# ) -> None:
#     """Test successful retrieval of patients by filters with next page."""
#     service = mock_patient_service
#     mock_response_data = {
#         "entry": [],
#         "link": {"nextPage": "next_page_token"},
#         "total": 1,
#     }
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         next_page_token = "next_page_token"
#         result = await service.get_by_filters(
#             valid_patient_filters, next_page=next_page_token
#         )

#         mock_make_request.assert_called_once()
#         assert isinstance(result, PatientFilterResponse)
#         assert result.total == 1
#         assert result.entry == []
#         assert result.link is not None and result.link.next_page == next_page_token


# @pytest.fixture
# def valid_patient_data() -> dict[str, Any]:
#     return {
#         "id_number": "1234567890",
#         "id_type": PatientIdTypeEnum.AADHAAR.value,
#         "abha_address": "test@sbx",
#         "patient_type": PatientTypeEnum.NEW.value,
#         "first_name": "John",
#         "middle_name": "M",
#         "last_name": "Doe",
#         "birth_date": "1990-01-01",
#         "gender": Gender.MALE.value,
#         "mobile_number": "+919876543210",
#         "email_id": "john.doe@example.com",
#         "address": "123 Main St",
#         "pincode": "123456",
#         "state": StatesAndUnionTerritories.ANDHRA_PRADESH.value,
#         "wants_to_link_whatsapp": True,
#         "photo": "base64string",
#         "resource_type": ResourceType.PATIENT.value,
#         "resource_id": "123",
#     }


# @pytest.fixture
# def valid_update_patient_data() -> dict[str, Any]:
#     return {
#         "resource_id": "123",
#         "email_id": "updated.john.doe@example.com",
#         "mobile_number": "+919876543210",
#         "resource_type": ResourceType.PATIENT.value,
#     }


# @pytest.fixture
# def valid_patient_filters() -> dict[str, Any]:
#     return {
#         "first_name": "John",
#         "last_name": "Doe",
#         "birth_date": "1990-01-01",
#         "gender": Gender.MALE.value,
#         "phone": "+919876543210",
#         "state": StatesAndUnionTerritories.ANDHRA_PRADESH.value,
#         "organization": "TestOrg",
#         "count": 10,
#         "identifier": "1234567890",
#     }
