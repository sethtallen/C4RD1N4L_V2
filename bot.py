import discord
from discord.utils import get
from environs import Env
import json

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

async def ListRBVCModels(message):
    model_list = ""
    for model in voice_synth.config['models']:
        model_list = model_list + "\n" + model
    await message.reply(content=model_list)

async def VerifyRBVCParameters(message):
    
    parameters = message.content.split(' ')

    #Parameter 1 is the model name
    if(parameters[1] not in voice_synth.config['models']):
        print('Model unavailable')
        await message.reply('Please provide a valid model.')
        return False
    
    if(parameters[2].lstrip('-').isdigit() == False):
        print('Transpose is not a number')
        await message.reply('Please provide an integer transpose value')
        print(type(parameters[2]))
        return False

    #Parameter 3 is the seperation model
    if(int(parameters[3]) not in [0,1,2]):
        print('invalid seperation parameter')
        await message.reply('Please provide a valid seperation parameter.')
        return False
    
    parameters = {
        'model':parameters[1],
        'transpose':int(parameters[2]),
        'seperation_model':int(parameters[3]),
        'channel_id':message.channel.id,
        'user_id':message.author.id
    }

    return parameters

async def VerifyRBVCAttachment(message):
    
    valid_extensions = ['mp3','wav','flac']

    #TODO add support for multiple conversions  
    if len(message.attachments) > 1:
        await message.reply('Please upload only one attachment')
        return False
    else:
        attachment = message.attachments[0]
        file_extension = str(attachment).split(".")
        if(file_extension[-1] not in valid_extensions):
            print('Invalid attachment type')
            await message.reply('Please upload a valid attachment')
            return False
    return True

async def VerifyRBVCWhitelist(message):

    #Discord introduced tagless usernamse. Now all usernames end with #0 to the bot.
    author = str(message.author)[:-2]

    if(author in voice_synth.config['whitelist']):
        return True
    else:
        print('Invalid user ID')
        await message.reply('You are not authorized to use RBVC')
        return False

@client.event
async def on_ready():       
    client.loop.create_task(voice_synth.CheckForUploads())
    print(f'We have logged in as {client.user}')   

@client.event
async def on_message(message):
    
    if(str(message.content).startswith('~rbvc')):

        whitelisted = await VerifyRBVCWhitelist(message)

        if(whitelisted):
            #List models
            if(str(message.content).split(" ")[1] == "models"):
                ListRBVCModels(message)
            
            elif(str(message.attachments) != "[]"):
                
                conversion_parameters = await VerifyRBVCParameters(message)
                valid_attachment = await VerifyRBVCAttachment(message)

                if(conversion_parameters != False and valid_attachment == True):
                    await voice_synth.VoiceConversion(message,conversion_parameters)

client.run(discord_api_token)