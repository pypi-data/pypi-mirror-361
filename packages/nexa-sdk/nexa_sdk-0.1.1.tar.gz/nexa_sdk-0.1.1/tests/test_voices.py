import pytest
from unittest.mock import MagicMock
from nexa_sdk.voices import VoiceAPI, Voice, CreateVoiceDto, UpdateVoiceDto, FilterVoicesDto

voice_data = {
    "id": 1,
    "name": "Voice1",
    "gender": "male",
    "provider_name": None,
    "provider_voice_id": None,
    "icon": None,
    "recording": None,
    "accent": None,
    "age_group": None,
    "created_at": None,
    "updated_at": None,
}

class DummyClient:
    def request(self, method, path, **kwargs):
        if path == "/voices/accents":
            return {"items": ["US", "UK"]}
        if path == "/voices" and method == "GET":
            return {"voices": [voice_data], "total": 1, "page": 1, "limit": 10, "totalPages": 1}
        if path.startswith("/voices/") and method == "GET":
            return voice_data
        if path == "/voices" and method == "POST":
            return voice_data
        if path.startswith("/voices/") and method == "PATCH":
            return voice_data
        if path.startswith("/voices/") and method == "DELETE":
            return None
        return {}

def test_list_voices():
    api = VoiceAPI(DummyClient())
    result = api.list_voices()
    assert hasattr(result, "voices")
    assert isinstance(result.voices[0], Voice)

def test_get_voice():
    api = VoiceAPI(DummyClient())
    voice = api.get_voice(1)
    assert isinstance(voice, Voice)

def test_create_voice():
    api = VoiceAPI(DummyClient())
    dto = CreateVoiceDto(name="Voice1", gender="male")
    voice = api.create_voice(dto)
    assert isinstance(voice, Voice)

def test_update_voice():
    api = VoiceAPI(DummyClient())
    dto = UpdateVoiceDto(name="Voice1")
    voice = api.update_voice(1, dto)
    assert isinstance(voice, Voice)

def test_delete_voice():
    api = VoiceAPI(DummyClient())
    assert api.delete_voice(1) is None

def test_get_accents():
    api = VoiceAPI(DummyClient())
    accents = api.get_accents()
    assert "US" in accents

def test_get_accents_items_key():
    class ItemsClient:
        def request(self, method, path, **kwargs):
            return {"items": ["US", "UK"]}
    api = VoiceAPI(ItemsClient())
    accents = api.get_accents()
    assert "US" in accents

def test_filter_voices_dto_to_query():
    dto = FilterVoicesDto(provider_name="test", accent="US", gender="male", name="TestName", page="1", limit="10")
    query = dto.to_query()
    assert query["provider_name"] == "test"
    assert query["accent"] == "US"
    assert query["gender"] == "male"
    assert query["name"] == "TestName"
    assert query["page"] == "1"
    assert query["limit"] == "10" 