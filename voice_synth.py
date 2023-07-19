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

@tasks.loop(seconds=4)
async def CheckForUploads():
    while True:
        await asyncio.sleep(10)
        directory_contents = os.listdir(processed_directory)
        if(len(directory_contents) > 0):
            print('Found files to upload')
            await UploadProcessedAudioFiles(directory_contents)

async def VoiceConversion(message,conversion_parameters):
    if(VerifyUserWhitelist(message) == True):
        await DownloadUnprocessedAudioFile(message, conversion_parameters)

async def DownloadUnprocessedAudioFile(message, conversion_parameters):
        attachment = message.attachments[0]
        filename = str(attachment).split('/')[-1]
        filename = filename.split('.')
        filename = filename[0] + "_" + str(randint(0,999)) + "." + filename[1]
        try:
            print('Attempting download of' + str(attachment))
            await attachment.save(unprocessed_directory + filename)
            GenerateConversionDetails(filename, conversion_parameters)
        except Exception as e:
            print(e)
            return False

#Drops a JSON file to the backend
def GenerateConversionDetails(filename,conversion_parameters):
    with open(unprocessed_directory + filename +'.json', 'w') as f:
        json.dump(conversion_parameters, f)

async def UploadProcessedAudioFiles(directory_contents):
    for file in directory_contents:
        converted_parameters = False
        file_extension = file.split('.')[-1]
        if(file_extension != 'json'):
            with open(processed_directory+file+'.json' ,'r') as parameter_file:
                converted_parameters = json.load(parameter_file)
                parameter_file.close()

            if(converted_parameters != False):
                attachment = discord.File(processed_directory + file)
                channel = client.get_channel(converted_parameters['channel_id'])
                user = await client.fetch_user(converted_parameters['user_id'])
                await channel.send(user.mention + "", file=attachment)
                os.remove(processed_directory + file)
                os.remove(processed_directory + file + '.json')

def VerifyUserWhitelist(message):
    
    #Discord introduced tagless usernamse. Now all usernames end with #0 to the bot.
    author = str(message.author)[:-2]
    if(author in config['whitelist']):
        return True
    else:
        print('Invalid user ID')
        return False