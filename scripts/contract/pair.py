from contract.etoken import Token
from contract.dex import DEX
from contract.functions import *

class Pair:
    def __init__(self, contract: Contract, pk, router: DEX, token1: Token, token2: Token):
        self.contract = contract
        self.pk = pk
        self.router = router
        self.token1 = token1
        self.token2 = token2

    def available(self) -> bool:
        return available(
            self.contract,
            self.pk,
            self.router.get_avail(),
            self.token1.get_address(),
            self.token2.get_address()
        )
    
    def convert(self, amount: int) -> int:
        return convert(
            self.contract,
            self.pk,
            self.router.get_estim(),
            self.token1.get_address(),
            self.token2.get_address(),
            amount
        )
    
    def __str__(self) -> str:
        return f"{self.token1} ({self.router})"