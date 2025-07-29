import pytest
from unittest.mock import MagicMock
from nexa_sdk.calls import CallAPI, Call, CreateCallDto, UpdateCallDto, FilterCallsDto

class DummyClient:
    def request(self, method, path, **kwargs):
        call_data = {
            "id": 1,
            "campaign_id": 1,
            "organisation_phone_number_id": 1,
            "campaign_lead_id": 1,
            "called_time": None,
            "duration": None,
            "type": None,
            "latency": None,
            "status": "done",
            "sentiment": "good",
            "summary": None,
            "transcript": None,
            "json_output": None,
            "recording_url": None,
            "is_deleted": False,
            "sensitive_delete": False,
            "createdAt": "now",
            "updatedAt": "now"
        }
        if method == "GET" and path.startswith("/call-logs/"):
            return call_data
        if method == "GET" and path == "/call-logs":
            return {"callLogs": [call_data], "total": 1, "page": 1, "limit": 10, "totalPages": 1}
        if method == "POST" and path == "/call-logs":
            return call_data
        if method == "PATCH":
            return call_data
        if method == "POST" and path == "/call-logs/initiate":
            return call_data
        return {}

def test_create_call():
    api = CallAPI(DummyClient())
    dto = CreateCallDto(1, 1, 1, "done")
    call = api.create_call(dto, "org1")
    assert isinstance(call, Call)

def test_get_call():
    api = CallAPI(DummyClient())
    call = api.get_call(1)
    assert isinstance(call, Call)

def test_list_calls():
    api = CallAPI(DummyClient())
    result = api.list_calls("org1")
    assert "callLogs" in result
    assert isinstance(result["callLogs"][0], Call)

def test_update_call():
    api = CallAPI(DummyClient())
    dto = UpdateCallDto()
    call = api.update_call(1, dto, "org1")
    assert isinstance(call, Call)

def test_initiate_call():
    api = CallAPI(DummyClient())
    call = api.initiate_call(1, 1, 1)
    assert isinstance(call, Call)

def test_filter_calls_dto_to_query_from_renaming():
    dto = FilterCallsDto(from_="2024-01-01")
    query = dto.to_query()
    assert "from" in query
    assert "from_" not in query
    assert query["from"] == "2024-01-01" 