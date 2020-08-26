import requests
import ast
import time
import preprocessor
from twilio.rest import Client
from tqdm import tqdm
from configs import (
    info_filename, 
    meta_filename, 
    parties, 
    twilio_sid,
    twilio_auth_token, 
    twilio_number,
    my_name, 
    my_number,
    destination_dir)

audio_dest_dir = destination_dir + 'audio/'
video_dest_dir = destination_dir +  'video/'

def get_num_episodes():
    while True:    
        try:
            with open(info_filename, 'r') as f:
                lines = f.readlines()
                #last line is blank.
                num_eps = len(lines) - 1    
                assert num_eps > 0
                break
        except:
            print('preprocessing...')
            preprocessor.preprocess()
    print('preprocessing completed')
    return num_eps
    
#returns true if download completed.
def download_or_resume(url, destination):
    try:
        with open(destination, 'ab') as f:
            headers = {}
            pos = f.tell()
            if pos > 0:
                headers['Range'] = f'bytes={pos}-'
            with requests.get(url, headers=headers, stream=True) as r:
                total_size = int(r.headers.get('content-length'))
                if pos >= total_size:
                    print('download completed')
                    return True
                r.raise_for_status()
                for chunk in tqdm(iterable = r.iter_content(chunk_size = 1024),
                                  total = (total_size - pos) // 1024,
                                  position = 0, leave = True):
                    f.write(chunk)
        print('download completed')
        return True
    except:
        return False
    
def download(url, destination):
    #mostly failures on my machine at least are due to my wi-fi being spotty,
    #so these increasing times try and catch it early if the wi-fi comes back
    #quickly and otherwise they just keep trying every 15 minutes. Be careful
    #if your conditions are very different than mine (mostly if you're not on
    #windows) to check progress intermittenly, because if there is a bug that 
    #shows up, you'll never make progress and just be caught in a loop. I lost
    #like 4 or 5 hours of download time that way. 
    def wait_time(num_iter):
        if num_iter == 0:
            return .02 #20 milliseconds
        elif num_iter == 1:
            return 5 #5 seconds
        elif num_iter == 2:
            return 60 #1 minute
        elif num_iter <= 5:
            return 300 #5 minutes
        else:
            return 900 #15 minutes
    num_iterations = 0
    while not download_or_resume(url, destination):
        #if the download failed, wait a while seconds before trying again
        time.sleep(wait_time(num_iterations))
        num_iterations += 1      
    
#Same numbering convention as always. 
#edit: I found the extra video. I should go back an recomment but I'm too lazy
#amyway, episode 97 in my convention, is a weird preview thing. So episodes 0
#to 96 in my convention are 1-97 on Harmontown.com, episode 97 doesn't exist,
#and episoded 98-360 are the same in my convention and online. And there's the 
#bonus episode 361 I have. So, that's the explanation. 
def download_episode_audio(episode_num):
    with open(info_filename, 'r') as f:
        line = f.readlines()[episode_num]
        data_list = ast.literal_eval(line)
    assert data_list[0] == episode_num
    title = data_list[1]
    audio_link = data_list[2]
    dest_filename = str(episode_num) + '-' + title + '_aud.mp3'
    dest = audio_dest_dir + dest_filename
    download(audio_link, dest)
    
def download_episode_video(episode_num):
    with open(info_filename, 'r') as f:
        line = f.readlines()[episode_num]
        data_list = ast.literal_eval(line)
    assert data_list[0] == episode_num
    title = data_list[1]
    video_link = data_list[3]
    if video_link is None:
        return
    dest_filename = str(episode_num) + '-' + title + '_vid.mp4'
    dest = video_dest_dir + dest_filename
    download(video_link, dest)
    
