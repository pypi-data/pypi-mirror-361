# from unittest.mock import AsyncMock

# from pydantic import ValidationError
# import pytest

# from carestack.base.base_types import ClientConfig
# from carestack.base.errors import EhrApiError
# from carestack.common.enums import (
#     UTILITY_API_ENDPOINTS,
#     Country,
#     OrganizationsIdType,
#     OrganizationEndPoints,
# )
# from carestack.organization.organization_dto import (
#     AddOrganizationDTO,
#     OrganizationSubTypeRequest,
#     OrganizationTypeRequest,
#     GetOrganizationsResponse,
#     OwnershipSubTypeRequest,
#     SearchOrganizationDTO,
#     SpecialitiesRequest,
#     UpdateOrganizationDTO,
# )
# from carestack.organization.organization_service import Organization
# from tests.config_test import client_config


# @pytest.fixture
# def organization_service(client_config: ClientConfig) -> Organization:
#     return Organization(client_config)


# @pytest.fixture
# def valid_add_organization_data() -> dict:
#     """Fixture providing a valid dictionary for AddOrganizationDTO."""
#     return {
#         "basicInformation": {
#             "facilityName": "Valid Test Facility",
#             "region": "North",
#             "addressLine1": "123 Valid St",
#             "addressLine2": "Suite 100",
#             "district": "Valid District",
#             "subDistrict": "Valid SubDistrict",
#             "city": "Valid City",
#             "state": "Valid State",
#             "country": Country.INDIA.value,
#             "pincode": "123456",
#             "latLongs": ["12.9716, 77.5946"],
#         },
#         "contactInformation": {
#             "mobileNumber": "+919876543210",
#             "email": "valid@example.com",
#             "landline": "0801234567",
#             "stdcode": "080",
#             "websiteLink": "http://valid.example.com",
#         },
#         "uploadDocuments": {
#             "boardPhoto": {"value": "valid_base64_1", "name": "valid_board.jpg"},
#             "buildingPhoto": {"value": "valid_base64_2", "name": "valid_building.png"},
#         },
#         "addAddressProof": [
#             {
#                 "addressProofType": "Electricity Bill",
#                 "addressProofAttachment": {
#                     "value": "valid_base64_3",
#                     "name": "valid_proof.pdf",
#                 },
#             }
#         ],
#         "facilityTimings": [
#             {"timings": "Mon-Fri", "shifts": [{"start": "09:00", "end": "17:00"}]}
#         ],
#         "facilityDetails": {
#             "ownershipType": "Private",
#             "ownershipSubType": "Individual",
#             "status": "Active",
#         },
#         "systemOfMedicine": {
#             "specialities": [
#                 {
#                     "systemofMedicineCode": "MODERN",
#                     "specialities": ["Cardiology", "Neurology"],
#                 }
#             ],
#             "facilityType": "Hospital",
#             "facilitySubType": "Super Speciality",
#             "serviceType": "IPD/OPD",
#         },
#         "facilityInventory": {
#             "totalNumberOfVentilators": 10,
#             "totalNumberOfBeds": 200,
#             "hasDialysisCenter": "Yes",
#             "hasPharmacy": "Yes",
#             "hasBloodBank": "Yes",
#             "hasCathLab": "Yes",
#             "hasDiagnosticLab": "Yes",
#             "hasImagingCenter": "Yes",
#             "servicesByImagingCenter": [
#                 {"service": "MRI", "count": 1},
#                 {"service": "CT", "count": 1},
#             ],
#             "nhrrid": "VALID_NHRRID",
#             "nin": "VALID_NIN",
#             "abpmjayid": "VALID_ABPMJAY",
#             "rohiniId": "VALID_ROHINI",
#             "echsId": "VALID_ECHS",
#             "cghsId": "VALID_CGHS",
#             "ceaRegistration": "VALID_CEA",
#             "stateInsuranceSchemeId": "VALID_STATEINS",
#         },
#         "accountId": "valid_account_123",
#     }


