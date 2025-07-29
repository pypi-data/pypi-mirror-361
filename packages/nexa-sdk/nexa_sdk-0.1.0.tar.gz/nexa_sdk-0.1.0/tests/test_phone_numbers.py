import pytest
from unittest.mock import MagicMock
from nexa_sdk.phone_numbers import PhoneNumberAPI, OrganizationPhoneNumber, CreateOrganizationPhoneNumberDto, UpdateOrganizationPhoneNumberDto, PlivoPhoneNumbersResponseDto, BasePhoneNumberDto, TwilioPhoneNumbersResponseDto, PurchasePhoneNumberRequestDto, PurchasePhoneNumberResponseDto, GetProviderPhoneNumbersRequestDto, GetProviderPhoneNumbersResponseDto

org_phone_number_dict = {"id": 1, "country_code": 1, "phone_number": 123, "telephony_provider_id": 1}
plivo_numbers_dict = {"api_id": "id", "objects": [], "meta": {}}

def valid_provider_numbers_response():
    return {
        "telephonyProviderId": 1,
        "providerName": "Test",
        "data": plivo_numbers_dict
    }

class DummyClient:
    def request(self, method, path, **kwargs):
        if method == "POST" and path == "/organization-phone-numbers":
            return org_phone_number_dict
        if method == "PATCH":
            return org_phone_number_dict
        if method == "DELETE":
            return None
        if path == "/organization-phone-numbers":
            return [org_phone_number_dict]
        if path.startswith("/organization-phone-numbers/") and method == "GET":
            parts = path.split("/")
            if len(parts) == 3 and parts[-1].isdigit():
                return org_phone_number_dict
        if path == "/organization-phone-numbers/plivo-numbers":
            return plivo_numbers_dict
        if path == "/organization-phone-numbers/plivo-purchase":
            return {"phoneNumber": "123", "status": "ok", "message": "done"}
        if path == "/organization-phone-numbers/twilio-numbers":
            return {"available_phone_numbers": [], "uri": "uri"}
        if path == "/organization-phone-numbers/purchase":
            return {"phoneNumber": "123", "organizationPhoneNumber": org_phone_number_dict}
        if path == "/organization-phone-numbers/provider-numbers":
            return valid_provider_numbers_response()
        return {}

def test_list_organization_phone_numbers():
    api = PhoneNumberAPI(DummyClient())
    numbers = api.list_organization_phone_numbers("org1")
    assert isinstance(numbers[0], OrganizationPhoneNumber)

def test_get_organization_phone_number():
    api = PhoneNumberAPI(DummyClient())
    number = api.get_organization_phone_number(1, "org1")
    assert isinstance(number, OrganizationPhoneNumber)

def test_create_organization_phone_number():
    api = PhoneNumberAPI(DummyClient())
    dto = CreateOrganizationPhoneNumberDto(1, 123, 1)
    number = api.create_organization_phone_number(dto, "org1")
    assert isinstance(number, OrganizationPhoneNumber)

def test_update_organization_phone_number():
    api = PhoneNumberAPI(DummyClient())
    dto = UpdateOrganizationPhoneNumberDto(country_code=1)
    number = api.update_organization_phone_number(1, dto, "org1")
    assert isinstance(number, OrganizationPhoneNumber)

def test_delete_organization_phone_number():
    api = PhoneNumberAPI(DummyClient())
    assert api.delete_organization_phone_number(1, "org1") is None

def test_get_plivo_numbers():
    api = PhoneNumberAPI(DummyClient())
    resp = api.get_plivo_numbers("IN")
    assert isinstance(resp, PlivoPhoneNumbersResponseDto)

def test_purchase_plivo_number():
    api = PhoneNumberAPI(DummyClient())
    resp = api.purchase_plivo_number("123")
    assert isinstance(resp, BasePhoneNumberDto)

def test_get_twilio_numbers():
    api = PhoneNumberAPI(DummyClient())
    resp = api.get_twilio_numbers("IN")
    assert isinstance(resp, TwilioPhoneNumbersResponseDto)

def test_purchase_phone_number():
    api = PhoneNumberAPI(DummyClient())
    dto = PurchasePhoneNumberRequestDto(phoneNumber="123", telephonyProviderId=1, countryISO="IN")
    resp = api.purchase_phone_number(dto, "org1")
    assert isinstance(resp, PurchasePhoneNumberResponseDto)
    assert isinstance(resp.organizationPhoneNumber, OrganizationPhoneNumber)

def test_get_provider_phone_numbers():
    api = PhoneNumberAPI(DummyClient())
    dto = GetProviderPhoneNumbersRequestDto(countryIso="IN", telephonyProviderId=1)
    resp = api.get_provider_phone_numbers(dto)
    assert isinstance(resp, GetProviderPhoneNumbersResponseDto)
    assert isinstance(resp.data, PlivoPhoneNumbersResponseDto)

def test_get_plivo_numbers_with_type():
    class PlivoTypeClient(DummyClient):
        def request(self, method, path, **kwargs):
            assert kwargs["params"]["type"] == "local"
            return plivo_numbers_dict
    api = PhoneNumberAPI(PlivoTypeClient())
    resp = api.get_plivo_numbers("IN", type_="local")
    assert isinstance(resp, PlivoPhoneNumbersResponseDto)

def test_get_twilio_numbers_with_number_type():
    class TwilioTypeClient(DummyClient):
        def request(self, method, path, **kwargs):
            assert kwargs["params"]["number_type"] == "mobile"
            return {"available_phone_numbers": [], "uri": "uri"}
    api = PhoneNumberAPI(TwilioTypeClient())
    resp = api.get_twilio_numbers("IN", number_type="mobile")
    assert isinstance(resp, TwilioPhoneNumbersResponseDto)

def test_get_provider_phone_numbers_twilio():
    class TwilioProviderClient(DummyClient):
        def request(self, method, path, **kwargs):
            return {
                "telephonyProviderId": 1,
                "providerName": "Test",
                "data": {"available_phone_numbers": [], "uri": "uri"}
            }
    api = PhoneNumberAPI(TwilioProviderClient())
    dto = GetProviderPhoneNumbersRequestDto(countryIso="IN", telephonyProviderId=1)
    resp = api.get_provider_phone_numbers(dto)
    assert isinstance(resp.data, TwilioPhoneNumbersResponseDto) 