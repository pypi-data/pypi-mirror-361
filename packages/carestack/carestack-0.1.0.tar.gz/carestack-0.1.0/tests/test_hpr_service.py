# from base.base_types import ClientConfig
# import pytest
# from unittest.mock import AsyncMock, patch
# from python.carestack.practitioner.hpr_registration.hpr_service import HPRService
# from python.carestack.practitioner.hpr_registration.hpr_dto import (
#     GenerateAadhaarOtpResponseSchema,
#     VerifyAadhaarOtpResponseSchema,
#     DemographicAuthViaMobileResponseSchema,
#     MobileOtpResponseSchema,
#     CheckAccountExistResponseSchema,
#     CreateHprIdWithPreVerifiedResponseBody,
#     GenerateAadhaarOtpRequestSchema,
#     VerifyAadhaarOtpRequestSchema,
#     DemographicAuthViaMobileRequestSchema,
#     GenerateMobileOtpRequestSchema,
#     VerifyMobileOtpRequestSchema,
#     CheckAccountExistRequestSchema,
#     HpIdSuggestionRequestSchema,
#     CreateHprIdWithPreVerifiedRequestBody,
# )
# from python.carestack.base.errors import EhrApiError

# @pytest.fixture
# def mock_hpr_service(client_config:ClientConfig) -> HPRService:
#     return HPRService(client_config)

# # --- generate_aadhaar_otp Tests ---
# @pytest.mark.asyncio
# async def test_generate_aadhaar_otp_success(mock_hpr_service:HPRService)->None:
#     """Test successful generation of Aadhaar OTP."""
#     service = mock_hpr_service
#     mock_response_data = {"txnId": "txn123", "mobileNumber": "9876543210"}
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.return_value = mock_response_data
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"aadhaar": "123456789012"}
#             result: GenerateAadhaarOtpResponseSchema = await service.generate_aadhaar_otp({"aadhaar": "123456789012"})
#             mock_make_post.assert_called_once_with("/aadhaar/generateOtp", {"aadhaar": "123456789012"})
#             mock_validate.assert_called_once_with(GenerateAadhaarOtpRequestSchema, {"aadhaar": "123456789012"})
#             assert isinstance(result, GenerateAadhaarOtpResponseSchema)
#             assert result.txnId == "txn123"
#             assert result.mobileNumber == "9876543210"

# @pytest.mark.asyncio
# async def test_generate_aadhaar_otp_ehr_api_error(mock_hpr_service:HPRService)->None:
#     """Test generate_aadhaar_otp when make_post_request raises EhrApiError."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = EhrApiError("API error", 400)
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"aadhaar": "123456789012"}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.generate_aadhaar_otp({"aadhaar": "123456789012"})
#             assert str(exc_info.value) == "API error"
#             assert exc_info.value.status_code == 400


# @pytest.mark.asyncio
# async def test_generate_aadhaar_otp_general_exception(mock_hpr_service:HPRService)->None:
#     """Test generate_aadhaar_otp when make_post_request raises a general Exception."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = Exception("General error")
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"aadhaar": "123456789012"}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.generate_aadhaar_otp({"aadhaar": "123456789012"})
#             assert "Error occurred while generating Aadhaar OTP" in str(exc_info.value)
#             assert exc_info.value.status_code == 500

# # --- verify_aadhaar_otp Tests ---
# @pytest.mark.asyncio
# async def test_verify_aadhaar_otp_success(mock_hpr_service:HPRService)->None:
#     """Test successful verification of Aadhaar OTP."""
#     service = mock_hpr_service
#     mock_response_data = {"txnId": "txn123", "mobileNumber": "9876543210", "photo": "test", "gender":"male", "name":"test", "email":"test@test.com", "pincode":"123456", "address":"test","district": "Test District",
#         "state": "Test State" }
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.return_value = mock_response_data
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"otp": "123456", "domainName": "domain", "idType":"idtype", "txnId": "txn123"}
#             result: VerifyAadhaarOtpResponseSchema = await service.verify_aadhaar_otp({"otp": "123456", "domainName": "domain", "idType":"idtype", "txnId": "txn123"})
#             mock_make_post.assert_called_once_with("/aadhaar/verifyOtp", {"otp": "123456", "domainName": "domain", "idType":"idtype", "txnId": "txn123"})
#             mock_validate.assert_called_once_with(VerifyAadhaarOtpRequestSchema, {"otp": "123456", "domainName": "domain", "idType":"idtype", "txnId": "txn123"})
#             assert isinstance(result, VerifyAadhaarOtpResponseSchema)
#             assert result.txnId == "txn123"
#             assert result.mobileNumber == "9876543210"
#             assert result.photo == "test"
#             assert result.gender == "male"
#             assert result.name == "test"
#             assert result.email == "test@test.com"
#             assert result.pincode == "123456"
#             assert result.address == "test"
#             assert result.district == "Test District"
#             assert result.state == "Test State"


