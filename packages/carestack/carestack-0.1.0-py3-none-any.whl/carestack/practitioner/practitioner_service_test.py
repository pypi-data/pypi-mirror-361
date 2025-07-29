# import pytest
# from unittest.mock import AsyncMock, patch
# from carestack.base.base_types import ClientConfig
# from carestack.common.enums import (
#     ResourceType,
#     Gender,
#     Departments,
#     PractitionerEndPoints,
# )
# from carestack.practitioner.practitioner_service import Practitioner
# from carestack.practitioner.practitioner_dto import (
#     CreateUpdatePractitionerResponse,
#     GetPractitionerResponse,
#     PractitionerFilterResponse,
#     CreatePractitionerDTO,
#     UpdatePractitionerDTO,
# )
# from carestack.base.errors import EhrApiError
# from tests.config_test import client_config
# from typing import Any


# @pytest.fixture
# def mock_practitioner_service(client_config: ClientConfig) -> Practitioner:
#     return Practitioner(client_config)


# @pytest.fixture
# def valid_practitioner_data() -> dict[str, Any]:
#     return {
#         "registration_id": "REG123",
#         "department": Departments.CARDIOLOGY.value,
#         "designation": "Doctor",
#         "status": "Active",
#         "joining_date": "2023-01-01",
#         "staff_type": "Permanent",
#         "first_name": "John",
#         "middle_name": "M",
#         "last_name": "Doe",
#         "birth_date": "1990-01-01",
#         "gender": Gender.MALE.value,
#         "mobile_number": "+919876543210",
#         "email_id": "john.doe@example.com",
#         "address": "123 Main St",
#         "pincode": "123456",
#         "state": "Andhra Pradesh",
#         "wants_to_link_whatsapp": True,
#         "photo": "base64string",
#         "resource_type": ResourceType.PRACTITIONER.value,
#         "resource_id": "123",
#     }


# @pytest.fixture
# def valid_update_practitioner_data() -> dict[str, Any]:
#     return {
#         "registration_id": "REG123",
#         "department": Departments.CARDIOLOGY.value,
#         "designation": "Doctor",
#         "status": "Active",
#         "joining_date": "2023-01-01",
#         "staff_type": "Permanent",
#         "first_name": "John",
#         "middle_name": "M",
#         "last_name": "Doe",
#         "birth_date": "1990-01-01",
#         "gender": Gender.MALE.value,
#         "mobile_number": "+919876543210",
#         "email_id": "updated.john.doe@example.com",
#         "address": "123 Main St",
#         "pincode": "123456",
#         "state": "Andhra Pradesh",
#         "wants_to_link_whatsapp": True,
#         "photo": "base64string",
#         "resource_type": ResourceType.PRACTITIONER.value,
#         "resource_id": "123",
#     }


# @pytest.fixture
# def valid_practitioner_filters() -> dict[str, Any]:
#     return {
#         "first_name": "John",
#         "last_name": "Doe",
#         "birth_date": "1990-01-01",
#         "gender": Gender.MALE.value,
#         "mobile_number": "+919876543210",
#         "state": "Andhra Pradesh",
#         "count": 10,
#     }


# # --- get_all Tests ---


# @pytest.mark.asyncio
# async def test_get_all_practitioners_success(
#     mock_practitioner_service: Practitioner,
# ) -> None:
#     """Test successful retrieval of all practitioners."""
#     service = mock_practitioner_service
#     mock_response_data = {
#         "type": "success",
#         "message": "Practitioners Fetched",
#         "request_resource": [],
#         "total_number_of_records": 0,
#         "next_page_link": None,
#     }
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         result: GetPractitionerResponse = await service.get_all()

#         mock_make_request.assert_called_once_with(
#             "GET", f"/get/{ResourceType.PRACTITIONER.value}", params=None
#         )
#         assert isinstance(result, GetPractitionerResponse)
#         assert result.message == "Practitioners Fetched"
#         assert result.type == "success"
#         assert result.request_resource == []
#         assert result.total_number_of_records == 0
#         assert result.next_page_link is None


# @pytest.mark.asyncio
# async def test_get_all_practitioners_with_next_page(
#     mock_practitioner_service: Practitioner,
# ) -> None:
#     """Test successful retrieval of all practitioners with next page."""
#     service = mock_practitioner_service
#     mock_response_data = {
#         "type": "success",
#         "message": "Practitioners Fetched",
#         "request_resource": [],
#         "total_number_of_records": 0,
#         "next_page_link": "next_page_token",
#     }
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data