# @pytest.mark.asyncio
# async def test_validate_data_success(organization_service, valid_add_organization_data):
#     """
#     Tests successful validation using the valid_add_organization_data fixture.
#     """
#     valid_data_from_fixture = valid_add_organization_data

#     validated_data = await organization_service._Organization__validate_data(
#         AddOrganizationDTO, valid_data_from_fixture
#     )

#     expected_dto = AddOrganizationDTO(**valid_data_from_fixture)
#     assert validated_data == expected_dto.model_dump(by_alias=True)


# @pytest.mark.asyncio
# async def test_validate_data_failure(organization_service):
#     data = {"name": 123}  # Invalid type for name
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service._Organization__validate_data(
#             AddOrganizationDTO, data
#         )
#     assert "Validation failed" in str(exc_info.value)
#     assert exc_info.value.status_code == 400


# @pytest.mark.asyncio
# async def test_get_all_success(organization_service):
#     mock_response = {
#         "message": None,
#         "data": [{"id": "1"}],
#         "nextPageLink": "2",
#         "totalNumberOfRecords": None,
#     }
#     organization_service.get = AsyncMock(return_value=mock_response)
#     response = await organization_service.get_all()  # Call without next_page
#     assert isinstance(response, GetOrganizationsResponse)
#     assert response.model_dump(by_alias=True) == mock_response

#     # FIX: Assert that the second argument passed to 'get' was None (or ANY)
#     organization_service.get.assert_called_with(
#         OrganizationEndPoints.GET_ALL_ORGANIZATIONS,
#         None,  # Expect None when no params are passed
#         # Alternatively, if the base client might pass {} sometimes:
#         # ANY # Use ANY from unittest.mock if the exact value (None vs {}) isn't critical
#     )


# @pytest.mark.asyncio
# async def test_get_all_with_next_page_success(organization_service):
#     # Ensure mock_response matches GetOrganizationsResponse structure
#     mock_response = {
#         "message": None,
#         "data": [{"id": "1"}],
#         "nextPageLink": "3",  # Matches the expected next page
#         "totalNumberOfRecords": 10,  # Example value
#     }
#     organization_service.get = AsyncMock(return_value=mock_response)
#     response = await organization_service.get_all(next_page="2")

#     # Assert the response object structure
#     assert isinstance(response, GetOrganizationsResponse)
#     assert response.model_dump(by_alias=True) == mock_response

#     # Assert the underlying call with correct params
#     organization_service.get.assert_called_with(
#         OrganizationEndPoints.GET_ALL_ORGANIZATIONS, {"nextPage": "2"}
#     )


# @pytest.mark.asyncio
# async def test_get_all_api_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_all()
#     assert "API Error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_all_unexpected_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_all()
#     assert "Failed to fetch facilities" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_by_id_success(organization_service):
#     mock_response = {
#         "message": "Organization found",
#         "data": [{"id": "1", "name": "Test organization"}],
#         "nextPageLink": None,
#         "totalNumberOfRecords": 1,
#     }
#     organization_service.get = AsyncMock(return_value=mock_response)
#     response = await organization_service.get_by_id(
#         OrganizationsIdType.ORGANIZATION_ID, "1"
#     )
#     assert isinstance(response, GetOrganizationsResponse)
#     assert response.model_dump(by_alias=True) == mock_response
#     organization_service.get.assert_called_with(
#         OrganizationEndPoints.GET_ORGANIZATION_BY_ID.format(
#             search_param=OrganizationsIdType.ORGANIZATION_ID.value, search_term="1"
#         )
#     )


# @pytest.mark.asyncio
# async def test_get_by_id_api_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_by_id(OrganizationsIdType.ORGANIZATION_ID, "1")
#     assert "API Error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_by_id_unexpected_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_by_id(OrganizationsIdType.ORGANIZATION_ID, "1")
#     assert "Failed to fetch organization with ID" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_exists_success(organization_service):
#     mock_response = {"message": "organization Found !!!"}
#     organization_service.get = AsyncMock(return_value=mock_response)
#     exists = await organization_service.exists(OrganizationsIdType.ORGANIZATION_ID, "1")
#     assert exists is True
#     organization_service.get.assert_called_with(
#         OrganizationEndPoints.ORGANIZATION_EXISTS.format(
#             search_param=OrganizationsIdType.ORGANIZATION_ID.value, search_term="1"
#         )
#     )


# @pytest.mark.asyncio
# async def test_exists_not_found(organization_service):
#     organization_service.get = AsyncMock(side_effect=EhrApiError("Not Found", 404))
#     exists = await organization_service.exists(OrganizationsIdType.ORGANIZATION_ID, "1")
#     assert exists is False


# @pytest.mark.asyncio
# async def test_exists_api_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.exists(OrganizationsIdType.ORGANIZATION_ID, "1")
#     assert "API Error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_exists_unexpected_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.exists(OrganizationsIdType.ORGANIZATION_ID, "1")
#     assert "Error while checking organization" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_create_success(organization_service, valid_add_organization_data):
#     """Tests successful organization creation."""
#     mock_api_response = {
#         "message": "organization created successfully",
#         "facilityId": "new_facility_123",
#     }
#     organization_service.post = AsyncMock(return_value=mock_api_response)

#     organization_data_dict = valid_add_organization_data
#     organization_dto = AddOrganizationDTO(**organization_data_dict)

#     response = await organization_service.create(
#         organization_dto.model_dump(by_alias=True)
#     )

#     assert response == mock_api_response["message"]

#     organization_service.post.assert_called_once_with(
#         OrganizationEndPoints.REGISTER_ORGANIZATION,
#         organization_dto.model_dump(by_alias=True),
#     )


# @pytest.mark.asyncio
# async def test_create_validation_error(organization_service):
#     organization_data = {"name": 123}  # Invalid type for name
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.create(organization_data)
#     assert "Validation failed" in str(exc_info.value)
#     assert exc_info.value.status_code == 400


# @pytest.mark.asyncio
# async def test_create_api_error(organization_service, valid_add_organization_data):
#     organization_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))

#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.create(valid_add_organization_data)
#     assert "API Error" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_create_unexpected_error(
#     organization_service, valid_add_organization_data
# ):
#     organization_service.post = AsyncMock(side_effect=Exception("Unexpected Error"))

#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.create(valid_add_organization_data)

#     assert "Failed to register organization" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_update_success(organization_service):
#     mock_response = {"message": "organization updated successfully"}
#     organization_service.put = AsyncMock(return_value=mock_response)
#     update_data = {
#         "id": "1",
#         "spoc_name": "Updated Spoc",
#         "spoc_id": "spoc123",
#         "consent_manager_name": "Updated Consent Manager",
#         "consent_manager_id": "consent123",
#     }
#     update_dto = UpdateOrganizationDTO(**update_data)
#     response = await organization_service.update(update_dto)

#     assert response == "organization updated successfully"
#     expected_validated_data = {
#         "id": "1",
#         "spocName": "Updated Spoc",
#         "spocId": "spoc123",
#         "consentManagerName": "Updated Consent Manager",
#         "consentManagerId": "consent123",
#     }
#     organization_service.put.assert_called_with(
#         OrganizationEndPoints.UPDATE_ORGANIZATION,
#         expected_validated_data,
#     )


# @pytest.mark.asyncio
# async def test_update_validation_error(organization_service):
#     update_data = {"id": "1", "spoc_name": 123}
#     with pytest.raises(EhrApiError) as exc_info:
#         try:
#             update_dto = UpdateOrganizationDTO(**update_data)
#             await organization_service.update(update_dto)
#         except Exception as e:
#             if "validation error" in str(e).lower():
#                 raise EhrApiError(f"Validation failed: {e}", status_code=400) from e
#             raise e

#     assert "Validation failed" in str(exc_info.value)
#     assert exc_info.value.status_code == 400


# @pytest.mark.asyncio
# async def test_update_api_error(organization_service):
#     organization_service.put = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     update_data = {
#         "id": "1",
#         "spoc_name": "Updated Spoc",
#         "spoc_id": "spoc123",
#         "consent_manager_name": "Updated Consent Manager",
#         "consent_manager_id": "consent123",
#     }
#     update_dto = UpdateOrganizationDTO(**update_data)
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.update(update_dto)
#     assert "API Error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_update_unexpected_error(organization_service):
#     organization_service.put = AsyncMock(side_effect=Exception("Unexpected Error"))
#     update_data = {
#         "id": "1",
#         "spoc_name": "Updated Spoc",
#         "spoc_id": "spoc123",
#         "consent_manager_name": "Updated Consent Manager",
#         "consent_manager_id": "consent123",
#     }
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.update(update_data)
#     assert "Failed to update organization" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_remove_success(organization_service):
#     mock_response = {"message": "organization deleted successfully"}
#     organization_service.delete = AsyncMock(return_value=mock_response)
#     response = await organization_service.remove("1")
#     assert response == "organization deleted successfully"
#     organization_service.delete.assert_called_with(
#         OrganizationEndPoints.DELETE_ORGANIZATION.format(organization_id="1")
#     )


# @pytest.mark.asyncio
# async def test_remove_api_error(organization_service):
#     organization_service.delete = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.remove("1")
#     assert "API Error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_remove_unexpected_error(organization_service):
#     organization_service.delete = AsyncMock(side_effect=Exception("Unexpected Error"))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.remove("1")
#     assert "Failed to delete organization" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_search_organization_success(organization_service):
#     mock_response = {"facilities": [{"id": "1"}]}
#     organization_service.post = AsyncMock(return_value=mock_response)
#     search_data = {
#         "ownership_code": "test_owner",
#         "state_lgd_code": "test_state",
#         "district_lgd_code": "test_district",
#         "sub_district_lgd_code": "test_subdistrict",
#         "pincode": "123456",
#         "organization_name": "Test organization",
#         "organization_id": "1",
#         "page": 1,
#         "results_per_page": 10,
#     }
#     search_dto = SearchOrganizationDTO(**search_data)
#     response = await organization_service.search_organization(search_dto)
#     assert response == mock_response
#     expected_validated_data = {
#         "ownershipCode": "test_owner",  # Alias is correct
#         "stateLGDCode": "test_state",
#         "districtLGDCode": "test_district",
#         "subDistrictLGDCode": "test_subdistrict",
#         "pincode": "123456",
#         "facilityName": "Test organization",
#         "facilityId": "1",
#         "page": 1,
#         "resultsPerPage": 10,
#     }
#     organization_service.post.assert_called_with(
#         OrganizationEndPoints.SEARCH_ORGANIZATION,
#         expected_validated_data,  # Compare with the alias-based dictionary
#     )


# @pytest.mark.asyncio
# async def test_search_organization_validation_error(organization_service):
#     """
#     Tests that search_organization raises EhrApiError(400) for invalid input
#     due to Pydantic validation failure triggered by __validate_data.
#     """
#     invalid_data = {
#         "organizationName": "Test Facility",
#         "resultsPerPage": 10,
#     }
#     with pytest.raises(EhrApiError) as exc_info:
#         try:
#             request_obj = SearchOrganizationDTO(**invalid_data)
#             await organization_service.search_organization(request_obj)

#         except ValidationError as ve:
#             raise EhrApiError(f"Validation failed: {ve}", 400) from ve
#     assert exc_info.value.status_code == 400
#     assert "Validation failed" in str(exc_info.value)
#     assert "page" in str(exc_info.value)
#     assert "Field required" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_search_organization_api_error(organization_service):
#     organization_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))

#     search_data = {
#         "ownership_code": "test_owner",
#         "state_lgd_code": "test_state",
#         "district_lgd_code": "test_district",
#         "sub_district_lgd_code": "test_subdistrict",
#         "pincode": "123456",
#         "organization_name": "Test organization",
#         "organization_id": "1",
#         "page": 1,
#         "results_per_page": 10,
#     }
#     search_dto = SearchOrganizationDTO(**search_data)

#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.search_organization(search_dto)

#     assert "API Error" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_search_organization_unexpected_error(organization_service):
#     organization_service.post = AsyncMock(side_effect=Exception("Unexpected Error"))
#     search_data = {
#         "ownership_Code": "test_owner",
#         "state_lgd_code": "test_state",
#         "district_lgd_code": "test_district",
#         "sub_district_lgd_code": "test_subdistrict",
#         "pincode": "123456",
#         "organization_name": "Test organization",
#         "organization_id": "1",
#         "page": 1,
#         "results_per_page": 10,
#     }
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.search_organization(search_data)
#     assert "Unexpected error while searching for organization" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_master_types_success(organization_service):
#     mock_response = {"types": ["type1", "type2"]}
#     organization_service.get = AsyncMock(return_value=mock_response)
#     response = await organization_service.get_master_types()
#     assert response == mock_response
#     organization_service.get.assert_called_with(UTILITY_API_ENDPOINTS.MASTER_TYPES)


# @pytest.mark.asyncio
# async def test_get_master_types_api_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_master_types()
#     assert "API Error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_master_types_unexpected_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_master_types()
#     assert "Failed to get master types" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_master_data_success(organization_service):
#     mock_response = {"data": ["data1", "data2"]}
#     organization_service.get = AsyncMock(return_value=mock_response)
#     response = await organization_service.get_master_data("test_type")
#     assert response == mock_response
#     organization_service.get.assert_called_with(
#         UTILITY_API_ENDPOINTS.MASTER_DATA_BY_TYPE.format(type="test_type")
#     )


# @pytest.mark.asyncio
# async def test_get_master_data_api_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_master_data("test_type")
#     assert "API Error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_master_data_unexpected_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_master_data("test_type")
#     assert "Failed to get master data of type" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_lgd_states_success(organization_service):
#     mock_response = [{"states": ["state1", "state2"]}]
#     organization_service.get = AsyncMock(return_value=mock_response)
#     response = await organization_service.get_lgd_states()
#     assert response == mock_response
#     organization_service.get.assert_called_with(
#         UTILITY_API_ENDPOINTS.STATES_AND_DISTRICTS
#     )


# @pytest.mark.asyncio
# async def test_get_lgd_states_api_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_lgd_states()
#     assert "API Error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_lgd_states_unexpected_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_lgd_states()
#     assert "Failed to get LGD states" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_lgd_sub_districts_success(organization_service):
#     mock_response = [{"subdistricts": ["subdistrict1", "subdistrict2"]}]
#     organization_service.get = AsyncMock(return_value=mock_response)
#     response = await organization_service.get_lgd_sub_districts("test_district")
#     assert response == mock_response
#     organization_service.get.assert_called_with(
#         UTILITY_API_ENDPOINTS.SUBDISTRICTS.format(district_code="test_district")
#     )


# @pytest.mark.asyncio
# async def test_get_lgd_sub_districts_api_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_lgd_sub_districts("test_district")
#     assert "API Error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_lgd_sub_districts_unexpected_error(organization_service):
#     organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_lgd_sub_districts("test_district")
#     assert "Failed to get LGD sub-districts for district code" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_organization_type_success(organization_service):
#     mock_response = {"organizationTypes": ["type1", "type2"]}
#     organization_service.post = AsyncMock(return_value=mock_response)
#     request_body = OrganizationTypeRequest(
#         ownershipCode="test_owner", systemOfMedicineCode="test_system"
#     )
#     response = await organization_service.get_organization_type(request_body)
#     assert response == mock_response
#     organization_service.post.assert_called_with(
#         UTILITY_API_ENDPOINTS.ORGANIZATION_TYPE,
#         {"ownershipCode": "test_owner", "systemOfMedicineCode": "test_system"},
#     )


# @pytest.mark.asyncio
# async def test_get_organization_type_validation_error(organization_service):
#     """
#     Tests that get_organization_type raises EhrApiError(400) for invalid input
#     due to Pydantic validation failure triggered by __validate_data.
#     """
#     invalid_data = {"ownershipCode": ""}
#     with pytest.raises(EhrApiError) as exc_info:
#         try:
#             request_obj = OrganizationTypeRequest(**invalid_data)
#             await organization_service.get_organization_type(request_obj)

#         except ValidationError as ve:
#             raise EhrApiError(f"Validation failed: {ve}", 400) from ve

#     assert exc_info.value.status_code == 400
#     assert "Validation failed" in str(exc_info.value)
#     assert "ownershipCode" in str(exc_info.value)
#     assert "Field required" in str(
#         exc_info.value
#     ) or "ownershipCode is required" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_organization_type_api_error(organization_service):
#     organization_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     request_body = OrganizationTypeRequest(
#         ownershipCode="test_owner", systemOfMedicineCode="test_system"
#     )
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_organization_type(request_body)
#     assert "API Error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_organization_type_unexpected_error(organization_service):
#     organization_service.post = AsyncMock(side_effect=Exception("Unexpected Error"))
#     request_body = OrganizationTypeRequest(
#         ownershipCode="test_owner", systemOfMedicineCode="test_system"
#     )
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_organization_type(request_body)
#     assert "Failed to get organization types" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_owner_subtypes_success(organization_service):
#     mock_response = {"ownerSubtypes": ["subtype1", "subtype2"]}
#     organization_service.post = AsyncMock(return_value=mock_response)
#     request_body = OwnershipSubTypeRequest(
#         ownershipCode="test_owner", ownerSubtypeCode="test_subtype"
#     )
#     response = await organization_service.get_owner_subtypes(request_body)
#     assert response == mock_response
#     organization_service.post.assert_called_with(
#         UTILITY_API_ENDPOINTS.OWNER_SUBTYPE,
#         {"ownershipCode": "test_owner", "ownerSubtypeCode": "test_subtype"},
#     )


# @pytest.mark.asyncio
# async def test_get_owner_subtypes_validation_error(organization_service):
#     """
#     Tests that get_owner_subtypes raises EhrApiError(400) for invalid input
#     due to Pydantic validation failure triggered by __validate_data.
#     """
#     invalid_data = {"ownershipCode": ""}
#     with pytest.raises(EhrApiError) as exc_info:
#         try:
#             request_obj = OwnershipSubTypeRequest(**invalid_data)
#             await organization_service.get_owner_subtypes(request_obj)

#         except ValidationError as ve:
#             raise EhrApiError(f"Validation failed: {ve}", 400) from ve

#     assert exc_info.value.status_code == 400
#     assert "Validation failed" in str(exc_info.value)
#     assert "ownershipCode" in str(exc_info.value)
#     assert "Field required" in str(
#         exc_info.value
#     ) or "ownershipCode is required" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_owner_subtypes_api_error(organization_service):
#     organization_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     request_body = OwnershipSubTypeRequest(
#         ownershipCode="test_owner", ownerSubtypeCode="test_subtype"
#     )
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_owner_subtypes(request_body)
#     assert "API Error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_owner_subtypes_unexpected_error(organization_service):
#     organization_service.post = AsyncMock(side_effect=Exception("Unexpected Error"))
#     request_body = OwnershipSubTypeRequest(
#         ownershipCode="test_owner", ownerSubtypeCode="test_subtype"
#     )
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_owner_subtypes(request_body)
#     assert "Failed to get owner subtypes" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_specialities_success(organization_service):
#     mock_response = {"specialities": ["spec1", "spec2"]}
#     organization_service.post = AsyncMock(return_value=mock_response)
#     request_body = SpecialitiesRequest(systemOfMedicineCode="test_system")
#     response = await organization_service.get_specialities(request_body)
#     assert response == mock_response
#     organization_service.post.assert_called_with(
#         UTILITY_API_ENDPOINTS.SPECIALITIES, {"systemOfMedicineCode": "test_system"}
#     )


# @pytest.mark.asyncio
# async def test_get_specialities_validation_error(organization_service):
#     """
#     Tests that get_specialities raises EhrApiError(400) for invalid input
#     due to Pydantic validation failure triggered by __validate_data.
#     """
#     invalid_data = {"systemOfMedicineCode": ""}
#     with pytest.raises(EhrApiError) as exc_info:
#         try:
#             request_obj = SpecialitiesRequest(**invalid_data)
#             await organization_service.get_specialities(request_obj)

#         except ValidationError as ve:
#             raise EhrApiError(f"Validation failed: {ve}", 400) from ve
#     assert exc_info.value.status_code == 400
#     assert "Validation failed" in str(exc_info.value)
#     assert "systemOfMedicineCode" in str(exc_info.value)
#     assert "Field required" in str(
#         exc_info.value
#     ) or "systemOfMedicineCode is required" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_specialities_api_error(organization_service):
#     organization_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     request_body = SpecialitiesRequest(systemOfMedicineCode="test_system")
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_specialities(request_body)
#     assert "API Error" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_specialities_unexpected_error(organization_service):
#     organization_service.post = AsyncMock(side_effect=Exception("Unexpected Error"))
#     request_body = SpecialitiesRequest(systemOfMedicineCode="test_system")
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_specialities(request_body)
#     assert "Failed to get specialities" in str(exc_info.value)
#     assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_get_organization_subtypes_success(organization_service):
#     mock_response = {"facilitySubtypes": ["subtype1", "subtype2"]}
#     organization_service.post = AsyncMock(return_value=mock_response)
#     request_body = OrganizationSubTypeRequest(facilityTypeCode="test_type")
#     response = await organization_service.get_organization_subtypes(request_body)
#     assert response == mock_response
#     organization_service.post.assert_called_with(
#         UTILITY_API_ENDPOINTS.ORGANIZATION_SUBTYPE,
#         {"facilityTypeCode": "test_type"},
#     )


# @pytest.mark.asyncio
# async def test_get_organization_subtypes_validation_error(organization_service):
#     """
#     Tests that get_organization_subtypes raises EhrApiError(400) for invalid input
#     due to Pydantic validation failure triggered by __validate_data.
#     """
#     invalid_data = {"facilityTypeCode": ""}
#     with pytest.raises(EhrApiError) as exc_info:
#         try:
#             request_obj = OrganizationSubTypeRequest(**invalid_data)
#             await organization_service.get_organization_subtypes(request_obj)

#         except ValidationError as ve:
#             raise EhrApiError(f"Validation failed: {ve}", 400) from ve
#     assert exc_info.value.status_code == 400
#     assert "Validation failed" in str(exc_info.value)
#     assert "facilityTypeCode" in str(exc_info.value)
#     assert "Field required" in str(
#         exc_info.value
#     ) or "facilityTypeCode is required" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_get_organization_subtypes_api_error(organization_service):
#     organization_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))
#     request_body = OrganizationSubTypeRequest(facilityTypeCode="test_type")
#     with pytest.raises(EhrApiError) as exc_info:
#         await organization_service.get_organization_subtypes(request_body)
#     assert "API Error" in str(exc_info.value)
