#--#

#Command Overview

#Audio
# !play, !stop, !random_song, !q, !skip

#Administration
# !gulag, !purge

#Fun
# !dog, !dinosaur

#--#

#Package Imports
import os
import random
import asyncio
import yt_dlp
import discord
import openai
from discord.ext import commands
from collections import defaultdict
from discord.ui import View, Select

#--#

#Variables
guild_queues = {}


#--#

#Intents Dictionary
intents = discord.Intents.all()
intents.guilds = True
intents.messages = True
intents.voice_states = True
intents.message_content = True
intents.members = True
#intents.direct_message_reactions = True

#--#

#Audit Log Function
async def log_command_usage(ctx):
    channel_id = 1091195885213470760 # Replace with the ID of the channel where you want to log command usage
    channel = bot.get_channel(channel_id)
    await channel.send(f"{ctx.author.name} used the {ctx.command.name} command.")

#Prefix Defined
bot = commands.Bot(command_prefix='!', intents=intents)

bot.remove_command('help')

#--#

#Boot
@bot.event
async def on_ready():
    print('Bot is ready.')

queues = defaultdict(list)
  
#--#

#Command - !help
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help",
        description="Here are the commands for the bot, sorted by category.",
        color=discord.Color.blue()
    )

    # Music commands
    music_commands = (
        ("!play <YouTube URL or search query>", "Play a song from a YouTube URL or search for a song using a query."),
        ("!stop", "Stop playing the current song and disconnect from the voice channel."),
        ("!skip", "Skip the current song."),
        ("!q", "Show the current queue of songs."),
        ("!random_song", "Play a random song from a predefined YouTube playlist."),
    )

    music_description = "\n".join([f"{cmd} - {desc}" for cmd, desc in music_commands])
    embed.add_field(name="Music", value=music_description, inline=False)

    # Administration commands
    administration_commands = (
        ("!gulag <@user>", "Remove all roles from a user and give them a specified role (requires administrator permission)."),
        ("!purge <# of msgs>", "Purges a specified number of messages up to 99. Will automatically add 1 to your number to delete the prompt. (requires administrator permission)."),
        ("!choose_role <Title> <Body of Embed> <Role 1 ID> <Role 2 ID>...", "This will create an Embed with the information provided. Members will be able to choose roles specified through a dropdown menu. The Title and Body will need to be surrounded by double quotation marks to mark a string.")
    )

    administration_description = "\n".join([f"{cmd} - {desc}" for cmd, desc in administration_commands])
    embed.add_field(name="Administration", value=administration_description, inline=False)

    # Fun commands
    fun_commands = (
        ("!dog", "Get a fun fact about dogs."),
        ("!dinosaur", "Get a fun fact about dinosaurs."),
    )

    fun_description = "\n".join([f"{cmd} - {desc}" for cmd, desc in fun_commands])
    embed.add_field(name="Fun", value=fun_description, inline=False)

    await ctx.send(embed=embed)


#--#
#AUDIO COMMANDS
#--#

#Command - !Play
@bot.command()
async def play(ctx, *, search: str, queue=False):
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel to use this command.")
        return

    voice_channel = ctx.author.voice.channel

    permissions = voice_channel.permissions_for(ctx.me)
    if not permissions.connect or not permissions.speak:
        await ctx.send("I don't have permission to join or speak in that voice channel.")
        return

    voice_client = ctx.guild.voice_client
    if voice_client is None:
        voice_client = await voice_channel.connect()

    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'default_search': 'ytsearch'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search, download=False)
        if info is None:
            await ctx.send('Invalid search query provided, please try again!')

        song = {
            'title': info['entries'][0]['title'],
            'url': info['entries'][0]['url'],
        }

        if not queue:
            await log_command_usage(ctx)

        if voice_client.is_playing() or voice_client.is_paused():
            queues[ctx.guild.id].append(song)
            await ctx.send(f"Added to the queue: {song['title']}")
        else:
            await start_playing(ctx, voice_client, song)

async def start_playing(ctx, voice_client, song):
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    source = discord.FFmpegOpusAudio(executable="ffmpeg", source=song['url'], **ffmpeg_options)

    def after_playing(error):
        if len(queues[ctx.guild.id]) > 0:
            next_song = queues[ctx.guild.id].pop(0)
            asyncio.run_coroutine_threadsafe(start_playing(ctx, voice_client, next_song), bot.loop)
        else:
            asyncio.run_coroutine_threadsafe(voice_client.disconnect(), bot.loop)

    voice_client.play(source, after=after_playing)
    await ctx.send(f"Now playing: {song['title']}")
  
#--#

#Command - !skip
@bot.command()
async def skip(ctx):
    await log_command_usage(ctx)
    voice_client = ctx.guild.voice_client
    if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
        voice_client.stop()
        await ctx.send("Skipped the current song.")
    else:
        await ctx.send("There's no song playing right now.")