#         next_page_token = "next_page_token"
#         result: GetPractitionerResponse = await service.get_all(
#             next_page=next_page_token
#         )

#         mock_make_request.assert_called_once_with(
#             "GET",
#             f"/get/{ResourceType.PRACTITIONER.value}",
#             params={"nextPage": next_page_token},
#         )
#         assert isinstance(result, GetPractitionerResponse)
#         assert result.message == "Practitioners Fetched"
#         assert result.type == "success"
#         assert result.request_resource == []
#         assert result.total_number_of_records == 0
#         assert result.next_page_link == next_page_token


# @pytest.mark.asyncio
# async def test_get_all_practitioners_ehr_api_error(
#     mock_practitioner_service: Practitioner,
# ) -> None:
#     """Test get_all_practitioners when get raises EhrApiError."""
#     service = mock_practitioner_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_all()

#         mock_make_request.assert_called_once_with(
#             "GET", f"/get/{ResourceType.PRACTITIONER.value}", params=None
#         )
#         assert "API error" in str(exc_info.value)


# # --- get_by_id Tests ---


# @pytest.mark.asyncio
# async def test_get_practitioner_by_id_success(
#     mock_practitioner_service: Practitioner,
# ) -> None:
#     """Test successful retrieval of a practitioner by ID."""
#     service = mock_practitioner_service
#     mock_response_data = {
#         "type": "success",
#         "message": "Practitioner Found",
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
#             "GET", f"/get/{ResourceType.PRACTITIONER.value}/123", params=None
#         )
#         assert isinstance(result, GetPractitionerResponse)
#         assert result.message == "Practitioner Found"


# @pytest.mark.asyncio
# async def test_get_practitioner_by_id_empty_id(
#     mock_practitioner_service: Practitioner,
# ) -> None:
#     """Test get_practitioner_by_id with an empty ID."""
#     service = mock_practitioner_service
#     with pytest.raises(EhrApiError) as exc_info:
#         await service.get_by_id("")
#     assert "Practitioner ID cannot be null or empty." in str(exc_info.value)
#     assert exc_info.value.status_code == 400


# @pytest.mark.asyncio
# async def test_get_practitioner_by_id_ehr_api_error(
#     mock_practitioner_service: Practitioner,
# ) -> None:
#     """Test get_practitioner_by_id when get raises EhrApiError."""
#     service = mock_practitioner_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 500)

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_by_id("123")
#         assert "API error" in str(exc_info.value)
#         mock_make_request.assert_called_once_with(
#             "GET", f"/get/{ResourceType.PRACTITIONER.value}/123", params=None
#         )
#         assert exc_info.value.status_code == 500


# # --- exists Tests ---


# @pytest.mark.asyncio
# async def test_practitioner_exists_true(
#     mock_practitioner_service: Practitioner,
# ) -> None:
#     """Test practitioner_exists returns True when practitioner is found."""
#     service = mock_practitioner_service
#     mock_response_data = {"message": "Practitioner Found !!!", "status": "success"}
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         result = await service.exists("123")
#         mock_make_request.assert_called_once_with(
#             "GET", f"/get/{ResourceType.PRACTITIONER.value}/123", params=None
#         )
#         assert result is True


# @pytest.mark.asyncio
# async def test_practitioner_exists_false(
#     mock_practitioner_service: Practitioner,
# ) -> None:
#     """Test practitioner_exists returns False when practitioner is not found."""
#     service = mock_practitioner_service
#     mock_response_data = {"message": "Practitioner Not Found", "status": "failed"}
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         result = await service.exists("123")
#         mock_make_request.assert_called_once_with(
#             "GET", f"/get/{ResourceType.PRACTITIONER.value}/123", params=None
#         )
#         assert result is False


# @pytest.mark.asyncio
# async def test_practitioner_exists_empty_id(
#     mock_practitioner_service: Practitioner,
# ) -> None:
#     """Test practitioner_exists returns False when given an empty ID."""
#     service = mock_practitioner_service
#     result = await service.exists("")
#     assert result is False


