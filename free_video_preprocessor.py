import requests
import re
from configs import num_free_video_pages, harmontown_un, harmontown_pw

#The deal with this. There are some free videos on the harmontown websit that
#don't fall under the video tag. There are so few it would probably be faster
#to just add them in by hand but this is better if it's self-contained. If I 
#wanted to I could mod the configs so you could run this without a harmontown
#account, but the problem with that is that some of the other code could be 
#moded if I make this too customizable to steal. I mean, you could probably 
#figure it out, if you know a little python, but this seems fair to me. Plus, 
#if you want the free episodes, there are few enough to download them manually.
ht_free_videos_url = 'https://www.harmontown.com/category/freevideos/page/'
login_url = 'https://www.harmontown.com/wp-login.php'
ep_126_url = ('https://download.harmontown.com/video/' + 
              'harmontown-2014-11-01-final.mp4')

#This has the standard episode numbering convention.
def get_episode_num(useful_url):
    try:
        ep_ind = useful_url.index('episode')
        first_dash_ind = useful_url.index('-', ep_ind)
        second_dash_ind = useful_url.index('-', first_dash_ind + 1)
        section = useful_url[first_dash_ind + 1 : second_dash_ind]
        ep_num = int(section)
    except Exception:
        try: #this bug was sly. I didn't even fix it for the normal videos. 
            ep_ind = useful_url.index('episode')
            first_dash_ind = useful_url.index('-', ep_ind)
            second_dash_ind = useful_url.index('/', first_dash_ind + 1)
            section = useful_url[first_dash_ind + 1 : second_dash_ind]
            ep_num = int(section)
        except:
            return None
    return ep_num

def process_page(page_num):
    page_url = ht_free_videos_url + str(page_num) + '/'
    with requests.Session() as s:
        payload = {'log' : harmontown_un, 'pwd' : harmontown_pw}
        p = s.post(login_url, data = payload) #p is unused. 4 diagnostics.
        page_source = s.get(page_url, allow_redirects = True).text
    #haha rhyme
    vid_mids = [m.start() for m in re.finditer('episode', page_source)]
    def extract_url(mid_ind):
        acceptable = True
        up_count = 0
        try:       
            while page_source[mid_ind + up_count] != '"':
                up_count += 1
        except IndexError:
            #in this case, and the one below, the hecky algorithm to find all
            #instances of "video" hecked up and wasn't surrounded in quotation
            #marks. We just set up count to 0 and this will be rejected later.
            up_count = 0
            acceptable = False
        down_count = 0
        try:
            while page_source[mid_ind - down_count] != '"':
                down_count += 1
        except:
            down_count = 0
            acceptable = False
        section = page_source[mid_ind - down_count + 1 : mid_ind + up_count]
        if len(section) < 4 or not acceptable:
            return None
        if section[:4] == 'http':
            return section
        else:
            return None
    vid_urls = set()
    for vid_mid in vid_mids:
        extracted = extract_url(vid_mid)
        if not extracted is None:
            vid_urls.add(extracted)
    vids = {}
    for vid_url in vid_urls:
        episode_number = get_episode_num(vid_url)
        if not episode_number is None:
            vids[episode_number] = vid_url
    return vids
            
def preprocess():
    handled_vids = []
    #so, the basic algorithm that works, as far as I can tell, for all videos, 
    #works also for every free video EXCEPT FOR ONE. The naming conventions on
    #the website are (I'm guessing intentionally) maddeningly inconsistent. I
    #just decided to included it manually rather than rewrite the entire code-
    #base for a single download. 
    final_dict = {}
    final_dict[126] = ep_126_url
    with requests.Session() as s:
        payload = {'log' : harmontown_un, 'pwd' : harmontown_pw}
        p = s.post(login_url, data = payload) #p is unused. 4 diagnostics.
        #video url is a link to the Harmontown.com page containing the video
        def get_download_url(video_url):
            video_page_source = s.get(video_url).text
            download_description = video_page_source.index(
                '">Download this episode')
            back_count = 1
            while video_page_source[download_description - back_count] != '"':
                back_count += 1
            return video_page_source[download_description - back_count + 1 : 
                                     download_description]
        for page in range(1, num_free_video_pages + 1):
            print('preprocessing video page ' + str(page) + 
                  ' / ' + str(num_free_video_pages) + '...')
            video_links = process_page(page)
            for episode in video_links.keys():
                if not episode in handled_vids:
                    try:
                        m_download_url = get_download_url(video_links[episode])
                    except:
                        m_download_url = None
                    if not m_download_url is None:
                        final_dict[episode] = m_download_url
            print('video page preprocessing complete') 
    return final_dict