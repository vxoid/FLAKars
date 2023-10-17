from abc import ABC, abstractmethod

class Router(ABC):
  @abstractmethod
  def __str__(self) -> str:
    raise NotImplemented()
  
  @abstractmethod
  def get_name(self) -> str:
    raise NotImplemented()

  @abstractmethod
  def get_arbitrage_address(self) -> str:
    raise NotImplemented()
  
  @abstractmethod
  def get_convert_address(self) -> str:
    raise NotImplemented()