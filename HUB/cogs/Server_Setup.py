
import asyncio
import os
import discord
from discord.ext import commands
from replit import db
from typing import Optional

# SETUP - Channel Data

class ServerSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ask_question(self, ctx, question: str) -> Optional[str]:
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send(question)
        try:
            message = await self.bot.wait_for('message', timeout=60.0, check=check)
            return message.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return None

    async def save_channel_data(self, guild_id: int, key: str, value: str):
        db_key = f"{guild_id}_{key}"
        db[db_key] = value

    async def get_channel_data(self, guild_id: int, key: str) -> Optional[str]:
        db_key = f"{guild_id}_{key}"
        return db.get(db_key)

# COMMAND - !server_setup
  
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def server_setup(self, ctx):
        questions = {
            "quote_channel": "What channel will be used for quotes? (Please mention the channel or say 'None' to disable this command)",
            "audit_log_channel": "What channel will be used for the audit log?(Please mention the channel or say 'None' to disable this command)"
        }

        for key, question in questions.items():
            answer = await self.ask_question(ctx, question)
            if answer:
                channel = discord.utils.get(ctx.guild.channels, mention=answer)
                if channel:
                    await self.save_channel_data(ctx.guild.id, key, channel.id)
                else:
                    await ctx.send(f"Invalid channel mention: {answer}")

        await ctx.send("Server setup complete.")

    ## EXAMPLE TO USE FUNCTION | from Server Setup.py import get_channel_data
    #@commands.command()
    #async def quote(ctx):
    #channel_id = get_channel_data(ctx.guild.id, "quote_channel")
    #if channel_id:
        #quote_channel = ctx.guild.get_channel(channel_id)
        # Your command logic using the quote_channel
    #else:
        # Notify the user that the channel hasn't been set up
        #await ctx.send("The Server Admins have decided not to give this command a channel.")

async def setup(bot):
    await bot.add_cog(ServerSetup(bot))