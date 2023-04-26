import discord
from discord.ext import commands
import asyncio
from cogs.Server_Setup import ServerSetup

class CMDQuote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_setup = ServerSetup(bot)

    @commands.command()
    async def quote(self, ctx):
        quote_channel_id = await self.server_setup.get_channel_data(ctx.guild.id, "quote_channel")
        if not quote_channel_id:
            await ctx.send("The Server Admins have decided not to give this command a channel.")
            return
      
        quote_channel = ctx.guild.get_channel(quote_channel_id)

        if quote_channel is None:
            await ctx.send("The quote channel could not be found. Please ask a Server Admin to check the channel configuration.")
            return

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        question = "What message do you want me to quote? Please @ the user, mention the channel (#channel), and then provide the exact message in parentheses. Separate all information with a comma and space - Example: @GroundsKeeper, #General, \"This is the quote\"."
        await ctx.send(question)

        try:
            response = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try the command again.")
            return

        try:
            member, channel, message = [x.strip() for x in response.content.split(',', 2)]
            member = await commands.MemberConverter().convert(ctx, member)
            channel = await commands.TextChannelConverter().convert(ctx, channel)
            message = message.strip('"')
        except (ValueError, commands.BadArgument):
            await ctx.send("Invalid format. Please follow the example format and try again.")
            return

        async for msg in channel.history():
            if msg.author == member and msg.content == message:
                embed = discord.Embed(description=message, color=0x00ff00)
                embed.set_author(name=member.display_name, icon_url=member.avatar)
                embed.set_footer(text=f"Quoted by {ctx.author.display_name} from #{channel.name}")
                await quote_channel.send(embed=embed)
                return

        await ctx.send("The message could not be found. Make sure you provided all information needed and quoted the message exactly.")

async def setup(bot):
    await bot.add_cog(CMDQuote(bot))