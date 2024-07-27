from restrict.restrict import Restrictable

class TelegramLoggerProfile(Restrictable):
  def __init__(self, token: str, chat_id: str):
    self.token = token
    self.chat_id = chat_id
    super().__init__()
    
  @staticmethod
  def from_dict(dict) -> "TelegramLoggerProfile":
    return TelegramLoggerProfile(dict["token"], dict["chat_id"])