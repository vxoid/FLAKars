from discord import ButtonStyle, Interaction, Intents, User
from discord.ui import button, View, Button
from datetime import timedelta, datetime
from discord.ext.commands import Bot
from arbitrage import *
from load_env import *
import pytz

TIME_FORMAT = "%Y-%m-%d %H:%M"

intents = Intents.all()
intents.members = True

bot = Bot(command_prefix="/", intents=intents)
user_multiplier = {}

def convert_to_timezone(datetime: datetime, timezone_offset: int) -> datetime:
  return datetime.astimezone(pytz.FixedOffset(timezone_offset * 60))

def set_timezone(datetime: datetime, timezone: int) -> datetime:
  timezone_offset = timedelta(hours=timezone)
  return datetime.replace(tzinfo=pytz.FixedOffset(timezone_offset.total_seconds() // 60))

def set_multiplier(user: User, multiplier: float):
  user_multiplier[user.id] = multiplier

def get_multiplier(user: User) -> float:
  return user_multiplier.get(user.id) or 10

class Menu(View):
  def __init__(self):
    super().__init__()

  @button(label="Double Arbitrage", style=ButtonStyle.grey)
  async def double_arbitrage(self, interaction: Interaction, _: Button):    
    role = interaction.guild.get_role(allowed_role)
    if allowed_role is not None and not interaction.user.guild_permissions.administrator and role not in interaction.user.roles:
      return

    multiplier = get_multiplier(interaction.user)

    await interaction.response.send_message(f"Fetching prices, {multiplier} multiplier🌐...")
    await interaction.message.delete()
    await flash_arbitrage(interaction, multiplier, True)
  
  @button(label="Triple Arbitrage", style=ButtonStyle.grey)
  async def triple_arbitrage(self, interaction: Interaction, _: Button):    
    role = interaction.guild.get_role(allowed_role)
    if allowed_role is not None and not interaction.user.guild_permissions.administrator and role not in interaction.user.roles:
      return

    multiplier = get_multiplier(interaction.user)

    await interaction.response.send_message(f"Fetching prices, {multiplier} multiplier🌐...")
    await interaction.message.delete()
    await flash_arbitrage(interaction, multiplier, False)

  @button(label="Set default multiplier", style=ButtonStyle.gray)
  async def set_multiplier(self, interaction: Interaction, _: Button):
    role = interaction.guild.get_role(allowed_role)
    if allowed_role is not None and not interaction.user.guild_permissions.administrator and role not in interaction.user.roles:
      return
    
    await interaction.response.send_message("Waiting for user response...")
    await interaction.user.send(f"Enter arbitrage multiplier, previous is {get_multiplier(interaction.user)}.")

    while True:
      response = await bot.wait_for("message", check=lambda message: message.author == interaction.user)
      try: 
        multiplier = float(response.content)
        break
      except ValueError:
        await interaction.user.send(f"'{response.content}' multiplier is invalid, try again.")

    set_multiplier(interaction.user, multiplier)
    await interaction.user.send(f"Successfully set default multiplier to {multiplier} ✅.")
  
  @button(label="Gas Price", style=ButtonStyle.blurple)
  async def gas(self, interaction: Interaction, _: Button):
    global web3

    role = interaction.guild.get_role(allowed_role)
    if allowed_role is not None and not interaction.user.guild_permissions.administrator and role not in interaction.user.roles:
      return
    
    gas_price = web3.eth.gas_price / 1e18
    value = "GWEI"
    if gas_price < 1:
      value = "WEI"
      gas_price = int(gas_price*1e18)

    await interaction.response.send_message(f"Current gas price is {gas_price} {value}.")

  @button(label="Withdraw", style=ButtonStyle.green)
  async def withdraw(self, interaction: Interaction, _: Button):    
    role = interaction.guild.get_role(allowed_role)
    if allowed_role is not None and not interaction.user.guild_permissions.administrator and role not in interaction.user.roles:
      return
    
    await interaction.response.send_message("Withdrawing...")
    withdrawAll(web3, contract, account)
    await interaction.channel.send("Succesfully withdrawn whole contract balance ✅.")