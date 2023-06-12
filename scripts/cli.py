import json
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

with open(sys.argv[1], "r") as file:
    config = json.loads(file.read())
    fl = config["fl"]
    weth = config["weth"]
    eth_dex = config["eth-dex"]
    node = config["node"]
    build = config["build"]
    tokens = config["tokens"]
    routers = config["routers"]
    private_key = config["private_key"]

dex_by_addr = { router["address"]: router["dex"] for router in routers }
addr_by_dex = { router["dex"]: router["address"] for router in routers }
get_addr_by_dex = lambda dex: addr_by_dex[dex]
get_dex_by_addr = lambda addr: dex_by_addr[addr]

sym_by_addr = { token["address"]: token["symbol"] for token in tokens }
addr_by_sym = { token["symbol"]: token["address"] for token in tokens }
get_sym_by_addr = lambda addr: sym_by_addr[addr]
get_addr_by_sym = lambda sym: addr_by_sym[sym]