# @pytest.mark.asyncio
# async def test_practitioner_exists_ehr_api_error(
#     mock_practitioner_service: Practitioner,
# ) -> None:
#     """Test practitioner_exists returns False when get raises EhrApiError."""
#     service = mock_practitioner_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)
#         result = await service.exists("123")
#         mock_make_request.assert_called_once_with(
#             "GET", f"/get/{ResourceType.PRACTITIONER.value}/123", params=None
#         )
#         assert result is False


# # --- create Tests ---


# @pytest.mark.asyncio
# async def test_create_practitioner_success(
#     mock_practitioner_service: Practitioner, valid_practitioner_data: dict[str, Any]
# ) -> None:
#     """Test successful creation of a practitioner."""
#     service = mock_practitioner_service
#     mock_response_data = {
#         "type": "success",
#         "message": "Practitioner Created",
#         "resourceId": "123",
#     }
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data

#         practitioner_dto = CreatePractitionerDTO(**valid_practitioner_data)
#         practitioner_data_with_alias = practitioner_dto.model_dump(by_alias=True)

#         result = await service.create(practitioner_data_with_alias)

#         mock_make_request.assert_called_once_with(
#             "POST",
#             PractitionerEndPoints.CREATE_PRACTITIONER,
#             data=practitioner_data_with_alias,
#         )
#         assert isinstance(result, CreateUpdatePractitionerResponse)
#         assert result.message == "Practitioner Created"
#         assert result.resource_id == "123"


# @pytest.mark.asyncio
# async def test_create_practitioner_ehr_api_error(
#     mock_practitioner_service: Practitioner, valid_practitioner_data: dict[str, Any]
# ) -> None:
#     """Test create_practitioner when make_post_request raises EhrApiError."""
#     service = mock_practitioner_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)

#         practitioner_dto = CreatePractitionerDTO(**valid_practitioner_data)
#         practitioner_data_with_alias = practitioner_dto.model_dump(by_alias=True)

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.create(practitioner_data_with_alias)

#         assert "API error" in str(exc_info.value)
#         mock_make_request.assert_called_once_with(
#             "POST",
#             PractitionerEndPoints.CREATE_PRACTITIONER,
#             data=practitioner_data_with_alias,
#         )


# @pytest.mark.asyncio
# async def test_create_practitioner_already_exists(
#     mock_practitioner_service: Practitioner, valid_practitioner_data: dict[str, Any]
# ) -> None:
#     """Test create_practitioner when make_post_request raises EhrApiError with 409 status code."""
#     service = mock_practitioner_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("Practitioner already exists", 409)

#         practitioner_dto = CreatePractitionerDTO(**valid_practitioner_data)
#         practitioner_data_with_alias = practitioner_dto.model_dump(by_alias=True)

#         with pytest.raises(EhrApiError) as exc_info:
#             await service.create(practitioner_data_with_alias)

#         assert (
#             "Practitioner already exists. Consider updating the existing record instead."
#             in str(exc_info.value)
#         )
#         mock_make_request.assert_called_once_with(
#             "POST",
#             PractitionerEndPoints.CREATE_PRACTITIONER,
#             data=practitioner_data_with_alias,
#         )


# # --- update Tests ---


# @pytest.mark.asyncio
# async def test_update_practitioner_success(
#     mock_practitioner_service: Practitioner,
#     valid_update_practitioner_data: dict[str, Any],
# ) -> None:
#     """Test successful update of a practitioner."""
#     service = mock_practitioner_service
#     mock_response_data = {
#         "type": "success",
#         "message": "Practitioner Updated",
#         "resourceId": "123",
#     }
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         practitioner_dto = UpdatePractitionerDTO(**valid_update_practitioner_data)
#         practitioner_data_with_alias = practitioner_dto.model_dump(by_alias=True)
#         result = await service.update(practitioner_data_with_alias)
#         mock_make_request.assert_called_once_with(
#             "PUT",
#             PractitionerEndPoints.UPDATE_PRACTITIONER,
#             data=practitioner_data_with_alias,
#         )
#         assert isinstance(result, CreateUpdatePractitionerResponse)
#         assert result.message == "Practitioner Updated"
#         assert result.resource_id == "123"


