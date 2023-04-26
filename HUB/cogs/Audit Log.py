#--#
#Audit Log
#--#

#IMPORTS

import discord
import replit
from replit import db
from discord.ext import commands


#--#

class AuditLog(commands.Cog):
    def __init__(self, bot):
      self.bot = bot

#Audit Log Function
    async def log_command_usage(self, ctx):
        if str(ctx.guild.id) in db:
            channel_id = int(db[str(ctx.guild.id)])
            channel = self.bot.get_channel(channel_id)
            if channel is not None:
                await channel.send(f"{ctx.author.name} used the {ctx.command.name} command in {ctx.guild.name}.")


#--#

async def setup(bot):
  await bot.add_cog(AuditLog(bot))