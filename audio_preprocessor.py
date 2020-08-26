import requests
import re
from configs import info_filename, backup_info_filename

#For simplicity, we gather all data from the FeedBurner page
feedburner_url = 'http://feeds.feedburner.com/HarmontownPodcast'
feedburner_source = requests.get(feedburner_url).text

title_start_indices = [m.end() for m in re.finditer('<title>', 
                                                      feedburner_source)]
#the first two <title> instances in the html source are page titles
episode_title_start_indices = title_start_indices[2:]
title_end_indices = [m.start() for m in re.finditer('</title>', 
                                                      feedburner_source)]

episode_title_end_indices = title_end_indices[2:]
assert len(episode_title_start_indices) == len(episode_title_end_indices)
num_episodes = len(episode_title_start_indices)

episode_title_start_indices.reverse()
episode_title_end_indices.reverse()

#so the episode number here doesn't correspond exactly to the episode number
#on Harmontown.com I don't know why as I'm writing this. Obviously Ad Nauseam
#is at the end. But there's an extra episode somewhere in the middle. 
def get_title(episode_num):
    raw_title = feedburner_source[episode_title_start_indices[episode_num]:
                                  episode_title_end_indices[episode_num]]
    possibly_dated_title = raw_title.strip().replace(' ', '-').lower()
    forbiden_title_chars = [',', '!', '?', '.', '"', ':', '/', '&', '+', '’']
    for m_char in forbiden_title_chars:
        possibly_dated_title = possibly_dated_title.replace(m_char, '')
    possibly_dated_title = possibly_dated_title.replace('--', '-')
    #I think this is irrelevant. Remnant of bug because their titles use some 
    #weird non-normal apostrophe. Ugh. That was an ugly one. 
    possibly_dated_title = possibly_dated_title.replace("'", "")
    #this might occasionally happen since I have to butcher so many characters
    possibly_dated_title = possibly_dated_title.replace('--', '-')
    if possibly_dated_title[-1] == ')':
        date_start = possibly_dated_title.index('(')
        return possibly_dated_title[:date_start - 1]
    else:
        return possibly_dated_title

titles = [get_title(num) for num in range(num_episodes)]

download_url_start = 'http://feedproxy.google.com/~r/HarmontownPodcast/~5/'
download_url_start_indices = [m.end() for m in re.finditer(download_url_start,
                                                           feedburner_source)]
assert len(download_url_start_indices) == num_episodes
download_url_start_indices.reverse()

#Same episode num spiel here as above. Not the Harmontown.com one.
def get_download_url(episode_num):
    counter = 0
    start_pt = download_url_start_indices[episode_num]
    while (feedburner_source[start_pt + counter : start_pt + counter + 4] 
           != '.mp3'):
        counter += 1
    section = feedburner_source[start_pt : start_pt + counter]
    return download_url_start + section + '.mp3'

download_urls = [get_download_url(num) for num in range(num_episodes)]

class harmontown_episode:
    def __init__(self, m_number, m_name, m_link):
        self.number = m_number
        self.name = m_name
        self.audio_link = m_link
        #this is a little bit bad form, but video links are only ever modified
        #in other python files, and all the episode creation is in this one.
        self.video_link = None
    
    def from_num(num):
        return harmontown_episode(num, titles[num], download_urls[num])
        
    def to_string(self):
        return str([self.number, self.name, self.audio_link, self.video_link])

episodes = [harmontown_episode.from_num(num) for num in range(num_episodes)]

def write():
    lines = [episodes[num].to_string() + '\n' for num in range(num_episodes)]
    with open(info_filename, 'w') as m_file:
        m_file.writelines(lines)
    with open(backup_info_filename, 'w') as m_file:
        m_file.writelines(lines)