from .errors import NotFoundTokenError, NotFoundRouterError, InvalidWETHRouterVersion
from contract.uniswapv3 import UniswapRouterV3
from contract.uniswapv2 import UniswapRouterV2
from contract.arbitrage import Arbitrage
from contract.contract import Contract
from .config_dict import ConfigDict
from .router_dict import RouterDict
from contract.router import Router
from .token_dict import TokenDict
from contract.token import Token
from attrs import define, field
from contract.pair import Pair
from web3 import exceptions
from typing import List
import colorama
import json

ARBITRAGE_AMOUNT_IN_ETH = 0.01

@define(kw_only=True)
class Config:
  node: str = field()
  private_key: str = field()
  bin: str = field()
  contract: Contract = field()
  lending_pool_address: str = field()
  weth: Token = field()
  weth_dex: UniswapRouterV2 = field()
  routers: List[Router] = field()
  tokens: List[Token] = field()
  flash_loan_tokens: List[Token] = field()

  @staticmethod
  def from_json_file(path: str, publish = False) -> "Config":
    with open(path) as file:
      dict = json.loads(file.read().strip())
    
    return Config.from_dict(dict, publish=publish)

  @staticmethod
  def from_dict(dict, publish = False) -> "Config":
    config = ConfigDict(dict)

    private_key = config.get("private_key")
    with open(config.get("abi")) as file:
      abi = json.loads(file.read().strip())
    with open(config.get("bytecode")) as file:
      bin = "0x" + file.read().strip()
    node = config.get("node")
    lending_pool_address = config.get("LPA")

    address = config.get("address")
    if publish:
      contract, tx_hash = Contract.publish(node, private_key, lending_pool_address, abi, bin)
    else:
      contract = Contract.new(node, private_key, address, abi)

    token_dicts = [TokenDict(token) for token in config.get("tokens")]
    tokens = [Token(name=token.get("symbol"), address=token.get("address")) for token in token_dicts]
    weth = find_from_tokens(config.get("weth"), tokens)
    flash_loan_tokens = [find_from_tokens(token, tokens) for token in config.get("fl")]

    routers = []
    weth_dex_name = config.get("eth-dex")
    weth_dex = None

    for router in config.get("routers"):
      router_dict = RouterDict(router)

      is_v3 = router_dict.is_v3()
      is_v2 = router_dict.is_v2()
      if is_v3:
        parsed_router = UniswapRouterV3(name=router_dict.get("name"), address=router_dict.get("router"), quoter_address=router_dict.get("quoter"), factory_address=router_dict.get("factory"))
      elif is_v2:
        parsed_router = UniswapRouterV2(name=router_dict.get("name"), address=router_dict.get("router"))
      
      routers.append(parsed_router)
      if router_dict.get("name") == weth_dex_name:
        if is_v2:
          weth_dex = parsed_router
        else:
          raise InvalidWETHRouterVersion(parsed_router, "Uniswap V2")
    
    if weth_dex is None:
      raise NotFoundRouterError(weth_dex_name, routers)
    
    return Config(
      node=node,
      private_key=private_key,
      bin=bin,
      contract=contract,
      lending_pool_address=lending_pool_address,
      weth=weth,
      weth_dex=weth_dex,
      routers=routers,
      tokens=tokens,
      flash_loan_tokens=flash_loan_tokens
    )
  
  def get_available_arbitrages(self) -> List[Arbitrage]:
    arbitrages = []
    eth_decimals = self.contract.decimals_of(self.weth)

    for token_1 in self.flash_loan_tokens:
      eth_pair = Pair(router=self.weth_dex, token_in=self.weth, token_out=token_1)

      if not self.contract.available(eth_pair):
        continue

      for token_2 in self.tokens:
        if token_1.address == token_2.address:
          continue

        for router_1 in self.routers:          
          pair_in = Pair(router=router_1, token_in=token_1, token_out=token_2)
          
          if not self.contract.available(pair_in):
            continue

          for router_2 in self.routers:
            if router_1.get_arbitrage_address() == router_2.get_arbitrage_address():
              continue

            pair_out = Pair(router=router_2, token_in=token_2, token_out=token_1)
            
            amount = int(ARBITRAGE_AMOUNT_IN_ETH * (10 ** eth_decimals))
            amount_in_token1 = self.contract.convert(eth_pair, amount)

            arbitrage = Arbitrage(eth_pair=eth_pair, pair_in=pair_in, pair_out=pair_out, amount=amount_in_token1)

            try:
              gas_fees = self.contract.get_gas_fees_of_flash_loan_arbitrage_with_min_income(arbitrage.pair_in, arbitrage.pair_out, arbitrage.amount, 0)
            except exceptions.ContractLogicError as e:
              print(colorama.Fore.RED + f"Gas fee fetching failed due to: {e}" + colorama.Fore.RESET)
              continue
            
            print(f"gas fees for {(gas_fees / 10**18)} ETH")
            gas_fees_in_weth = int((gas_fees / 10**18) * 10**eth_decimals)
            gas_fees_in_token1 = self.contract.convert(arbitrage.eth_pair, gas_fees_in_weth)

            try:
              self.contract.flash_loan_arbitrage_with_min_income(arbitrage.pair_in, arbitrage.pair_out, arbitrage.amount, gas_fees_in_token1)
            except exceptions.ContractLogicError as e:
              print(colorama.Fore.RED + f"Arbitrage failed due to: {e}" + colorama.Fore.RESET)
              continue
            
            print(colorama.Fore.GREEN + f"{str(arbitrage)} ✅" + colorama.Fore.RESET)
            arbitrages.append(arbitrage)
    
    return arbitrages
  
def find_from_tokens(name: str, tokens: List[Token]) -> Token:
  tokens_with_target_name = [token for token in tokens if token.name == name]

  if len(tokens_with_target_name) > 0:
    return tokens_with_target_name[0]
  
  raise NotFoundTokenError(name, tokens)