from .errors import NotFoundRouterElementError
from attrs import define, field
from .safe_dict import SafeDict
from typing import Dict

@define
class RouterDict(SafeDict):
  dict: Dict = field()

  def get(self, key: str):
    value = self.dict.get(key)

    if value is None:
      raise NotFoundRouterElementError(self.dict, key)

    return value
  
  def includes_key(self, key: str) -> bool:
    return key in self.dict
  
  def is_v2(self) -> bool:
    return not self.is_v3()

  def is_v3(self) -> bool:
    return self.includes_key("quoter") and self.includes_key("factory")