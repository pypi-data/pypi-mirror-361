from nexa_sdk.utils import dataclass_to_dict
from dataclasses import dataclass

@dataclass
class Dummy:
    a: int
    b: int = None
    c: int = 3

def test_dataclass_to_dict():
    d = Dummy(1)
    result = dataclass_to_dict(d)
    assert result == {"a": 1, "c": 3} 