from contract.arbitrage import Arbitrage
from errors.errors import RateError
from .logger import Logger
from colorama import Fore

class CliLogger(Logger):
  def __init__(self) -> None:
    super().__init__()

  def get_id(self) -> str:
    return "CLI"

  async def _log_start(self):
    print(Fore.GREEN + f"> starting flash loan arbitrage..." + Fore.RESET)

  async def _log_success(self, arbitrage: Arbitrage):
    print(Fore.GREEN + f"{str(arbitrage)} ✅" + Fore.RESET)

  async def _log_error(self, arbitrage: Arbitrage, err):
    print(Fore.RED + f"{str(arbitrage)} failed -> {err}" + Fore.RESET)