from attrs import define, field
from .router import Router
from .token import Token

@define(kw_only=True)
class Pair:
  router: Router = field()
  token_in: Token = field()
  token_out: Token = field()

  def __str__(self) -> str:
    return f"{self.token_in.name} -> {self.token_out.name} on {self.router.get_name()}"