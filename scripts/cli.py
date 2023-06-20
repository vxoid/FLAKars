from contract.etoken import Token
from contract.dex import DEX
from colors import *
import json
import sys

with open(sys.argv[1], "r") as file:
    config = json.loads(file.read())
    lpa = config["LPA"]
    node = config["node"]
    abi = config["abi"]
    bytecode = config["bytecode"] if "bytecode" in config else None

    tokens = [Token(token["address"], token["symbol"]) for token in config["tokens"]]
    routers = [
        DEX(
            router["address"],
            router["dex"],
            router["estim"] if "estim" in router else None,
            router["avail"] if "avail" in router else None
        ) for router in config["routers"]
    ]

    def get_token_by_sym(symbol: str) -> Token:
        try:
            return [token for token in tokens if str(token) == symbol][0]
        except IndexError:
            raise ModuleNotFoundError(COLOR_RED + f"There isn't any token with symbol '{symbol}'" + COLOR_RESET)
    def get_router_by_sym(dex: str) -> DEX:
        try:
            return [router for router in routers if str(router) == dex][0]
        except IndexError:
            raise ModuleNotFoundError(COLOR_RED + f"There isn't any router with name '{dex}'" + COLOR_RESET)
    
    fl = [get_token_by_sym(fl_token) for fl_token in config["fl"]]
    weth = get_token_by_sym(config["weth"])
    eth_router = get_router_by_sym(config["eth-dex"])
    private_key = config["private_key"]