from contract.functions import *
from contract.arbitrage import *
from contract.arbmath import *
from typing import *
from consts import *
from discord.ext.commands import Bot
from discord import Intents
import asyncio
import sys

def usage(args):
    space = " "*len(args[0])
    print("USAGE: ")
    print(f"{args[0]} config.json 0x2B9F1873d99B3C6322b34e978699c7313C348d30")
    print(f"{space  } ^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(f"{space  } path to configuration file            contract address")

if len(sys.argv) < 3:
    usage(sys.argv)
    sys.exit(-1)

from cli import *
    
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

async def debug_arbitrage(arbitrage: DualArbitrage | TribArbitrage, amount: int, estimated_amount: int, ctx):
    message = f"✅ Succesfully arbitraged {amount} to {estimated_amount} ({estimated_amount*100/amount}%) {arbitrage}"
    await notify(message, ctx)
    print(message)

with open(abi, "r") as file:
    abi = json.loads(file.read().strip())

web3 = Web3(Web3.HTTPProvider(node))

contract = web3.eth.contract(address=Web3.to_checksum_address(sys.argv[2]), abi=abi)
account = web3.eth.account.from_key(private_key)

async def flash_arbitrage(ctx, mult: float, dual: bool):
    message = "Fetching prices🌐..."

    await notify(message, ctx)
    print(message)
     
    if dual:
        arbitrages = await get_most_profitable_dual(
            fl,
            tokens,
            routers,
            weth,
            eth_router,
            mult,
            debug_arbitrage,
            ctx
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
            ctx
        )
    if len(arbitrages) == 0:
        message = "No profit made, there is no profitable arbitrages❌."

        await notify(message, ctx)
        print(message)
        print("-"*len(message))
        return
    
    # arbitraging
    await arbitrage_while_profitable(arbitrages, mult, debug_arbitrage, ctx)
    message = "Arbitrages ended✅."

    await notify(message, ctx)
    print(message)
    print("-"*len(message))

intents = Intents.all()
intents.members = True

bot = Bot(command_prefix="/", intents=intents)
loop = asyncio.get_event_loop()

async def notify(message: str, ctx):
    await ctx.channel.send(message)

@bot.command(description="get current gas price in WEI/GWEI")
async def gas(ctx):
    gas_price = web3.eth.gas_price/1e18
    value = "GWEI"
    if gas_price < 1:
        value = "WEI"
        gas_price = int(gas_price*1e18)
    await ctx.channel.send(f"current gas price in {value} is {gas_price}")

@bot.command(description="dual dex flashloan arbitrage")
async def arbitrage2(ctx, mult: int):
    await flash_arbitrage(ctx, mult, True)

@bot.command(description="triple dex flashload arbitrage")
async def arbitrage3(ctx, mult: int):
    await flash_arbitrage(ctx, mult, False)

bot.run(BOT_TOKEN)