from contract.router import Router
from contract.token import Token
from typing import List

class NotFoundTokenError(Exception):
  def __init__(self, token_name: str, tokens: List[Token]):
    message = f"\n'{token_name}' token is not available\n"
    
    message += "Choose one out of:\n" 
    for token in tokens:
      message += f"{token.name}\t{token.address}\n"   

    super().__init__(message)

class NotFoundRouterError(Exception):
  def __init__(self, router_name: str, routers: List[Router]):
    message = f"\n'{router_name}' is not available\n"
    
    message += "Choose one out of:\n" 
    for router in routers:
      message += f"{router.get_name()}\t{router.get_arbitrage_address()}\n"   

    super().__init__(message)

class InvalidWETHRouterVersion(Exception):
  def __init__(self, router: Router, target_version: str):
    message = f"{router.get_name()} must be {target_version} in order to be weth router (dex)"
    
    super().__init__(message)

class NotFoundRouterElementError(Exception):
  def __init__(self, router_dict, key: str):
    message = f"\nInvalid router: {router_dict}\nCannot find '{key}' key"

    super().__init__(message)

class NotFoundTokenElementError(Exception):
  def __init__(self, token_dict, key: str):
    message = f"\nInvalid token: {token_dict}\nCannot find '{key}' key"

    super().__init__(message)

class NotFoundConfigElementError(Exception):
  def __init__(self, config_dict, key: str):
    message = f"\nInvalid config: {config_dict}\nCannot find '{key}' key"

    super().__init__(message)