# @pytest.mark.asyncio
# async def test_verify_aadhaar_otp_ehr_api_error(mock_hpr_service:HPRService)->None:
#     """Test verify_aadhaar_otp when make_post_request raises EhrApiError."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = EhrApiError("API error", 400)
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"otp": "123456", "domainName": "domain", "idType":"idtype", "txnId": "txn123"}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.verify_aadhaar_otp({"otp": "123456", "domainName": "domain", "idType":"idtype", "txnId": "txn123"})
#             assert "Error occurred while verifying Aadhaar OTP" in str(exc_info.value)
#             assert exc_info.value.status_code == 500

# @pytest.mark.asyncio
# async def test_verify_aadhaar_otp_general_exception(mock_hpr_service:HPRService)->None:
#     """Test verify_aadhaar_otp when make_post_request raises a general Exception."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = Exception("General error")
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"otp": "123456", "domainName": "domain", "idType":"idtype", "txnId": "txn123"}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.verify_aadhaar_otp({"otp": "123456", "domainName": "domain", "idType":"idtype", "txnId": "txn123"})
#             assert "Error occurred while verifying Aadhaar OTP" in str(exc_info.value)
#             assert exc_info.value.status_code == 500

# # --- demographic_auth_via_mobile Tests ---
# @pytest.mark.asyncio
# async def test_demographic_auth_via_mobile_success(mock_hpr_service:HPRService)->None:
#     """Test successful demographic authentication via mobile."""
#     service = mock_hpr_service
#     mock_response_data = {"verified": True}
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.return_value = mock_response_data
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"txnId": "txn123", "mobileNumber": "9876543210"}
#             result: DemographicAuthViaMobileResponseSchema = await service.demographic_auth_via_mobile({"txnId": "txn123", "mobileNumber": "9876543210"})
#             mock_make_post.assert_called_once_with("/demographic-auth/mobile", {"txnId": "txn123", "mobileNumber": "9876543210"})
#             mock_validate.assert_called_once_with(DemographicAuthViaMobileRequestSchema, {"txnId": "txn123", "mobileNumber": "9876543210"})
#             assert isinstance(result, DemographicAuthViaMobileResponseSchema)
#             assert result.verified is True

# @pytest.mark.asyncio
# async def test_demographic_auth_via_mobile_ehr_api_error(mock_hpr_service:HPRService)->None:
#     """Test demographic_auth_via_mobile when make_post_request raises EhrApiError."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = EhrApiError("API error", 400)
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"txnId": "txn123", "mobileNumber": "9876543210"}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.demographic_auth_via_mobile({"txnId": "txn123", "mobileNumber": "9876543210"})
#             assert "Error occurred while verifying demographic auth via mobile" in str(exc_info.value)
#             assert exc_info.value.status_code == 500

# @pytest.mark.asyncio
# async def test_demographic_auth_via_mobile_general_exception(mock_hpr_service:HPRService)->None:
#     """Test demographic_auth_via_mobile when make_post_request raises a general Exception."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = Exception("General error")
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"txnId": "txn123", "mobileNumber": "9876543210"}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.demographic_auth_via_mobile({"txnId": "txn123", "mobileNumber": "9876543210"})
#             assert "Error occurred while verifying demographic auth via mobile" in str(exc_info.value)
#             assert exc_info.value.status_code == 500

