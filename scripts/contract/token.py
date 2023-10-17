from attrs import define, field

@define(kw_only=True)
class Token:
  name: str = field()
  address: str = field()