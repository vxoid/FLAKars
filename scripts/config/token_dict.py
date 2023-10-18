from .errors import NotFoundTokenElementError
from attrs import define, field
from .safe_dict import SafeDict
from typing import Dict

@define
class TokenDict(SafeDict):
  dict: Dict = field()

  def get(self, key: str):
    value = self.dict.get(key)

    if value is None:
      raise NotFoundTokenElementError(self.dict, key)

    return value
  
  def includes_key(self, key: str) -> bool:
    return key in self.dict