# # --- generate_mobile_otp Tests ---
# @pytest.mark.asyncio
# async def test_generate_mobile_otp_success(mock_hpr_service:HPRService)->None:
#     """Test successful generation of mobile OTP."""
#     service = mock_hpr_service
#     mock_response_data = {"txnId": "txn123", "mobileNumber": None}
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.return_value = mock_response_data
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"mobile": "9876543210","txnId": "txn123"}
#             result: MobileOtpResponseSchema = await service.generate_mobile_otp({"mobile": "9876543210","txnId": "txn123"})
#             mock_make_post.assert_called_once_with("/generate/mobileOtp", {"mobile": "9876543210","txnId": "txn123"})
#             mock_validate.assert_called_once_with(GenerateMobileOtpRequestSchema, {"mobile": "9876543210","txnId": "txn123"})
#             assert isinstance(result, MobileOtpResponseSchema)
#             assert result.txnId == "txn123"
#             assert result.mobileNumber is None

# @pytest.mark.asyncio
# async def test_generate_mobile_otp_ehr_api_error(mock_hpr_service:HPRService)->None:
#     """Test generate_mobile_otp when make_post_request raises EhrApiError."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = EhrApiError("API error", 400)
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"mobile": "9876543210","txnId": "txn123"}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.generate_mobile_otp({"mobile": "9876543210","txnId": "txn123"})
#             assert "Error occurred while generating mobile OTP" in str(exc_info.value)
#             assert exc_info.value.status_code == 500

# @pytest.mark.asyncio
# async def test_generate_mobile_otp_general_exception(mock_hpr_service:HPRService)->None:
#     """Test generate_mobile_otp when make_post_request raises a general Exception."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = Exception("General error")
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"mobile": "9876543210","txnId": "txn123"}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.generate_mobile_otp({"mobile": "9876543210","txnId": "txn123"})
#             assert "Error occurred while generating mobile OTP" in str(exc_info.value)
#             assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_verify_mobile_otp_success(mock_hpr_service:HPRService)->None:
#     """Test successful verification of mobile OTP."""
#     service = mock_hpr_service
#     mock_response_data = {"txnId": "txn123", "mobileNumber": None}
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.return_value = mock_response_data
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"otp": "123456", "txnId": "txn123"}
#             result: MobileOtpResponseSchema = await service.verify_mobile_otp({"otp": "123456", "txnId": "txn123"})
#             mock_make_post.assert_called_once_with("/verify/mobileOtp", {"otp": "123456", "txnId": "txn123"})
#             mock_validate.assert_called_once_with(VerifyMobileOtpRequestSchema, {"otp": "123456", "txnId": "txn123"})
#             assert isinstance(result, MobileOtpResponseSchema)
#             assert result.txnId == "txn123"
#             assert result.mobileNumber is None


# @pytest.mark.asyncio
# async def test_verify_mobile_otp_ehr_api_error(mock_hpr_service:HPRService)->None:
#     """Test verify_mobile_otp when make_post_request raises EhrApiError."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = EhrApiError("API error", 400)
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"otp": "123456", "txnId": "txn123"}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.verify_mobile_otp({"otp": "123456", "txnId": "txn123"})
#             assert "Error occurred while verifying mobile OTP" in str(exc_info.value)
#             assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_verify_mobile_otp_general_exception(mock_hpr_service:HPRService)->None:
#     """Test verify_mobile_otp when make_post_request raises a general Exception."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = Exception("General error")
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"otp": "123456", "txnId": "txn123"}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.verify_mobile_otp({"otp": "123456", "txnId": "txn123"})
#             assert "Error occurred while verifying mobile OTP" in str(exc_info.value)
#             assert exc_info.value.status_code == 500

# # --- check_account_exist Tests ---
# @pytest.mark.asyncio
# async def test_check_account_exist_success(mock_hpr_service:HPRService)->None:
#     """Test successful check of account existence."""
#     service = mock_hpr_service
#     mock_response_data = {
#     "txnId": "txn123",
#     "mobileNumber": "9876543210",
#     "photo": "test",
#     "gender": "male",
#     "name": "test",
#     "email": "test@test.com",
#     "pincode": "123456",
#     "address": "test",
#     }

