#--#
#Open AI Functions | Disabled
#--#

#IMPORTS

import os
import openai
from discord.ext import commands

#--#

class CMDOAI(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

#Command - Fun Facts | !dog & !dinosaur

@commands.command()
async def get_chat_gpt_response(prompt):
    openai.api_key = os.environ['Open_AI_Token']
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

@commands.command()
async def dog(ctx):
    prompt = "What is an obscure dog fact that very little people know? Don't be repeditive."
    response = await get_chat_gpt_response(prompt)
    await ctx.send(response)

@commands.command()
async def dinosaur(ctx):
    prompt = "What is an obscure dinosaur fact that very little people know? Don't be repeditive."
    response = await get_chat_gpt_response(prompt)
    await ctx.send(response)

#--#
async def setup(bot):
  await bot.add_cog(CMDOAI(bot))