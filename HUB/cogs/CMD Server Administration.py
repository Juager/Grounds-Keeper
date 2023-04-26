#--#
#Administration Commands
#--#

#IMPORTS

import discord
from discord.ext import commands

#--#
#COMMANDS
#--#

class CMDSAdmin(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

#Command - Gulag
  @commands.command()
  @commands.has_permissions(administrator=True)
  async def gulag(self, ctx, user:discord.member):
    
    audit_log_cog = self.bot.get_cog('cog.Audit Log')
    if audit_log_cog is not None:
      await audit_log_cog.log_command_usage(ctx)
    else:
      print('Audit Log cog not found')

    old_roles = user.roles.copy()
    await user.edit(roles=[])
    role_id = ctx.self.bot.gulage_role_id
    role = ctx.guild.get_role(role_id)
    await user.add_roles(role)
    channel_id = ctx.bot.gulag_channel_id
    channel = self.bot.get_channel(channel_id)

    roles_str = ""
    for r in old_roles:
        if r != ctx.guild.default_role:
            roles_str += r.name + ", "
    roles_str = roles_str.rstrip(", ")

    await channel.send(f"{user.mention} has been given the {role.name} role and had the following roles taken away: {roles_str}")

  @gulag.error
  async def gulag_error(self, ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the necessary permissions to use this command.")

#Command - Purge
  @commands.command()
  @commands.has_permissions(administrator=True)
  async def purge(self, ctx, amount: int):
    
    audit_log_cog = self.bot.get_cog('cog.Audit Log')
    if audit_log_cog is not None:
      await audit_log_cog.log_command_usage(ctx)
    else:
      print('Audit Log cog not found')
    
    if amount > 99:  # Limit the purge amount to 99 messages at a time (100 including the command message)
        await ctx.send("You can only purge up to 99 messages at a time.")
        return

    await ctx.channel.purge(limit=amount + 1)  # Add 1 to also delete the command message

  @purge.error
  async def purge_error(ctx, error):
      if isinstance(error, commands.MissingPermissions):
          await ctx.send("You don't have the necessary permissions to use this command.")
      elif isinstance(error, commands.MissingRequiredArgument):
          await ctx.send("Please specify the number of messages to delete.")
      elif isinstance(error, commands.BadArgument):
          await ctx.send("Invalid input. Please enter a number.")
      
  #--#
async def setup(bot):
  await bot.add_cog(CMDSAdmin(bot))