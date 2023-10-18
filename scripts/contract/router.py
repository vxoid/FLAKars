from abc import ABC, abstractmethod

class Router(ABC):
  @abstractmethod
  def __str__(self) -> str:
    raise NotImplementedError()
  
  @abstractmethod
  def get_name(self) -> str:
    raise NotImplementedError()

  @abstractmethod
  def get_arbitrage_address(self) -> str:
    raise NotImplementedError()
  
  @abstractmethod
  def get_available_address(self) -> str:
    raise NotImplementedError()
  
  @abstractmethod
  def get_convert_address(self) -> str:
    raise NotImplementedError()