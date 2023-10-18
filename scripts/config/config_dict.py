from .errors import NotFoundConfigElementError
from attrs import define, field
from .safe_dict import SafeDict
from typing import Dict

@define
class ConfigDict(SafeDict):
  dict: Dict = field()

  def get(self, key: str):
    value = self.dict.get(key)

    if value is None:
      raise NotFoundConfigElementError(self.dict, key)

    return value
  
  def includes_key(self, key: str) -> bool:
    return key in self.dict