from contract.arbitrage import Arbitrage
from errors.errors import RateError
from abc import abstractmethod
from colorama import Fore
import asyncio

class Logger:
  def __init__(self) -> None:
    pass 

  @abstractmethod
  def get_id(self) -> str:
    raise NotImplementedError()

  @abstractmethod
  async def _log_start(self):
    raise NotImplementedError()
  
  @abstractmethod
  async def _log_success(self, arbitrage: Arbitrage):
    raise NotImplementedError()
  
  @abstractmethod
  async def _log_error(self, arbitrage: Arbitrage, err):
    raise NotImplementedError()

  async def log_start(self):
    try:
      await self._log_start()
    except RateError as e:
      print(Fore.RED + f"[{self.get_id()} LOGGER]: flood wait for {e.time}")
      await asyncio.sleep(e.time + 1)
      return await self.log_start()
    except Exception as e:
      print(Fore.RED + f"[{self.get_id()} LOGGER]: unhandled err -> {e}" + Fore.RESET)

  async def log_success(self, arbitrage: Arbitrage):
    try:
      await self._log_success(arbitrage)
    except RateError as e:
      print(Fore.RED + f"[{self.get_id()} LOGGER]: flood wait for {e.time}")
      await asyncio.sleep(e.time + 1)
      return await self.log_success(arbitrage)
    except Exception as e:
      print(Fore.RED + f"[{self.get_id()} LOGGER]: unhandled err -> {e}" + Fore.RESET)
  
  async def log_error(self, arbitrage: Arbitrage, err):
    try:
      await self._log_error(arbitrage, err)
    except RateError as e:
      print(Fore.RED + f"[{self.get_id()} LOGGER]: flood wait for {e.time}")
      await asyncio.sleep(e.time + 1)
      return await self.log_error(arbitrage, err)
    except Exception as e:
      print(Fore.RED + f"[{self.get_id()} LOGGER]: unhandled err -> {e}" + Fore.RESET)
