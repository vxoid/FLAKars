from contract.functions import *
from web3.contract.contract import Contract
from web3 import Web3

class Pair:
    def __init__(self, contract: Contract, pk, router: str, token1: str, token2: str, estim: str=None, avail: str=None):
        self.contract = contract
        self.pk = pk
        self.router = router
        self.token1 = token1
        self.token2 = token2
        self.estim = estim
        self.avail = avail

    def available(self) -> bool:
        return available(
            self.contract,
            self.pk,
            self.avail if self.avail else self.router,
            self.token1,
            self.token2
        )
    
    def convert(self, amount):
        return convert(
            self.contract,
            self.pk,
            self.estim if self.estim else self.router,
            self.token1,
            self.token2,
            amount
        )
    
    def debug_first(self, get_sym_by_addr, get_dex_by_addr):
        return f"{get_sym_by_addr(self.token1)}({get_dex_by_addr(self.router)})"
    
    def debug(self, get_sym_by_addr, get_dex_by_addr):
        return f"{get_dex_by_addr(self.router)} {get_sym_by_addr(self.token1)} -> {get_sym_by_addr(self.token2)}"
    
class DualArbitrage:
    def __init__(
            self,
            web3: Web3,
            contract: Contract,
            account,
            pair1: Pair,
            pair2: Pair
        ):
        self.web3 = web3
        self.contract = contract
        self.account = account
        self.pair1 = pair1
        self.pair2 = pair2

    def estimate(self, amount):
        amount1 = self.pair1.convert(amount)
        amount2 = self.pair2.convert(amount1)

        return amount2
    
    def arbitrage(self, amount):
        return dualDexArbitrage(
            self.web3,
            self.contract,
            self.account,
            self.pair1.router,
            self.pair2.router,
            self.pair1.token1,
            self.pair2.token1,
            amount
        )
    
    def estimateGasFlashArbitrage(self, amount):
        return estimateGasFlDualArbitrage(
            self.contract,
            self.account.address,
            self.pair1.router,
            self.pair2.router,
            self.pair1.token1,
            self.pair2.token1,
            amount
        )
    
    def flashArbitrage(self, amount):
        return flDualArbitrage(
            self.web3,
            self.contract,
            self.account,
            self.pair1.router,
            self.pair2.router,
            self.pair1.token1,
            self.pair2.token1,
            amount
        )
    
    def debug(self, get_sym_by_addr, get_dex_by_addr):
        result = f"{self.pair1.debug_first(get_sym_by_addr, get_dex_by_addr)} <-> {self.pair2.debug_first(get_sym_by_addr, get_dex_by_addr)}"
        return result

class TribArbitrage:
    def __init__(
            self,
            web3: Web3,
            contract: Contract,
            account,
            pair1: Pair,
            pair2: Pair,
            pair3: Pair
        ):
        self.web3 = web3
        self.contract = contract
        self.account = account
        self.pair1 = pair1
        self.pair2 = pair2
        self.pair3 = pair3

    def estimate(self, amount):
        amount1 = self.pair1.convert(amount)
        amount2 = self.pair2.convert(amount1)
        amount3 = self.pair3.convert(amount2)

        return amount3
    
    def arbitrage(self, amount):
        return tribDexArbitrage(
            self.web3,
            self.contract,
            self.account,
            self.pair1.router,
            self.pair2.router,
            self.pair3.router,
            self.pair1.token1,
            self.pair2.token1,
            self.pair3.token1,
            amount
        )
    
    def estimateGasFlashArbitrage(self, amount):
        return estimateGasFlTribArbitrage(
            self.contract,
            self.account.address,
            self.pair1.router,
            self.pair2.router,
            self.pair3.router,
            self.pair1.token1,
            self.pair2.token1,
            self.pair3.token1,
            amount
        )
    
    def flashArbitrage(self, amount):
        return flTribArbitrage(
            self.web3,
            self.contract,
            self.account,
            self.pair1.router,
            self.pair2.router,
            self.pair3.router,
            self.pair1.token1,
            self.pair2.token1,
            self.pair3.token1,
            amount
        )
    
    def debug(self, get_sym_by_addr, get_dex_by_addr):
        result = f"{self.pair1.debug_first(get_sym_by_addr, get_dex_by_addr)} -> {self.pair2.debug_first(get_sym_by_addr, get_dex_by_addr)} -> {self.pair3.debug_first(get_sym_by_addr, get_dex_by_addr)}"
        return result