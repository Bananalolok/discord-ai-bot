import nextcord
from nextcord.ext import commands
from src import ai
import config

messages={}
async def process():
    pass

async def process_chat(message: nextcord.Message):
    chat_id = str(message.author.id) if message.channel.type == nextcord.ChannelType.private else f"{message.channel.id}{message.author.id}"
    if chat_id not in messages:
        messages[chat_id] = []
    messages[chat_id].append({'role': 'user', 'content': message.content})
    chat_msgs = [{'role': 'system', 'content': config.chat_system_prompt}] + messages[chat_id]
    response = await ai.respond(chat_msgs)
    await message.reply(response)

class MessageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        print("message")
        if message.author == self.bot.user:
            return
        bot_mentioned = any(user == self.bot.user for user in message.mentions)
        if bot_mentioned or (message.reference and message.reference.resolved and message.reference.resolved.author == self.bot.user):
            print("stuff is happening")
            async with message.channel.typing():
                await process_chat(message)

def setup(bot):
    bot.add_cog(MessageCog(bot))
