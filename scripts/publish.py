from consts import *
from colors import *
from web3 import Web3
import json
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

def deploy(node: str, abi, bytecode, private_key, *args):
    web3 = Web3(Web3.HTTPProvider(node))

    contract = web3.eth.contract(abi=abi, bytecode=bytecode)

    # creating tx
    account = web3.eth.account.from_key(private_key)
    web3.eth.default_account = account.address

    constructor = contract.constructor(*args)
    
    gas_price = web3.eth.gas_price
    gas_limit = constructor.estimate_gas()

    eth = gas_price*gas_limit/1e18
    print(f"publish will consume {eth} ETH, gas price - {gas_price}, gas limit - {gas_limit}")
    if eth > MAX_GAS:
        raise RuntimeError(COLOR_RED + f"gas fee({eth}) is too high" + COLOR_RESET)

    tx = constructor.build_transaction({
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gasPrice": gas_price,
        "gas": gas_limit,
    })

    signed_tx = account.sign_transaction(tx)

    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    print("✅Contract was succesfully deployed at -", tx_receipt.contractAddress)

with open(sys.argv[1], "r") as file:
    config = json.loads(file.read())
    lpa = config["LPA"]
    node = config["node"]
    build = config["build"]
    private_key = config["private_key"]

with open(f"{build}.bin", "r") as file:
    bytecode = "0x" + file.read().strip()

with open(f"{build}.abi", "r") as file:
    abi = json.loads(file.read().strip())

deploy(node, abi, bytecode, private_key, Web3.to_checksum_address(lpa))