from datetime import datetime, timedelta
from errors.errors import *
from typing import List
import random

class Restrictable:
  def __init__(self, trusted: bool = False, secure: bool = False):
    self.__restricted_till = datetime.now()
    self.__secure = secure
    self.__trusted = trusted
  
  def available(self) -> bool:
    cur_time = datetime.now()
    return cur_time >= self.__restricted_till

  def get_restricted_till(self):
    return self.__restricted_till

  def set_rate_limit(self, for_secs: float):
    self.__restricted_till = datetime.now() + timedelta(seconds=for_secs)

  def is_secure(self) -> bool:
    return self.__secure
  
  def is_trusted(self) -> bool:
    return self.__trusted

class RestrictableHolder:
  def __init__(self, restrictables: List[Restrictable]) -> None:
    self.restrictables = restrictables
    
  def _get_most_recently_unlocked(self) -> Restrictable:
    cur_time = datetime.now()
    result = self.restrictables[0]
    
    for proxy in self.restrictables:
      if proxy.get_restricted_till() - cur_time < result.get_restricted_till() - cur_time:
        result = proxy

    return result

  def _get_available(self) -> List[Restrictable]:
    return [restrictable for restrictable in self.restrictables if restrictable.available()]
  
  def _get_random(self) -> Restrictable:
    restrictables = self._get_available()
    if len(restrictables) < 1:
      restrictable = self._get_most_recently_unlocked()
      raise RateError((restrictable.get_restricted_till() - datetime.now()).total_seconds())

    return random.choice(restrictables)