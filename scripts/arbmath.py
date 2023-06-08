from arbitrage import *
from consts import *
from typing import Tuple

def estimateGasAndAmount(web3: Web3, arbitrage: DualArbitrage | TribArbitrage, eth_pair: Pair, gas_mult: float) -> Tuple[int, int, int, str]:
    eth_gas_estimate = int(ESTIMATE_GAS_ETH*1e18)
    token1_gas_estimate = eth_pair.convert(eth_gas_estimate) if eth_pair.token1 != arbitrage.pair1.token1 else eth_gas_estimate

    estimated_gas = 0
    try:
        estimated_gas = arbitrage.estimateGasFlashArbitrage(token1_gas_estimate)
    except Exception as e:
        return 0, 0, 0, e
    
    amount_eth = int(web3.eth.gas_price*estimated_gas)
    amount_token1 = eth_pair.convert(amount_eth) if eth_pair.token1 != arbitrage.pair1.token1 else amount_eth
    amount = int(amount_token1*gas_mult)

    estimated_amount = 0
    try:
        estimated_amount = arbitrage.estimate(amount)
    except Exception as e:
        return 0, 0, 0, e
    
    income = estimated_amount - amount
    if income < amount_token1:
        return 0, 0, 0, f"Income does not cover costs ({amount_token1}/{income})"
    
    return amount, estimated_amount, estimated_gas, None