#--#

#Command - !q
@bot.command()
async def q(ctx):
    await log_command_usage(ctx)
    queue = queues.get(ctx.guild.id, [])
    if not queue:
        await ctx.send("There are no songs in the queue.")
        return

    queue_text = "Songs in the queue:\n"
    for idx, song_info in enumerate(queue, start=1):
        queue_text += f"{idx}. {song_info['title']}\n"

    await ctx.send(queue_text)

#--#

#Command - !Stop
@bot.command()
async def stop(ctx):
    await log_command_usage(ctx)
    voice_channel = ctx.author.voice.channel
    if voice_channel is None:
        await ctx.send("You need to be in a voice channel to use this command.")
        return
    voice_client = ctx.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
    else:
        await ctx.send("I'm not connected to a voice channel.")

#--#

#Command - !Random_Song

# Predefined YouTube playlist URL
playlist_url = "https://www.youtube.com/playlist?list=PLtg6VBytbdL4O6cpBMbAoliCKLcddtHLF"

@bot.command()
async def random_song(ctx):
    await log_command_usage(ctx)
    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': False, 'extract_flat': True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

        if 'entries' not in info:
            await ctx.send('Invalid playlist URL provided, please try again!')
            return

        videos = info['entries']
        random_video = random.choice(videos)
        video_url = f"https://www.youtube.com/watch?v={random_video['id']}"

        await play(ctx, video_url)

#--#
#ADMINISTRATOR COMMANDS
#--#

# Command - !choose_role
class RoleSelector(Select):
    def __init__(self, roles):
        options = [
            discord.SelectOption(label=role.name, value=role.id)
            for role in roles
        ]
        super().__init__(placeholder="Select a role", min_values=1, max_values=len(roles), options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user if isinstance(interaction.user, discord.Member) else guild.get_member(interaction.user.id)
        
        updated_roles = []
        for role_id in self.values:
            role = discord.utils.get(guild.roles, id=int(role_id))
            updated_roles.append(role)
        
        for role in updated_roles:
            if role not in member.roles:
                await member.add_roles(role)
            else:
                await member.remove_roles(role)
        
        await interaction.response.send_message(f"Updated your roles: {', '.join([role.name for role in updated_roles])}", ephemeral=True)

class RoleView(View):
    def __init__(self):
        super().__init__()

@bot.command()
@commands.has_permissions(administrator=True)
async def choose_role(ctx, title: str, body: str, *role_ids: int):
    print("Choose role command executed") 
    roles = [ctx.guild.get_role(role_id) for role_id in role_ids]

    selector = RoleSelector(roles) 

    view = RoleView()
    view.add_item(selector)

    embed = discord.Embed(title=title, description=body, color=discord.Color.blurple())

    await ctx.send(embed=embed, view=view)

@choose_role.error
async def choose_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Sorry, you don't have permission to use this command.")

#--#
#Command - !Gulag
@bot.command()
@commands.has_permissions(administrator=True)
async def gulag(ctx, user: discord.Member):
    await log_command_usage(ctx)
    # Remove all roles from the user
    old_roles = user.roles.copy()
    await user.edit(roles=[])

    # Get the role ID you want to add
    role_id = 935639858813227048  # Replace with the ID of your desired role

    # Find the role object using the ID
    role = ctx.guild.get_role(role_id)

    # Add the role to the user
    await user.add_roles(role)

    # Send message to specified channel with the roles taken away from the user
    channel_id = 1091195568300236800  # Replace with the ID of the channel where you want the message to be sent
    channel = bot.get_channel(channel_id)
    
    # Construct the string of roles taken away from the user
    roles_str = ""
    for r in old_roles:
        if r != ctx.guild.default_role:
            roles_str += r.name + ", "
    roles_str = roles_str.rstrip(", ")  # Remove the trailing comma and space

    await channel.send(f"{user.mention} has been given the {role.name} role and had the following roles taken away: {roles_str}")

@gulag.error
async def gulag_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the necessary permissions to use this command.")

#--#

#Command - !Purge
@bot.command()
@commands.has_permissions(administrator=True)
async def purge(ctx, amount: int):
    await log_command_usage(ctx)
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
#FUN COMMANDS
#--#

#Command - Fun Facts | !dog & !dinosaur

openai.api_key = os.environ['Open_AI_Token']

async def get_chat_gpt_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

@bot.command()
async def dog(ctx):
    prompt = "What is an obscure dog fact that very little people know? Don't be repeditive."
    response = await get_chat_gpt_response(prompt)
    await ctx.send(response)

@bot.command()
async def dinosaur(ctx):
    prompt = "What is an obscure dinosaur fact that very little people know? Don't be repeditive."
    response = await get_chat_gpt_response(prompt)
    await ctx.send(response)

#--#

#Error Checks

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

#--#
#Login
bot.run(os.environ['GK_Token'])