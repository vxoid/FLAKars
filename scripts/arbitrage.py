from config.config import Config
import asyncio
import sys

def usage(args):
  space = " "*len(args[0])
  print("USAGE: ")
  print(f"{args[0]} config.json")
  print(f"{space  } ^^^^^^^^^^^")
  print(f"{space  } path to the configuration file")

async def main():
  if len(sys.argv) <= 0:
    usage(sys.argv)
    return
  
  config = Config.from_json_file(sys.argv[1])
  while True:
    async with asyncio.TaskGroup() as tg:
      for logger in config.loggers:
        tg.create_task(logger.log_start())

    arbitrages = await config.get_available_arbitrages()
    await config.arbitrage_while_profitable(arbitrages)
        
    await asyncio.sleep(2 * 60 * 60) # once per 2h

if __name__ == "__main__":
  asyncio.run(main())