import pytest
from unittest.mock import MagicMock
from nexa_sdk.system import SystemAPI, Language, Llm, SystemVoice

class DummyClient:
    def request(self, method, path):
        if path == "/languages":
            return [{"id": 1, "name": "English", "code": "en"}]
        if path == "/llms":
            return [{"id": 1, "name": "GPT", "icon": None, "provider_id": "p1", "provider": "OpenAI", "createdAt": "now", "updatedAt": "now"}]
        if path == "/voices":
            return {"voices": [{"id": 1, "name": "Voice1", "gender": "male", "provider_name": None, "provider_voice_id": None, "icon": None, "recording": None, "accent": None, "age_group": None}]}
        return []

def test_list_languages():
    api = SystemAPI(DummyClient())
    langs = api.list_languages()
    assert isinstance(langs[0], Language)
    assert langs[0].name == "English"

def test_list_llms():
    api = SystemAPI(DummyClient())
    llms = api.list_llms()
    assert isinstance(llms[0], Llm)
    assert llms[0].name == "GPT"

def test_list_voices():
    api = SystemAPI(DummyClient())
    voices = api.list_voices()
    assert isinstance(voices[0], SystemVoice)
    assert voices[0].name == "Voice1" 