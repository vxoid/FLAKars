class UnknownError(Exception):
  def __init__(self, message, errors = None):
    msg = f"{message}"
    if errors is not None:
      msg += f", errors: {errors}"

    super().__init__(msg)
    self.errors = errors

class RateError(UnknownError):
  def __init__(self, time: float = 800):
    super().__init__(f"The resource is being rate limited for {time} secs.")
    self.time = time