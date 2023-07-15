import discord
from discord.ext import tasks
import os
import asyncio
import json
from random import randint

client = None

conversion_queue = []

unprocessed_directory = "eyai/discord/unprocessed/"
processed_directory = 'eyai/discord/processed/'
os.chdir("/home/geiru/C4RD1N4L_V2")

with open('config.json') as json_file:
    config = json.load(json_file)

print(config['models'])
print(config['whitelist'])

@tasks.loop(seconds=10)
async def CheckForUploads():
    while True:
        await asyncio.sleep(10)
        directory_contents = os.listdir(processed_directory)
        if(len(directory_contents) > 0):
            print('Found files to upload')
            await UploadProcessedAudioFiles(directory_contents)

async def VoiceConversion(message):
    if(VerifyUserWhitelist(message) == True and VerifyAttachment(message) == True):
        conversion_params = VerifyMessageParameters(message)
        print(conversion_params)
        if(conversion_params != False):
            await DownloadUnprocessedAudioFile(message, conversion_params)

async def DownloadUnprocessedAudioFile(message, conversion_params):
        attachment = message.attachments[0]
        filename = str(attachment).split('/')[-1]
        filename = filename.split('.')
        filename = filename[0] + "_" + str(randint(0,999)) + "." + filename[1]
        try:
            print('Attempting download of' + str(attachment))
            await attachment.save(unprocessed_directory + filename)
            GenerateConversionDetails(filename, conversion_params)
            conversion_queue.append({'channel':message.channel,'filename':filename})
        except Exception as e:
            print(e)
            return False

def GenerateConversionDetails(filename,conversion_params):
    with open(unprocessed_directory + filename +'.json', 'w') as f:
        json.dump(conversion_params, f)

async def UploadProcessedAudioFiles(directory_contents):
    for file in directory_contents:
        for member in conversion_queue:
            print(file)
            print(member['filename'])
            if(file == member['filename']):
                try:
                    print('Match found')
                    attachment = discord.File(processed_directory + file)
                    channel = client.get_channel(member['channel'].id)
                    await channel.send(file=attachment)
                    os.remove(processed_directory + file)
                except:
                    print('issue with uploading')

def VerifyUserWhitelist(message):
    
    #Discord introduced tagless usernamse. Now all usernames end with #0 to the bot.
    author = str(message.author)[:-2]
    if(author in config['whitelist']):
        return True
    else:
        print('Invalid user ID')
        return False

def VerifyMessageParameters(message):
    parameters = message.content.split(' ')
    if(len(parameters) > 3):
        print('Too many parameters')
        return False
    if(parameters[1] not in config['models']):
        print('Model unavailable')
        return False
    return {'transpose':parameters[2],'model':parameters[1]}

def VerifyAttachment(message):
    if len(message.attachments) > 1:
        return False
    else:
        attachment = message.attachments[0]
        file_extension = str(attachment).split(".")
        if(file_extension[-1] not in ['mp3','wav']):
            print('Invalid attachment type')
            return False
    return True
