from contract.functions import *
from contract.pair import Pair
from web3.contract.contract import Contract
from web3 import Web3
    
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

    def estimate(self, amount: int) -> int:
        amount1 = self.pair1.convert(amount)
        amount2 = self.pair2.convert(amount1)

        return amount2
    
    def arbitrage(self, amount: int):
        return dualDexArbitrage(
            self.web3,
            self.contract,
            self.account,
            self.pair1.router.get_address(),
            self.pair2.router.get_address(),
            self.pair1.token1.get_address(),
            self.pair2.token1.get_address(),
            amount
        )
    
    def estimateGasFlashArbitrage(self, amount: int) -> int:
        return estimateGasFlDualArbitrage(
            self.contract,
            self.account.address,
            self.pair1.router.get_address(),
            self.pair2.router.get_address(),
            self.pair1.token1.get_address(),
            self.pair2.token1.get_address(),
            amount
        )
    
    def flashArbitrage(self, amount: int):
        return flDualArbitrage(
            self.web3,
            self.contract,
            self.account,
            self.pair1.router.get_address(),
            self.pair2.router.get_address(),
            self.pair1.token1.get_address(),
            self.pair2.token1.get_address(),
            amount
        )
    
    def __str__(self) -> str:
        return f"{self.pair1} <-> {self.pair2}"

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

    def estimate(self, amount: int) -> int:
        amount1 = self.pair1.convert(amount)
        amount2 = self.pair2.convert(amount1)
        amount3 = self.pair3.convert(amount2)

        return amount3
    
    def arbitrage(self, amount: int):
        return tribDexArbitrage(
            self.web3,
            self.contract,
            self.account,
            self.pair1.router.get_address(),
            self.pair2.router.get_address(),
            self.pair3.router.get_address(),
            self.pair1.token1.get_address(),
            self.pair2.token1.get_address(),
            self.pair3.token1.get_address(),
            amount
        )
    
    def estimateGasFlashArbitrage(self, amount: int) -> int:
        return estimateGasFlTribArbitrage(
            self.contract,
            self.account.address,
            self.pair1.router.get_address(),
            self.pair2.router.get_address(),
            self.pair3.router.get_address(),
            self.pair1.token1.get_address(),
            self.pair2.token1.get_address(),
            self.pair3.token1.get_address(),
            amount
        )
    
    def flashArbitrage(self, amount: int):
        return flTribArbitrage(
            self.web3,
            self.contract,
            self.account,
            self.pair1.router.get_address(),
            self.pair2.router.get_address(),
            self.pair3.router.get_address(),
            self.pair1.token1.get_address(),
            self.pair2.token1,
            self.pair3.token1.get_address(),
            amount
        )
    
    def __str__(self) -> str:
        return f"{self.pair1} -> {self.pair2} -> {self.pair3}"