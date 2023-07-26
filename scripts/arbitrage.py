from contract.etoken import Token
from contract.functions import *
from contract.arbitrage import *
from discord import Interaction
from contract.arbmath import *
from contract.dex import DEX
from load_env import *
from typing import *
import sys

def usage(args):
    space = " "*len(args[0])
    print("USAGE: ")
    print(f"{args[0]} config.json")
    print(f"{space  } ^^^^^^^^^^^")
    print(f"{space  } path to configuration file")

if len(sys.argv) < 2:
    usage(sys.argv)
    sys.exit(-1)

from cli import *
    
with open(abi, "r") as file:
    abi = json.loads(file.read().strip())

web3 = Web3(Web3.HTTPProvider(node))
contract = web3.eth.contract(address=Web3.to_checksum_address(contract_addr), abi=abi)
account = web3.eth.account.from_key(private_key)

async def get_most_profitable_trib(
        fl: List[Token],
        tokens: List[Token],
        routers: List[DEX],
        eth_token: Token,
        eth_router: DEX,
        mult: float,
        on_success,
        *args
    ) -> List[Tuple[TribArbitrage, Pair]]:
    arbitrages = []
    for fl_token in fl:
        eth_pair = Pair(contract, account.address, eth_router, eth_token, fl_token)
        if fl_token != eth_token and not eth_pair.available():
            print(COLOR_YELLOW + f"{eth_pair} does not exists" + COLOR_RESET)
            continue
        
        for token2 in tokens:
            for token3 in tokens:
                if fl_token == token2 and token2 == token3:
                    continue
                
                for router1 in routers:
                    pair1 = Pair(contract, account.address, router1, fl_token, token2)

                    if fl_token != token2 and not pair1.available():
                        print(COLOR_YELLOW + f"{pair1} does not exists" + COLOR_RESET)
                        continue

                    for router2 in routers:
                        pair2 = Pair(contract, account.address, router2, token2, token3)

                        if token2 != token3 and not pair2.available():
                            print(COLOR_YELLOW + f"{pair2} does not exists" + COLOR_RESET)
                            continue

                        for router3 in routers:
                            pair3 = Pair(contract, account.address, router3, token3, fl_token)
                            
                            if token3 != fl_token and not pair3.available():
                                print(COLOR_YELLOW + f"{pair3} does not exists" + COLOR_RESET)
                                continue

                            arbitrage = TribArbitrage(
                                web3,
                                contract,
                                account,
                                pair1,
                                pair2,
                                pair3
                            )
                            amount, estimated_amount, _, error = estimateGasAndAmount(web3, arbitrage, eth_pair, mult)
                            if error is not None:
                                print(COLOR_RED + f"{arbitrage} failed with {error}" + COLOR_RESET)
                                continue

                            print(f"found {amount}/{estimated_amount}({estimated_amount/amount}) {arbitrage}")

                            try:
                                arbitrage.flashArbitrage(amount)
                            except Exception as e:
                                print(COLOR_RED + f"arbitrage failed with {e}" + COLOR_RESET)
                            else:
                                await on_success(arbitrage, amount, estimated_amount, *args)
                            arbitrages.append((arbitrage, eth_pair))
                                       
    return arbitrages

async def get_most_profitable_dual(
        fl: List[Token],
        tokens: List[Token],
        routers: List[DEX],
        eth_token: Token,
        eth_router: DEX,
        mult: float,
        on_success,
        *args
    ) -> List[Tuple[DualArbitrage, Pair]]:
    arbitrages = []
    for fl_token in fl:
        eth_pair = Pair(contract, account.address, eth_router, eth_token, fl_token)
        if fl_token != eth_token and not eth_pair.available():
            print(COLOR_YELLOW + f"{eth_pair} does not exists" + COLOR_RESET)
            continue
        for token2 in tokens:
            if fl_token == token2:
                continue

            for router1 in routers:
                pair1 = Pair(contract, account.address, router1, fl_token, token2)

                if not pair1.available():
                    print(COLOR_YELLOW + f"{pair1} does not exists" + COLOR_RESET)
                    continue

                for router2 in routers:
                    pair2 = Pair(contract, account.address, router2, token2, fl_token)

                    if not pair2.available():
                        print(COLOR_YELLOW + f"{pair2} does not exists" + COLOR_RESET)
                        continue

                    arbitrage = DualArbitrage(
                        web3,
                        contract,
                        account,
                        pair1,
                        pair2
                    )

                    amount, estimated_amount, _, error = estimateGasAndAmount(web3, arbitrage, eth_pair, mult)
                    if error is not None:
                        print(COLOR_RED + f"{arbitrage} failed with {error}" + COLOR_RESET)
                        continue

                    print(f"found {amount}/{estimated_amount}({estimated_amount/amount}) {arbitrage}")

                    try:
                        arbitrage.flashArbitrage(amount)
                    except Exception as e:
                        print(COLOR_RED + f"arbitrage failed with {e}" + COLOR_RESET)
                    else:
                        await on_success(arbitrage, amount, estimated_amount, *args)
                    arbitrages.append((arbitrage, eth_pair))
                                    
    return arbitrages

async def arbitrage_while_profitable(arbitrages: List[Tuple[DualArbitrage | TribArbitrage, Pair]], mult: float, on_success, *args):
    while len(arbitrages) != 0:
        i = 0
        while i<len(arbitrages):
            arbitrage = arbitrages[i][0]
            eth_pair = arbitrages[i][1]

            amount, estimated_amount, _, error = estimateGasAndAmount(web3, arbitrage, eth_pair, mult)
            if error is not None:
                print(
                    COLOR_RED +
                    f"{arbitrage} failed with {error}"
                    + COLOR_RESET
                )
                arbitrages.pop(i)
                continue

            print(f"found {amount}/{estimated_amount}({estimated_amount/amount}) {arbitrage}")

            try:
                arbitrage.flashArbitrage(amount)
            except Exception as e:
                print(COLOR_RED + f"arbitrage failed with {e}" + COLOR_RESET)
            else:
                await on_success(arbitrage, amount, estimated_amount, *args)

            i += 1

async def debug_arbitrage(arbitrage: DualArbitrage | TribArbitrage, amount: int, estimated_amount: int, interaction: Interaction):
    message = f"\
✅ Succesfully arbitraged {amount} to {estimated_amount} ({estimated_amount*100/amount}%) {arbitrage}, income = {estimated_amount-amount} {arbitrage.pair1.token1}"
    await notify(message, interaction)
    print(message)

async def notify(message: str, interaction: Interaction):
    await interaction.channel.send(message)

async def flash_arbitrage(interaction: Interaction, mult: float, dual: bool):
    if dual:
        arbitrages = await get_most_profitable_dual(
            fl,
            tokens,
            routers,
            weth,
            eth_router,
            mult,
            debug_arbitrage,
            interaction
        )
    else:
        arbitrages = await get_most_profitable_trib(
            fl,
            tokens,
            routers,
            weth,
            eth_router,
            mult,
            debug_arbitrage,
            interaction
        )
    if len(arbitrages) == 0:
        message = "No profit made, there is no profitable arbitrages❌."

        await notify(message, interaction)
        print(message)
        print("-"*len(message))
        return
    
    # arbitraging
    await arbitrage_while_profitable(arbitrages, mult, debug_arbitrage, interaction)
    message = "Arbitrages ended✅."

    await notify(message, interaction)
    print(message)
    print("-"*len(message))