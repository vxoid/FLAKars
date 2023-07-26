from discord.ext.commands import Context
from contract.functions import *
from contract.arbitrage import *
from contract.arbmath import *
from load_env import *
from views import *

@bot.command(description="gives the menu!")
async def menu(ctx: Context):
  user = ctx.author if type(ctx) == Context else ctx.user

  role = ctx.guild.get_role(allowed_role)
  if allowed_role is not None and not user.guild_permissions.administrator and role not in user.roles:
    return
  
  main_view = Menu()
  await ctx.channel.send("Here is the menu! 💬", view=main_view)

if __name__ == "__main__":
  bot.run(token)