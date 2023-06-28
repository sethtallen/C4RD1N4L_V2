import discord
from discord.utils import get
from environs import Env

import voice_synth

intents = discord.Intents.default()
intents.message_content = True
env = Env()
env.read_env()

discord_api_token = env.str('DISCORD_API_TOKEN')

client = discord.Client(intents=intents)

voice_synth.client = client

async def TargetedSpammingDetection(author_tag,message,recent_messages):
    if(str(message.author) == author_tag):
        recent_messages.pop(0)
        spam_count = 0
        for recent_message in recent_messages:
            if(str(recent_message.author) == author_tag and message.content in recent_message.content):
                spam_count = spam_count + 1
        
        if(spam_count > 2):
            return True
        else:
            return False
    else:
        return False

@client.event
async def on_ready():
    client.loop.create_task(voice_synth.CheckForUploads())
    print(f'We have logged in as {client.user}')   

@client.event
async def on_message(message):
    
    if(str(message.content).startswith('~rbvc')):
        if(str(message.content).split(" ")[1] == "models"):
            model_list = ""
            for model in voice_synth.config['models']:
                model_list = model_list + "\n" + model
            await message.reply(content=model_list)
        else:
            if(str(message.attachments) != "[]"):
                await voice_synth.VoiceConversion(message)

client.run(discord_api_token)