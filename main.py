import nextcord
from nextcord.ext import commands
import config

bot = commands.Bot(command_prefix='!', intents=nextcord.Intents.all(), default_guild_ids=[1066217739565420554])

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.slash_command(name='hello', description="Says Hello back", dm_permission=True)
async def hello(inter: nextcord.Interaction):
    await inter.send(f'Hello {inter.user.mention}!')

bot.load_extension("cogs.image")
bot.load_extension("cogs.chat")
bot.run(config.bot_token)
