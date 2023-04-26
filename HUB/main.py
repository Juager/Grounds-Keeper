#--#

#Command Overview

#CMD Audio
# !play, !stop, !q, !skip

#CMD Bot Administration
# !GK_Info, !PGK_Info

#CMD Open AI - Disabled
# !dog, !dinosaur

#CMD Quote
# !quote

#CMD Server Administration
# !purge, !gulag (Disabled)

#Roles
# !rolereaction

#Server_Setup
# !server_setup

#--#

#Package Imports

import os
import discord
from datetime import datetime
from discord.ext import commands
from collections import defaultdict
from discord.ui import View, Select
from discord import SelectOption
from replit import db

intents = discord.Intents.all()
intents.guilds = True
intents.messages = True
intents.voice_states = True
intents.message_content = True
intents.members = True

COGS = [
    "cogs.CMD Audio",
    "cogs.CMD Bot Administration",
    #"cogs.OpenAI",
    "cogs.Audit Log",
    "cogs.CMD Server Administration",
    "cogs.Server_Setup",
    "cogs.Roles",
    "cogs.CMD Quote",
]

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

async def load_cogs(bot):
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"Loaded cog: {cog}")
        except Exception as e:
            print(f"Failed to load cog: {cog} - {e}")

queues = defaultdict(list)

@bot.event
async def on_ready():
    print("Bot is ready.")
    await load_cogs(bot)

class HelpView(View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())

class HelpSelect(Select):
    def __init__(self):
        options = [
            SelectOption(label="Server Setup", value="server_setup"),
            SelectOption(label="Administration", value="administration"),
            SelectOption(label="Audio", value="audio"),
            SelectOption(label="Fun", value="fun"),
        ]
        super().__init__(placeholder="Choose a category", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_category = self.values[0]

        category_commands = {
            "server_setup": [
                ("!set_audit_log_channel", "<Channel ID> - Set up the server audit-log channel."),
                ("!SetupGulag", "Start the setup function for the !Gulag command."),
                ("!rolereaction", "Create an embed to allow members to choose roles."),
            ],
            "administration": [
                ("!Gulag", "<@user> - Remove all roles from a user and give them a specified role."),
                ("!purge", "<# of msgs> - Purge a specified number of messages up to 99."),
            ],
            "audio": [
                ("!play", "<YouTube URL or search query> - Play a song."),
                ("!stop", "Stop playing the current song and disconnect from the voice channel."),
                ("!skip", "Skip the current song."),
                ("!q", "Show the current queue of songs."),
            ],
            "fun": [
                ("All fun commands are currently", "disabled."),
            ],
        }

        category_name = {
            "server_setup": "Server Setup",
            "administration": "Administration",
            "audio": "Audio",
            "fun": "Fun",
        }

        if selected_category in category_commands:
            commands = category_commands[selected_category]
            commands_description = "\n".join([f"{cmd} - {desc}" for cmd, desc in commands])

            embed = discord.Embed(
                title=category_name[selected_category],
                description=commands_description,
                color=discord.Color.blue(),
            )
            await interaction.response.edit_message(embed=embed, view=self.view)
        else:
            await interaction.response.send_message("Invalid category selected.", ephemeral=True)

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help",
        description="Here are the commands for the bot, sorted by category.",
        color=discord.Color.blue(),
    )
    view = HelpView()
    await ctx.send(embed=embed, view=view)

bot.start_time = datetime.utcnow()

#@bot.event
#async def on_command_error(ctx, error):
    #if isinstance(error, commands.CommandNotFound):
        #return
    #raise error

bot.run(os.environ["GK_Token"])