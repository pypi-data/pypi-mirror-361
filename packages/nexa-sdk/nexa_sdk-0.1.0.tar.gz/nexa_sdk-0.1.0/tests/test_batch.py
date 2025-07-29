import pytest
from unittest.mock import MagicMock
from nexa_sdk.batch import BatchAPI, BatchCall, CreateBatchCallDto, BatchCallRecipient

class DummyClient:
    def request(self, method, path, **kwargs):
        return {"id": 1, "campaign_id": 1, "agent_id": 1, "status": "done", "createdAt": "now", "updatedAt": "now"}

def test_create_batch_call():
    api = BatchAPI(DummyClient())
    recipient = BatchCallRecipient(recipient_phone_number="1234567890")
    dto = CreateBatchCallDto(campaign_id=1, agent_id=1, calls=[recipient])
    batch = api.create_batch_call(dto)
    assert isinstance(batch, BatchCall) 