#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.return_value = mock_response_data
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"txnId": "txn123", "preverifiedCheck": True}
#             result: CheckAccountExistResponseSchema = await service.check_account_exist({"txnId": "txn123", "preverifiedCheck": True})
#             mock_make_post.assert_called_once_with("/check/account-exist", {"txnId": "txn123", "preverifiedCheck": True})
#             mock_validate.assert_called_once_with(CheckAccountExistRequestSchema, {"txnId": "txn123", "preverifiedCheck": True})
#             assert isinstance(result, CheckAccountExistResponseSchema)
#             assert result.txnId == "txn123"
#             assert result.mobileNumber == "9876543210"
#             assert result.photo == "test"
#             assert result.gender == "male"
#             assert result.name == "test"
#             assert result.email == "test@test.com"
#             assert result.pincode == "123456"
#             assert result.address == "test"


# @pytest.mark.asyncio
# async def test_check_account_exist_ehr_api_error(mock_hpr_service:HPRService)->None:
#     """Test check_account_exist when make_post_request raises EhrApiError."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = EhrApiError("API error", 400)
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"txnId": "txn123", "preverifiedCheck": True}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.check_account_exist({"txnId": "txn123", "preverifiedCheck": True})
#             assert "Error occurred while checking account existence" in str(exc_info.value)
#             assert exc_info.value.status_code == 500


# @pytest.mark.asyncio
# async def test_check_account_exist_general_exception(mock_hpr_service:HPRService)->None:
#     """Test check_account_exist when make_post_request raises a general Exception."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = Exception("General error")
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"txnId": "txn123", "preverifiedCheck": True}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.check_account_exist({"txnId": "txn123", "preverifiedCheck": True})
#             assert "Error occurred while checking account existence" in str(exc_info.value)
#             assert exc_info.value.status_code == 500

# # --- get_hpr_suggestion Tests ---
# @pytest.mark.asyncio
# async def test_get_hpr_suggestion_success(mock_hpr_service:HPRService)->None:
#     """Test successful retrieval of HPR ID suggestions."""
#     service = mock_hpr_service
#     mock_response_data = ["hprid1", "hprid2", "hprid3"]
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.return_value = mock_response_data
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"txnId": "txn123"}
#             result = await service.get_hpr_suggestion({"txnId": "txn123"})
#             mock_make_post.assert_called_once_with("/hpId/suggestion", {"txnId": "txn123"})
#             mock_validate.assert_called_once_with(HpIdSuggestionRequestSchema, {"txnId": "txn123"})
#             assert isinstance(result, list)
#             assert result == mock_response_data


# @pytest.mark.asyncio
# async def test_get_hpr_suggestion_ehr_api_error(mock_hpr_service:HPRService)->None:
#     """Test get_hpr_suggestion when make_post_request raises EhrApiError."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = EhrApiError("API error", 400)
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"txnId": "txn123"}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.get_hpr_suggestion({"txnId": "txn123"})
#             assert "Error occurred while getting hpr suggestion" in str(exc_info.value)
#             assert exc_info.value.status_code == 500

# @pytest.mark.asyncio
# async def test_get_hpr_suggestion_general_exception(mock_hpr_service:HPRService)->None:
#     """Test get_hpr_suggestion when make_post_request raises a general Exception."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = Exception("General error")
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {"txnId": "txn123"}
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.get_hpr_suggestion({"txnId": "txn123"})
#             assert "Error occurred while getting hpr suggestion" in str(exc_info.value)
#             assert exc_info.value.status_code == 500

