from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

def validate_non_empty(value: str, field_name: str) -> str:
    """Helper function to validate required fields."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value.strip()

class GenerateAadhaarOtpRequestSchema(BaseModel):
    """Request schema for generating Aadhaar OTP."""
    aadhaar: str = Field(..., description="Aadhaar number")

    @field_validator("aadhaar")
    def validate_aadhaar(cls, value:str)->str:
        if not value:
            raise ValueError("Aadhaar cannot be empty")
        if not value.isdigit() or len(value) != 12:
            raise ValueError("Aadhaar must be exactly 12 digits")
        return value


class GenerateAadhaarOtpResponseSchema(BaseModel):
    """Response schema for generating Aadhaar OTP."""
    txnId: str = Field(..., description="Transaction ID")
    mobileNumber: str = Field(..., description="Mobile number")


class VerifyAadhaarOtpRequestSchema(BaseModel):
    """Request schema for verifying Aadhaar OTP."""
    domainName: str = Field(..., description="Domain name")
    idType: str = Field(..., description="ID type")
    otp: str = Field(..., description="OTP")
    restrictions: Optional[str] = Field(None, description="Restrictions (optional)")
    txnId: str = Field(..., description="Transaction ID")

    @field_validator("domainName", "idType", "otp", "txnId")
    def validate_required_field(value: str, info: FieldValidationInfo) -> str:
        """Reusable function to validate required fields."""
        return validate_non_empty(value, info.field_name)

class VerifyAadhaarOtpResponseSchema(BaseModel):
    """Response schema for verifying Aadhaar OTP."""
    txnId: str 
    mobileNumber: Optional[str] = None
    photo: str 
    gender: str
    name: str 
    email: Optional[str] = None
    pincode: str 
    birthDate: Optional[str] = None
    careOf: Optional[str] = None
    house: Optional[str] = None
    street: Optional[str] = None
    landmark: Optional[str] = None
    locality: Optional[str] = None
    villageTownCity: Optional[str] = None
    subDist: Optional[str] = None
    district: str 
    state: str 
    postOffice: Optional[str] = None
    address: str 


class DemographicAuthViaMobileRequestSchema(BaseModel):
    """Request schema for demographic authentication via mobile."""
    txnId: str = Field(..., description="Transaction ID")
    mobileNumber: str = Field(..., description="Mobile number")

    @field_validator("txnId", "mobileNumber")
    def validate_required_fields(cls, value:str)->str:
        if not value or not value.strip():
            raise ValueError("This field cannot be empty")
        return value


class DemographicAuthViaMobileResponseSchema(BaseModel):
    """Response schema for demographic authentication via mobile."""
    verified: bool = Field(..., description="Verification status")


class GenerateMobileOtpRequestSchema(BaseModel):
    """Request schema for generating mobile OTP."""
    mobile: str = Field(..., description="Mobile number")
    txnId: str = Field(..., description="Transaction ID")

    @field_validator("mobile", "txnId")
    def validate_required_fields(cls, value: str,info: FieldValidationInfo) -> str:
        """Ensure the field is not empty."""
        return validate_non_empty(value, info.field_name)


class MobileOtpResponseSchema(BaseModel):
    """Response schema for generating mobile OTP."""
    txnId: str = Field(..., description="Transaction ID")
    mobileNumber: Optional[str] = Field(None, description="Mobile number (always null)")


class VerifyMobileOtpRequestSchema(BaseModel):
    """Request schema for verifying mobile OTP."""
    otp: str = Field(..., description="OTP")
    txnId: str = Field(..., description="Transaction ID")

    @field_validator("otp", "txnId")
    def validate_required_fields(cls, value:str,info: FieldValidationInfo)->str:
        return validate_non_empty(value, info.field_name)

class CheckAccountExistRequestSchema(BaseModel):
    """Request schema for checking account existence."""
    txnId: str
    preverifiedCheck: bool

    @field_validator("txnId")
    def validate_required_fields(cls, value:str)->str:
        if not value:
            raise ValueError("This field cannot be empty")
        return value


class HprAccountResponse (BaseModel):
    """Response schema for checking account existence when HPR ID is present."""
    model_config = ConfigDict(populate_by_name=True,use_enum_values=True, by_alias=True)
    token: str = Field(..., description="token",alias="token") 
    hprIdNumber: str = Field(..., description="hprIdNumber",alias="hprIdNumber") 
    hprId: str = Field(..., description="HPR ID",alias= "hprId")
    categoryId: int = Field(..., description="Category ID",alias="categoryId" ) 
    subCategoryId: int=Field(..., description="Sub-category ID",alias="subCategoryId") 
    new: bool = Field(..., description="new")
    categoryName: str = Field(..., description="Category name",alias= "categoryName")
    categorySubName: str = Field(..., description="Category sub name",alias= "categorySubName")

class NonHprAccountResponse (BaseModel):
    """Response schema for checking account existence when HPR ID is not present."""
    model_config = ConfigDict(populate_by_name=True,use_enum_values=True, by_alias=True)
    txnId: Optional[str] = Field(None, description="Transaction ID")
    token: str = Field(..., description="token",alias="token") 
    hprIdNumber: str = Field(..., description="hprIdNumber",alias="hprIdNumber") 
    name: Optional[str] = Field(None, description="Name",alias="name")
    firstName: Optional[str] = Field(None, description="First name",alias="firstName") 
    lastName: Optional[str] = Field(None, description="last name",alias="lastName") 
    middleName: Optional[str] = Field(None, description="Middle name",alias="middleName") 
    gender: Optional[str] = Field(None, description="Gender")
    yearOfBirth: Optional[str] = Field(None, description="year of birth",alias="yearOfBirth")
    monthOfBirth: Optional[str] = Field(None, description="month of birth",alias="monthOfBirth")
    dayOfBirth: Optional[str] = Field(None, description="Day of birth",alias="dayOfBirth") 
    districtCode: Optional[str] = Field(None, description="Disrict Code",alias="districtCode")
    stateCode: Optional[str] = Field(None, description="state Code",alias="stateCode")
    stateName: Optional[str] = Field(None, description="State Name",alias="stateName")
    districtName: Optional[str] = Field(None, description="District Name",alias="districtName")
    address: Optional[str] = Field(None, description="Address")
    pincode: Optional[str] = Field(None, description="Pincode")
    profilePhoto: Optional[str] = Field(None, description="Profile photo",alias="profilePhoto")
    categoryId: int = Field(..., description="Category ID",alias="categoryId" ) 
    subCategoryId: int=Field(..., description="Sub-category ID",alias="subCategoryId") 
    new: bool = Field(..., description="new")

class HpIdSuggestionRequestSchema(BaseModel):
    """Request schema for HP ID suggestion."""
    txnId: str = Field(..., description="Transaction ID")

    @field_validator("txnId")
    def validate_txnId(cls, value: str)->str:
        if not value:
            raise ValueError("txnId cannot be empty")
        return value

class CreateHprIdWithPreVerifiedRequestBody(BaseModel):
    """Request body schema for creating HPR ID with pre-verified data."""
    address: str = Field(..., description="Address")
    dayOfBirth: str = Field(..., description="Day of birth")
    districtCode: str = Field(..., description="District code")
    email: str = Field(..., description="Email")
    firstName: str = Field(..., description="First name")
    hpCategoryCode: str = Field(..., description="HP category code")
    hpSubCategoryCode: str = Field(..., description="HP subcategory code")
    hprId: str = Field(..., description="HPR ID")
    lastName: str = Field(..., description="Last name")
    middleName: Optional[str] = Field(None, description="Middle name (optional)")
    monthOfBirth: str = Field(..., description="Month of birth")
    password: str = Field(..., description="Password")
    pincode: str = Field(..., description="Pincode")
    profilePhoto: Optional[str] = Field(None, description="Profile photo (optional)")
    stateCode: str = Field(..., description="State code")
    txnId: str = Field(..., description="Transaction ID")
    yearOfBirth: str = Field(..., description="Year of birth")
    
    @field_validator("address", "dayOfBirth","districtCode", "email", "firstName", "hpCategoryCode", "hpSubCategoryCode", "hprId", "lastName", "monthOfBirth", "password", "pincode", "stateCode", "txnId", "yearOfBirth")
    def check_required_field(cls, value: str, info: FieldValidationInfo) -> str:
        return validate_non_empty(value, info.field_name)
    
    @field_validator("dayOfBirth", "monthOfBirth", "yearOfBirth")
    def check_number_string(value: str, info: FieldValidationInfo) -> str:
        if not value.isdigit():
            raise ValueError(f"{info.field_name} must contain numeric characters only")

        num_value = int(value)
 
        if info.field_name == "dayOfBirth" and not (1 <= num_value <= 31):
            raise ValueError("dayOfBirth must be between 1 and 31")

        if info.field_name == "monthOfBirth" and not (1 <= num_value <= 12):
            raise ValueError("monthOfBirth must be between 1 and 12")

        if info.field_name == "yearOfBirth" and len(value) != 4:
            raise ValueError("yearOfBirth must be exactly 4 digits")

        return value


class CreateHprIdWithPreVerifiedResponseBody(BaseModel):
    """Response body schema for creating HPR ID with pre-verified data."""
    token: str = Field(..., description="Token")
    hprIdNumber: str = Field(..., description="HPR ID number",alias="hprIdNumber")
    name: str = Field(..., description="Name",alias="name")
    gender: str = Field(..., description="Gender",alias="gender")
    yearOfBirth: str = Field(..., description="Year of birth",alias= "yearOfBirth")
    monthOfBirth: str = Field(..., description="Month of birth",alias= "monthOfBirth")
    dayOfBirth: str = Field(..., description="Day of birth",alias= "dayOfBirth")
    firstName: str = Field(..., description="First name",alias= "firstName")
    hprId: str = Field(..., description="HPR ID",alias= "hprId")
    lastName: str = Field(..., description="Last name",alias= "lastName")
    middleName: Optional[str] = Field(None, description="Middle name",alias= "middleName")
    stateCode: str = Field(..., description="State code",alias= "stateCode")
    districtCode: Optional[str] = Field(None, description="District code",alias= "districtCode")
    stateName: str = Field(..., description="State name",alias= "stateName")
    districtName: Optional[str] = Field(None, description="District name",alias="districtName")
    email: Optional[str] = Field(None, description="Email",alias= "email")
    kycPhoto: str = Field(..., description="KYC photo",alias= "kycPhoto")
    mobile: str = Field(..., description="Mobile number",alias= "mobile")
    categoryId: int = Field(..., description="Category ID",alias= "categoryId")
    subCategoryId: int = Field(..., description="Subcategory ID",alias="subCategoryId")
    authMethods: list[str] = Field(..., description="Authentication methods",alias= "authMethods")
    new: bool = Field(..., description="New flag",alias= "new")
