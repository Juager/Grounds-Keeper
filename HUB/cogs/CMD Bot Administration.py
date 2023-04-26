#--#
#Bot Admin. Commands
#--#

#IMPORTS

import discord
from datetime import datetime
from discord.ext import commands

#--#

class CMDBAdmin(commands.Cog):
    def __init__(self, bot):
      self.bot = bot

# COMMAND - PGK_Info
  
    @commands.command()
    async def PGK_Info(self, ctx):
        authorized_users = [337794345468035073, 353973065597714432]
        if ctx.author.id not in authorized_users:
            return
    
        guilds = self.bot.guilds
        guild_info = []
    
        for guild in guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel) and channel.permissions_for(guild.me).create_instant_invite:
                    invite = await channel.create_invite()
                    guild_info.append(f"{guild.name}: {invite.url}")
                    break
    
        uptime = datetime.utcnow() - self.bot.start_time
        uptime_str = str(uptime).split(".")[0]
    
        if ctx.guild is None:
            await ctx.author.send(f"I am currently in {len(self.bot.guilds)} server(s). Uptime: {uptime_str}\n\nServer Invites:\n" + "\n".join(guild_info))
        else:
            await ctx.send(f"I am currently in {len(self.bot.guilds)} server(s). Uptime: {uptime_str}\n\nServer Invites:\n" + "\n".join(guild_info))

# COMMAND - GK_Info
  
    @commands.command()
    async def GK_Info(self, ctx):
        # Fetch the developer user objects from their IDs
        juager = self.bot.get_user(337794345468035073)
        twit = self.bot.get_user(353973065597714432)

        # Create an invite for the GroundsKeeper Discord server
        invite_channel = self.bot.get_channel(1093294254727634974)
        invite = await invite_channel.create_invite(max_age=1800, max_uses=0)

        # Create the embed
        embed = discord.Embed(
            title="Developers & GroundsKeeper Discord Server",
            description=f"Meet the developers of GroundsKeeper and join our Discord server!",
            color=0x00bfff,
        )

        # Add the developers to the embed
        embed.add_field(name="Juager", value=f"[Profile](https://discord.com/users/{juager.id})", inline=True)
        embed.add_field(name="Twit", value=f"[Profile](https://discord.com/users/{twit.id})", inline=True)

        # Add the server invite to the embed
        embed.add_field(name="GroundsKeeper Discord Server", value=f"[Join us]({invite.url})", inline=False)

        # Send the embed
        await ctx.send(embed=embed)

#--#
async def setup(bot):
  await bot.add_cog(CMDBAdmin(bot))