# # --- create_hpr_id_with_preverified Tests ---
# @pytest.mark.asyncio
# async def test_create_hpr_id_with_preverified_success(mock_hpr_service:HPRService)->None:
#     """Test successful creation of HPR ID with pre-verified data."""
#     service = mock_hpr_service
#     mock_response_data = {
#         "token": "test_token",
#         "hprIdNumber": "test_hpr_id",
#         "name": "Test User",
#         "gender": "male",
#         "yearOfBirth": "1990",
#         "monthOfBirth": "01",
#         "dayOfBirth": "01",
#         "firstName": "Test",
#         "hprId": "test_hpr_id",
#         "lastName": "User",
#         "middleName": "Middle",
#         "stateCode": "TS",
#         "districtCode": "29",
#         "stateName": "Telangana",
#         "districtName": "test_district",
#         "email": "test@example.com",
#         "kycPhoto": "test",
#         "mobile": "9876543210",
#         "categoryCode": "test",
#         "subCategoryCode": "test",
#         "authMethods": "test",
#         "new": True,
#     }
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.return_value = mock_response_data
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {
#                 "address": "test address",
#                 "dayOfBirth": "01",
#                 "districtCode": "29",
#                 "email": "test@example.com",
#                 "firstName": "Test",
#                 "hpCategoryCode": "test",
#                 "hpSubCategoryCode": "test",
#                 "hprId": "test_hpr_id",
#                 "lastName": "User",
#                 "middleName": "Middle",
#                 "monthOfBirth": "01",
#                 "password": "test_password",
#                 "pincode": "123456",
#                 "profilePhoto": "test",
#                 "stateCode": "TS",
#                 "txnId": "txn123",
#                 "yearOfBirth": "1990",
#             }
#             request_body = mock_validate.return_value
#             result: CreateHprIdWithPreVerifiedResponseBody = await service.create_hpr_id_with_preverified(request_body)

#             mock_make_post.assert_called_once_with("/create/hprIdWithPreVerified", request_body)
#             mock_validate.assert_called_once_with(CreateHprIdWithPreVerifiedRequestBody, request_body)
#             assert isinstance(result, CreateHprIdWithPreVerifiedResponseBody)
#             assert result.token == "test_token"
#             assert result.hprIdNumber == "test_hpr_id"

# @pytest.mark.asyncio
# async def test_create_hpr_id_with_preverified_ehr_api_error(mock_hpr_service:HPRService)->None:
#     """Test create_hpr_id_with_preverified when make_post_request raises EhrApiError."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = EhrApiError("API error", 400)
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {
#                 "address": "test address",
#                 "dayOfBirth": "01",
#                 "districtCode": "29",
#                 "email": "test@example.com",
#                 "firstName": "Test",
#                 "hpCategoryCode": "test",
#                 "hpSubCategoryCode": "test",
#                 "hprId": "test_hpr_id",
#                 "lastName": "User",
#                 "middleName": "Middle",
#                 "monthOfBirth": "01",
#                 "password": "test_password",
#                 "pincode": "123456",
#                 "profilePhoto": "test",
#                 "stateCode": "TS",
#                 "txnId": "txn123",
#                 "yearOfBirth": "1990",
#             }
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.create_hpr_id_with_preverified(mock_validate.return_value)
#         assert "API error" in str(exc_info.value)
#         assert exc_info.value.status_code == 400
#         assert "Error occurred while creating hpr id with preverified data" in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_create_hpr_id_with_preverified_general_exception(mock_hpr_service:HPRService)->None:
#     """Test create_hpr_id_with_preverified when make_post_request raises a general Exception."""
#     service = mock_hpr_service
#     with patch.object(service, 'make_post_request', new_callable=AsyncMock) as mock_make_post:
#         mock_make_post.side_effect = Exception("General error")
#         with patch.object(service, 'validate_data', new_callable=AsyncMock) as mock_validate:
#             mock_validate.return_value = {
#                 "address": "test address",
#                 "dayOfBirth": "01",
#                 "districtCode": "29",
#                 "email": "test@example.com",
#                 "firstName": "Test",
#                 "hpCategoryCode": "test",
#                 "hpSubCategoryCode": "test",
#                 "hprId": "test_hpr_id",
#                 "lastName": "User",
#                 "middleName": "Middle",
#                 "monthOfBirth": "01",
#                 "password": "test_password",
#                 "pincode": "123456",
#                 "profilePhoto": "test",
#                 "stateCode": "TS",
#                 "txnId": "txn123",
#                 "yearOfBirth": "1990",
#             }
#             with pytest.raises(EhrApiError) as exc_info:
#                 await service.create_hpr_id_with_preverified(mock_validate.return_value)
#         assert "Error occurred while creating hpr id with preverified data" in str(exc_info.value)
#         assert exc_info.value.status_code == 500
