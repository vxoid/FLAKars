from abc import ABC, abstractmethod

class SafeDict(ABC):
  @abstractmethod
  def get(self, key: str):
    raise NotImplementedError()
  
  @abstractmethod
  def includes_key(self, key: str) -> bool:
    raise NotImplementedError()