from contract.functions import *
from arbitrage import *
from typing import *
from consts import *
import json
import sys

COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"

def usage(args):
    space = " "*len(args[0])
    print("USAGE: ")
    print(f"{args[0]} config.json 0x2B9F1873d99B3C6322b34e978699c7313C348d30")
    print(f"{space  } ^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(f"{space  } path to configuration file            contract address")

if len(sys.argv) < 3:
    usage(sys.argv)
    sys.exit(-1)

def get_most_profitable(web3: Web3, contract, account, fl, tokens, routers) -> List[Tuple[Arbitrage, Pair]]:
    eth_token = get_addr_by_sym(WETH)
    arbitrages = []
    for fl_token in fl:
        for token2 in tokens:
            for token3 in tokens:
                if fl_token == token2 and token2 == token3:
                    continue
                
                for router1, estim1, avail1 in routers:
                    pair1 = Pair(contract, account.address, router1, fl_token, token2, estim=estim1, avail=avail1)
                    eth_pair = Pair(contract, account.address, router1, eth_token, fl_token, estim=estim1, avail=avail1)
                    if fl_token != eth_token and not eth_pair.available():
                        print(
                            COLOR_YELLOW +
                            f"{WETH} -> "
                            + f"{get_sym_by_addr(fl_token)} does not exists on {get_dex_by_addr(router1)}"
                            + COLOR_RESET
                        )
                        continue

                    if fl_token != token2 and not pair1.available():
                        print(
                            COLOR_YELLOW +
                            f"{get_sym_by_addr(fl_token)} -> "
                            + f"{get_sym_by_addr(token2)} does not exists on {get_dex_by_addr(router1)}"
                            + COLOR_RESET
                        )
                        continue

                    for router2, estim2, avail2 in routers:
                        pair2 = Pair(contract, account.address, router2, token2, token3, estim=estim2, avail=avail2)

                        if token2 != token3 and not pair2.available():
                            print(
                                COLOR_YELLOW +
                                f"{get_sym_by_addr(token2)} -> "
                                + f"{get_sym_by_addr(token3)} does not exists on {get_dex_by_addr(router2)}"
                                + COLOR_RESET
                            )
                            continue

                        for router3, estim3, avail3 in routers:
                            pair3 = Pair(contract, account.address, router3, token3, fl_token, estim=estim3, avail=avail3)
                            
                            if token3 != fl_token and not pair3.available():
                                print(
                                    COLOR_YELLOW +
                                    f"{get_sym_by_addr(token3)} -> "
                                    + f"{get_sym_by_addr(fl_token)} does not exists on {get_dex_by_addr(router3)}"
                                    + COLOR_RESET
                                )
                                continue

                            arbitrage = Arbitrage(
                                web3,
                                contract,
                                account,
                                pair1,
                                pair2,
                                pair3
                            )

                            estimated_gas = 0
                            try:
                                eth = int(ESTIMATE_GAS_ETH*1e18)
                                token1_amount = eth_pair.convert(eth) if fl_token != eth_token else eth
                                estimated_gas = arbitrage.estimateGasFlashArbitrage(token1_amount)
                            except Exception as e:
                                print(
                                    COLOR_RED +
                                    f"{arbitrage.debug(get_sym_by_addr, get_dex_by_addr)} flarbitrage gas estimation failed with {e}"
                                    + COLOR_RESET
                                )
                                continue

                            estimated_amount = 0
                            token1_gas = 0
                            amount = 0
                            try:
                                eth = int((web3.eth.gas_price*GAS)*estimated_gas)
                                print(f"estimated gas fees - {eth/1e18}")

                                token1_gas = eth_pair.convert(eth) if fl_token != eth_token else eth
                                amount = int(token1_gas*FLA_GAS)

                                estimated_amount = arbitrage.estimate(amount)

                                income = estimated_amount - amount

                                if income <= token1_gas:
                                    print(
                                        COLOR_YELLOW +
                                        f"income {income} - {amount+token1_gas}/{estimated_amount}({estimated_amount/(amount+token1_gas)}) {arbitrage.debug(get_sym_by_addr, get_dex_by_addr)} won\'t be profitable"
                                        + COLOR_RESET
                                    )
                                    continue
                            except Exception as e:
                                print(
                                    COLOR_RED +
                                    f"{arbitrage.debug(get_sym_by_addr, get_dex_by_addr)} estimation failed with {e}"
                                    + COLOR_RESET
                                )
                                continue

                            print(f"found {amount}/{estimated_amount}({estimated_amount/amount}) {arbitrage.debug(get_sym_by_addr, get_dex_by_addr)}")

                            try:
                                arbitrage.flashArbitrage(amount, gas_limit=estimated_gas)
                            except Exception as e:
                                print(COLOR_RED + f"arbitrage failed with {e}" + COLOR_RESET)
                            else:
                                print(f"✅💹 Succesfully arbitraged {arbitrage.debug(get_sym_by_addr, get_dex_by_addr)}")

                                print("-------------------------------------------------------")
                            arbitrages.append((arbitrage, eth_pair))
                                       
    return arbitrages

with open(sys.argv[1], "r") as file:
    config = json.loads(file.read())
    fl = config["fl"]
    node = config["node"]
    build = config["build"]
    tokens = config["tokens"]
    routers = config["routers"]
    private_key = config["private_key"]

dex_by_addr = { router["address"]: router["dex"] for router in routers }
get_dex_by_addr = lambda addr: dex_by_addr[addr]

sym_by_addr = { token["address"]: token["symbol"] for token in tokens }
addr_by_sym = { token["symbol"]: token["address"] for token in tokens }
get_sym_by_addr = lambda addr: sym_by_addr[addr]
get_addr_by_sym = lambda sym: addr_by_sym[sym]

with open(f"{build}.abi", "r") as file:
    abi = json.loads(file.read().strip())

web3 = Web3(Web3.HTTPProvider(node))

contract = web3.eth.contract(address=Web3.to_checksum_address(sys.argv[2]), abi=abi)
account = web3.eth.account.from_key(private_key)
eth_token = get_addr_by_sym(WETH)

while True:
    print("Fetching prices...")
    arbitrages = get_most_profitable(
        web3,
        contract,
        account,
        [get_addr_by_sym(fl_token["symbol"]) for fl_token in fl],
        [token["address"] for token in tokens],
        [(router["address"], router["estim"] if "estim" in router else None, router["avail"] if "avail" in router else None) for router in routers]
    )

    # arbitraging
    while len(arbitrages) != 0:
        i = 0
        while i<len(arbitrages):
            arbitrage = arbitrages[i][0]
            eth_pair = arbitrages[i][1]

            estimated_gas = 0
            token1_gas = 0
            amount = 0
            try:
                eth = int(ESTIMATE_GAS_ETH*1e18)
                token1_amount = int(eth_pair.convert(eth) if arbitrage.pair1.token1 != eth_pair.token1 else eth)
                estimated_gas = arbitrage.estimateGasFlashArbitrage(token1_amount)

                eth = int((web3.eth.gas_price*GAS)*estimated_gas)
                token1_gas = eth_pair.convert(eth) if arbitrage.pair1.token1 != eth_pair.token1 else eth
                amount = int(token1_gas*FLA_GAS)

                arbitrage.estimateGasFlashArbitrage(amount)
            except Exception as e:
                print(
                    COLOR_RED +
                    f"removing {arbitrage.debug(get_sym_by_addr, get_dex_by_addr)} due to flarbitrage gas estimation failed with {e}"
                    + COLOR_RESET
                )
                continue

            amount = 0
            estimated_amount = 0
            try:
                estimated_amount = arbitrage.estimate(amount)

                income = estimated_amount - amount
                if income <= token1_gas:
                    print(COLOR_RED + f"removing {amount}/{estimated_amount}({estimated_amount/amount}) {arbitrage.debug(get_sym_by_addr, get_dex_by_addr)}" + COLOR_RESET)
                    arbitrages.pop(i)
                    continue
            except Exception as e:
                print(
                    COLOR_RED +
                    f"removing {arbitrage.debug(get_sym_by_addr, get_dex_by_addr)} estimation failed with {e}"
                    + COLOR_RESET
                )
                arbitrages.pop(i)
                continue

            print(
                f"found {amount}/{estimated_amount}({estimated_amount/amount}) {arbitrage.debug(get_sym_by_addr, get_dex_by_addr)}"
            )

            try:
                arbitrage.flashArbitrage(amount, gas_limit=estimated_gas)
            except Exception as e:
                print(COLOR_RED + f"arbitrage failed with {e}" + COLOR_RESET)
            else:
                print(
                    f"✅💹 Succesfully arbitraged {arbitrage.debug(get_sym_by_addr, get_dex_by_addr)}"
                )

                print("-------------------------------------------------------")

            i += 1