class download_action:
    audio = 'audio'
    video = 'video'
    party = 'party'
    action_types = [audio, video, party]
    
    def __init__(self, m_action_type, m_ep_num):
        self.action_type = m_action_type
        self.ep_num = m_ep_num
        assert self.action_type in download_action.action_types
        
    def get_audio_action(m_ep_num):
        return download_action(download_action.audio, m_ep_num)
    
    def get_video_action(m_ep_num):
        return download_action(download_action.audio, m_ep_num)
    
    def first_action():
        return download_action.get_audio_action(0)
    
    def log_cur(self):
        if self.action_type == download_action.party:
            print('basically done. yeet.')
        else:
            if self.action_type == download_action.audio:
                print('downloading audio for episode ' 
                      + str(self.ep_num) + '...')
            else:
                print('downloading video for episode '
                      + str(self.ep_num) + '...')
    
    def write(self):
        lines = []
        lines.append(self.action_type + '\n')
        if self.action_type != download_action.party:
            lines.append(str(self.ep_num) + '\n')
        with open(meta_filename, 'w') as f:
            f.writelines(lines)
            
    def act(self):
        self.log_cur()
        if self.action_type == download_action.audio:
            download_episode_audio(self.ep_num)
        elif self.action_type == download_action.video:
            download_episode_video(self.ep_num)
        self.write()

def get_next_action(num_episodes):
    with open(meta_filename, 'r') as f:
        lines = f.readlines()
        if len(lines) == 0:
            return download_action.first_action()
        cat = lines[0].strip()
        if cat == 'party':
            return download_action(download_action.party, None)
        else:
            num = int(lines[1])
            print(num_episodes)
            if num < num_episodes: #-1 bc indexed from 0
                if cat == download_action.audio:
                    return download_action.get_audio_action(num + 1)
                elif cat == download_action.video:
                    return download_action.get_video_action(num + 1)
                else:
                    return download_action(download_action.party, None)
            else:
                if cat == download_action.audio:
                    return download_action.get_video_action(0)
                else:
                    return download_action(download_action.party, None)    
               
                
#the scale of this script, especially with my slow wi-fi, is huge. Mostly, one 
#can get a ballapark status update by simply checking the drive one windows to 
#see what episodes have copied in what folders. Subparts within episodes are, 
#practically, negligible. This is just a way to alert the user that all files 
#have been downloaded.     
def party():
    msg = 'Hey ' + my_name + '! Your Harmontown Download has completed!'
    client = Client(twilio_sid, twilio_auth_token)
    client.messages.create(to=my_number, from_=twilio_number, body=msg)
    
#the structure of this file is intentionally convoluted to make unexpected 
#errors easy to work with. If you get stopped half-way through by whatever it
#may be that stops you, all you have to do is keep running this. If you party
#though, running this an extra time will send you another text. 
def download_harmontown():
    #this implictly handles preprocessing
    number_of_episodes = get_num_episodes() 
    cur_action = get_next_action(number_of_episodes)
    while cur_action.action_type != download_action.party:
        cur_action.act()
        cur_action = get_next_action(number_of_episodes)
    cur_action.write() #this is to write the final party action. 
    if parties:
        party()
        
#the data integrity code here is not the best. It's likely a download or two
#might fail. If that happens, you can literally just comment out this line and
#manually ask it to retry, after deleting the failed file. e.g. 
#   download_action.get_audio_action(17).act()
#be sure to change your meta file back to party() when your done though, just 
#for the sake of good practce
        
#edit: I'm gonna leave this comment in because it's useful to know, but I no 
#longer thing these downloads should fail badly under normal condition, I was
#observing a bug because the first version of the preprocessor forgot to strip
#the titles of colons. 
        
#edit #2: There was an error with the download of episode 49 (joe-jackson...) 
#I don't know what caused it. I changed a good chunk of all the pre-processing 
#code between the first and second run. I'll probably never try from the top--
#that's kind of what half the code is designed to ensure. If it happens to you
#   download_action.get_audio_action(49).act()
#is all I ran, just like above. 
        
#edit #3: 296 also failed. And then I checked back later and it had worked. 
#Also a bug where I got a Permission error to write to the meta_file. My guess
#is that one's from not closing it. Besides that things seem to be working. 
        
download_harmontown()