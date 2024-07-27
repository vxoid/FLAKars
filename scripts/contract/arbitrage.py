from attrs import define, field
from .pair import Pair

@define(kw_only=True)
class Arbitrage:
  weth_pair: Pair = field()
  pair_in: Pair = field()
  pair_out: Pair = field()
  amount: int = field()
  min_income: int = field()

  def __str__(self) -> str:
    return f"{self.amount} {self.pair_in.token_in.name} ({self.pair_in.router.get_name()}) <-> {self.pair_out.token_in.name} ({self.pair_out.router.get_name()})"