from infer_cli import vc_single
from time import sleep
import os
import json

unprocessed_dir = "discord/unprocessed/"
processed_dir = "discord/processed/"
os.chdir("/home/thinkingmachine/rbvc")

with open('model_mappings.json') as f:
    model_map = json.load(f)

while True:
    directory_contents = os.listdir(unprocessed_dir)
    if(len(directory_contents) > 0):
        for file in directory_contents:
            file_extension = file.split('.')[-1]
            #sometimes it tries to grab the json before transfer completes
            if len(directory_contents) < 2:
                break
            #can come in as a .wav, .mp3, etc. If its not a .json, it has a json file that matches
            if(file_extension != 'json'):
                parameters=[]
                with open(unprocessed_dir+file+'.json' ,'r') as parameter_file:
                    parameters = json.load(parameter_file)

                transpose = parameters['transpose']
                selected_model = parameters['model']
                file_index = 'logs/' + model_map[selected_model] + '/added_IVF213_Flat_nprobe_1_v1.index' #TODO need to fix this to look dynamically for the .index
                model_path = 'weights/' + model_map[selected_model] + '.pth'

                vc_single(sid=0,input_audio_path=unprocessed_dir + file,f0_up_key=transpose,f0_file=None,f0_method="harvest",file_index=file_index,file_index2="",index_rate=1,filter_radius=3,resample_sr=0,rms_mix_rate=0,model_path=model_path,output_path = processed_dir+file)
                
                #Delete the files from unprocessed
                if(os.path.isfile(processed_dir+file)):
                    os.remove(unprocessed_dir+file)
                    os.rename(unprocessed_dir+file+'.json',processed_dir+file+'.json')