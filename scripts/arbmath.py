from arbitrage import *
from consts import *
from typing import Tuple

def estimateGasAndAmount(web3: Web3, arbitrage: DualArbitrage | TribArbitrage, eth_pair: Pair) -> Tuple[int, int, int, bool, str]:
    estimated_gas = 0
    try:
        eth = int(ESTIMATE_GAS_ETH*1e18)
        token1_amount = eth_pair.convert(eth) if arbitrage.pair1.token1 != eth_pair.token1 else eth
        estimated_gas = arbitrage.estimateGasFlashArbitrage(token1_amount)
    except Exception as e:
        return 0, 0, 0, False, f"arbitrage estimation error - {e}"
    
    estimated_amount = 0
    token1_gas = 0
    amount = 0
    try:
        eth = int(ESTIMATE_GAS_ETH*1e18)

        token1_gas = eth_pair.convert(eth) if arbitrage.pair1.token1 != eth_pair.token1 else eth
        amount = int(token1_gas*FLA_GAS)

        estimated_amount = arbitrage.estimate(amount)

        income = estimated_amount - amount

        if income <= token1_gas:
            message = f"won\'t be profitable {income} - {amount+token1_gas}/{estimated_amount}({estimated_amount/(amount+token1_gas)})"
            return 0, 0, 0, False, message
    except Exception as e:
        return 0, 0, 0, False, f"estimation error - {e}"

    return amount, estimated_amount, estimated_gas, True, ""