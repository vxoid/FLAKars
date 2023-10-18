from attrs import define, field
from .router import Router

@define(kw_only=True)
class UniswapRouterV2(Router):
  name: str = field()
  address: str = field()

  def __str__(self) -> str:
    return f"{self.address} ({self.name})"
  
  def get_name(self) -> str:
    return self.name
  
  def get_arbitrage_address(self) -> str:
    return self.address
  
  def get_available_address(self) -> str:
    return self.address

  def get_convert_address(self) -> str:
    return self.address