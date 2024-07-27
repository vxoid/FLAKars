from logger.telegram_logger_profile import TelegramLoggerProfile
from aiogram.exceptions import TelegramRetryAfter
from restrict.restrict import RestrictableHolder
from aiogram.utils.markdown import hbold
from contract.arbitrage import Arbitrage
from .logger import Logger
from typing import List
import aiogram

class TelegramLogger(Logger):
  def __init__(self, profiles: List[TelegramLoggerProfile] = []):
    self.profiles = RestrictableHolder(profiles)
    super().__init__()

  def get_id(self) -> str:
    return "telegram"

  async def __log(self, message: str):
    profile = self.profiles._get_random()

    bot = aiogram.Bot(profile.token)
    try:
      await bot.send_message(profile.chat_id, message, parse_mode='HTML')
    except TelegramRetryAfter as e:
      profile.set_rate_limit(e.retry_after)
      return await self.__log(message)
    finally:
      await bot.session.close()

  async def _log_start(self):
    return await self.__log("> starting flash loan arbitrage...")

  async def _log_success(self, arbitrage: Arbitrage):
    await self.__log(f"> '{hbold(str(arbitrage))}' ✅")

  async def _log_error(self, arbitrage: Arbitrage, err):
    # await self.__log(f"> could not arbitrage '{hbold(str(arbitrage))}' -> {hbold(err)}*")
    pass # ignore errs