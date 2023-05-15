from typing import List
from web3 import Web3
import json
import sys

MIN_PROFIT = 1.009
BREAK_PROFIT = 2.0
COLOR_YELLOW = "\033[93m"
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

def balanceOf(contract, pk, token):
    function = contract.functions.balanceOf(
        Web3.to_checksum_address(token)
    )

    return function.call({ "from": pk })

def withdraw(web3: Web3, contract, account, token, amount):
    function = contract.functions.withdraw(
        Web3.to_checksum_address(token),
        amount
    )

    tx = function.build_transaction({
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gas": function.estimate_gas({ "from": account.address }),
        "gasPrice": web3.eth.gas_price
    })
    signed_tx = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return web3.eth.wait_for_transaction_receipt(tx_hash)

def flArbitrage(web3: Web3, contract, account, router1, router2, token1, token2, amount):
    function = contract.functions.flArbitrage(
        Web3.to_checksum_address(router1),
        Web3.to_checksum_address(router2),
        Web3.to_checksum_address(token1),
        Web3.to_checksum_address(token2),
        amount
    )

    tx = function.build_transaction({
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gas": function.estimate_gas({ "from": account.address }),
        "gasPrice": web3.eth.gas_price
    })
    signed_tx = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return web3.eth.wait_for_transaction_receipt(tx_hash)

def dexArbitrage(web3: Web3, contract, account, router1, router2, token1, token2, amount):
    function = contract.functions.dexArbitrage(
        Web3.to_checksum_address(router1),
        Web3.to_checksum_address(router2),
        Web3.to_checksum_address(token1),
        Web3.to_checksum_address(token2),
        amount
    )

    tx = function.build_transaction({
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gas": function.estimate_gas({ "from": account.address }),
        "gasPrice": web3.eth.gas_price
    })
    signed_tx = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return web3.eth.wait_for_transaction_receipt(tx_hash)

def estimateDexArbitrage(contract, pk, router1, router2, token1, token2, amount):
    function = contract.functions.estimateDexArbitrage(
        Web3.to_checksum_address(router1),
        Web3.to_checksum_address(router2),
        Web3.to_checksum_address(token1),
        Web3.to_checksum_address(token2),
        amount
    )

    return function.call({ "from": pk })

class Arbitrage:
    def __init__(self, router1, router2, token1, token2, profit):
        self.router1 = router1
        self.router2 = router2
        self.token1 = token1
        self.token2 = token2
        self.profit = profit

def get_most_profitable(contract, pk, tokens, routers, break_profit, min_profit) -> List[Arbitrage]:
    arbitrages = []
    for token1, amount in tokens:
        for token2, _ in tokens:
            if token1 == token2: # cant estimate arbitarge on 2 same tokens
                continue
            for router1 in routers:
                for router2 in routers:
                    if router1 == router2: # no profit due to fees
                        continue
                    estimated_amount = 0
                    try:
                        estimated_amount = estimateDexArbitrage(contract, pk, router1, router2, token1, token2, amount)
                    except Exception as e:
                        print(
                            COLOR_YELLOW +
                            f"{get_sym_by_addr(token1)}({get_dex_by_addr(router1)}) <-> {get_sym_by_addr(token2)}({get_dex_by_addr(router2)}) failed with {e}"
                            + COLOR_RESET
                        )
                        continue

                    if float(estimated_amount) >= amount*break_profit:
                        arbitrages.append(Arbitrage(router1, router2, token1, token2, estimated_amount))
                        return arbitrages

                    if float(estimated_amount) > amount*min_profit:
                        arbitrages.append(Arbitrage(router1, router2, token1, token2, estimated_amount))
                    
    return arbitrages

with open(sys.argv[1], "r") as file:
    config = json.loads(file.read())
    node = config["node"]
    build = config["build"]
    tokens = config["tokens"]
    routers = config["routers"]
    private_key = config["private_key"]

dex_by_addr = { router["address"]: router["dex"] for router in routers }
get_dex_by_addr = lambda addr: dex_by_addr[addr]

sym_by_addr = { token["address"]: token["symbol"] for token in tokens }
addr_by_sym = { token["symbol"]: token["address"] for token in tokens }
fl_by_addr = { token["address"]: token["fl"] for token in tokens }
get_sym_by_addr = lambda addr: sym_by_addr[addr]
get_addr_by_sym = lambda sym: addr_by_sym[sym]

with open(f"{build}.abi", "r") as file:
    abi = json.loads(file.read().strip())

web3 = Web3(Web3.HTTPProvider(node))

contract = web3.eth.contract(address=sys.argv[2], abi=abi)
account = web3.eth.account.from_key(private_key)

while True:
    balance_by_addr = { token["address"]: balanceOf(contract, account.address, token["address"]) for token in tokens }
    arb_by_addr = {}
    priced_tokens = []
    for token in tokens:
        balance = balance_by_addr[token["address"]]
        if balance == 0 or token["fl"]:
            balance = token["arbitrage"]

        priced_tokens.append((token["address"], balance))
        arb_by_addr.update({ token["address"]: balance })

    print("Fetching prices...")
    arbitrages = get_most_profitable(
        contract,
        account.address,
        priced_tokens,
        [router["address"] for router in routers],
        BREAK_PROFIT,
        MIN_PROFIT
    )

    for arbitrage in arbitrages:
        print(f"{get_sym_by_addr(arbitrage.token1)}({get_dex_by_addr(arbitrage.router1)}) <-> {get_sym_by_addr(arbitrage.token2)}({get_dex_by_addr(arbitrage.router2)}) -> {arbitrage.profit}")
        try:
            if balance_by_addr[arbitrage.token1] == 0 or fl_by_addr[arbitrage.token1]:
                flArbitrage(web3, contract, account, arbitrage.router1, arbitrage.router2, arbitrage.token1, arbitrage.token2, arb_by_addr[arbitrage.token1])
            else:
                dexArbitrage(web3, contract, account, arbitrage.router1, arbitrage.router2, arbitrage.token1, arbitrage.token2, balance_by_addr[arbitrage.token1])
        except Exception as e:
            print(COLOR_YELLOW + f"arbitrage failed with {e}" + COLOR_RESET)
            continue

        print(f"✅💹 Succesfully arbitraged, current balance is {balanceOf(contract, account.address, arbitrage.token1)} {get_sym_by_addr(arbitrage.token1)}")
        print("-------------------------------------------------------")