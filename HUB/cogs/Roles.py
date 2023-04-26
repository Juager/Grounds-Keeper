import asyncio
from discord.ext import commands
from discord import Embed
import replit

# Initialize the replit database
db = replit.db

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def rolereaction(self, ctx):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        embed = Embed()
        questions = [
            "What would you like the title of the embed to be?",
            "What would you like the description of the embed to be?",
            "Please provide the @ for all the roles you'd like users to be able to select in one message.",
            "Please provide the reactions (emojis) you want, in the same order as the roles. Separate emojis with a space."
        ]

        role_mentions = None
        reactions = None
        for question in questions:
            await ctx.send(question)

            try:
                answer = await self.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Time limit exceeded, please restart the setup process.", delete_after=10)
                return

            if question == questions[0]:
                embed.title = answer.content
            elif question == questions[1]:
                embed.description = answer.content
            elif question == questions[2]:
                role_mentions = answer.role_mentions
                roles = [role.id for role in role_mentions]
            elif question == questions[3]:
                reactions = answer.content.split()

        # Create the embed and add the role reactions
        for index, role in enumerate(role_mentions):
            embed.add_field(name=role.name, value=reactions[index], inline=False)

        sent_message = await ctx.channel.send(embed=embed)

        # Make the bot react to its own message
        for reaction in reactions:
            await sent_message.add_reaction(reaction)

        # Store the embed and role information in the replit database
        embed_key = f"{ctx.guild.id}_roles_embed"
        db[embed_key] = {"embed": embed.to_dict(), "roles": roles, "reactions": reactions}

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        embed_key = f"{payload.guild_id}_roles_embed"

        if embed_key not in db:
            return

        # Get the guild, member, and role information
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        stored_embed = db[embed_key]
        role_ids = stored_embed["roles"]
        reactions = stored_embed["reactions"]

        # Assign the corresponding role based on the reaction
        try:
            reaction_index = reactions.index(payload.emoji.name)
            role = guild.get_role(role_ids[reaction_index])
            if role not in member.roles:
                await member.add_roles(role)
        except ValueError:
            # Ignore if the reaction is not in the list of reactions
            pass
        except IndexError:
            # Ignore if the index is out of range
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        embed_key = f"{payload.guild_id}_roles_embed"

        if embed_key not in db:
            return

        # Get the guild, member, and role information
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        stored_embed = db[embed_key]
        role_ids = stored_embed["roles"]
        reactions = stored_embed["reactions"]

        # Remove the corresponding role based on the reaction
        try:
            reaction_index = reactions.index(payload.emoji.name)
            role = guild.get_role(role_ids[reaction_index])
            if role in member.roles:
                await member.remove_roles(role)
        except ValueError:
            # Ignore if the reaction is not in the list of reactions
            pass
        except IndexError:
            # Ignore if the index is out of range
            pass
          
async def setup(bot):
    await bot.add_cog(Roles(bot))