# @pytest.mark.asyncio
# async def test_update_practitioner_ehr_api_error(
#     mock_practitioner_service: Practitioner,
#     valid_update_practitioner_data: dict[str, Any],
# ) -> None:
#     """Test update_practitioner when make_put_request raises EhrApiError."""
#     service = mock_practitioner_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)
#         practitioner_dto = UpdatePractitionerDTO(**valid_update_practitioner_data)
#         practitioner_data_with_alias = practitioner_dto.model_dump(by_alias=True)
#         with pytest.raises(EhrApiError) as exc_info:
#             await service.update(practitioner_data_with_alias)

#         assert "API error" in str(exc_info.value)
#         mock_make_request.assert_called_once_with(
#             "PUT",
#             PractitionerEndPoints.UPDATE_PRACTITIONER,
#             data=practitioner_data_with_alias,
#         )


# @pytest.mark.asyncio
# async def test_update_practitioner_invalid_data(
#     mock_practitioner_service: Practitioner,
#     valid_update_practitioner_data: dict[str, Any],
# ) -> None:
#     """Test update_practitioner with invalid data."""
#     service = mock_practitioner_service
#     invalid_practitioner_data = valid_update_practitioner_data.copy()
#     invalid_practitioner_data["mobile_number"] = "1234567890"
#     with pytest.raises(EhrApiError) as exc_info:
#         await service.update(invalid_practitioner_data)
#     assert "Validation error in PractitionerService." in str(exc_info.value)
#     assert exc_info.value.status_code == 400


# # --- get_by_filters Tests ---


# @pytest.mark.asyncio
# async def test_get_practitioner_by_filters_success(
#     mock_practitioner_service: Practitioner, valid_practitioner_filters: dict[str, Any]
# ) -> None:
#     """Test successful retrieval of practitioners by filters."""
#     service = mock_practitioner_service
#     mock_response_data = {"entry": [], "link": None, "total": 1}
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         result = await service.get_by_filters(valid_practitioner_filters)

#         mock_make_request.assert_called_once()
#         assert isinstance(result, PractitionerFilterResponse)
#         assert result.total == 1
#         assert result.entry == []


# @pytest.mark.asyncio
# async def test_get_practitioner_by_filters_ehr_api_error(
#     mock_practitioner_service: Practitioner, valid_practitioner_filters: dict[str, Any]
# ) -> None:
#     """Test get_practitioner_by_filters when make_get_request raises EhrApiError."""
#     service = mock_practitioner_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)
#         with pytest.raises(EhrApiError) as exc_info:
#             await service.get_by_filters(valid_practitioner_filters)

#         mock_make_request.assert_called_once()
#         assert "API error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_practitioner_by_filters_with_next_page(
#     mock_practitioner_service: Practitioner, valid_practitioner_filters: dict[str, Any]
# ) -> None:
#     """Test successful retrieval of practitioners by filters with next page."""
#     service = mock_practitioner_service
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
#             valid_practitioner_filters, next_page=next_page_token
#         )

#         mock_make_request.assert_called_once()
#         assert isinstance(result, PractitionerFilterResponse)
#         assert result.total == 1
#         assert result.entry == []
#         assert result.link is not None and result.link.next_page == next_page_token


# # --- delete Tests ---


# @pytest.mark.asyncio
# async def test_delete_practitioner_success(
#     mock_practitioner_service: Practitioner,
# ) -> None:
#     """Test successful deletion of a practitioner."""
#     service = mock_practitioner_service
#     mock_response_data = {
#         "status": "success",
#         "message": "Deleted Practitioner with ID 123 Successfully",
#     }
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.return_value = mock_response_data
#         await service.delete("123")
#         mock_make_request.assert_called_once_with(
#             "DELETE", f"/health-lake/delete/{ResourceType.PRACTITIONER.value}/123"
#         )


# @pytest.mark.asyncio
# async def test_delete_practitioner_ehr_api_error(
#     mock_practitioner_service: Practitioner,
# ) -> None:
#     """Test delete_practitioner when make_delete_request raises EhrApiError."""
#     service = mock_practitioner_service
#     with patch.object(
#         service, "_BaseService__make_request", new_callable=AsyncMock
#     ) as mock_make_request:
#         mock_make_request.side_effect = EhrApiError("API error", 400)
#         with pytest.raises(EhrApiError) as exc_info:
#             await service.delete("123")

#         assert "API error" in str(exc_info.value)
#         assert exc_info.value.status_code == 400
#         mock_make_request.assert_called_once_with(
#             "DELETE", f"/health-lake/delete/{ResourceType.PRACTITIONER.value}/123"
#         )
