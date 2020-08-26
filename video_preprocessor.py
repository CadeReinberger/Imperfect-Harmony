import requests
import re
from configs import harmontown_un, harmontown_pw, num_video_pages

harmontown_videos_url = 'https://www.harmontown.com/category/videos/page/'
login_url = 'https://www.harmontown.com/wp-login.php'

#I mentioned when gathering the data that there's an episode I proccessed that
#isn't on Harmontown.com. It's before the video episodes start, and since we
#index from 0, that cancels out. So we don't have to worry about it. And we 
#also don't have to worry about the one on the end, obviously.
def get_episode_num(useful_url):
    try:
        ep_ind = useful_url.index('episode')
        first_dash_ind = useful_url.index('-', ep_ind)
        second_dash_ind = useful_url.index('-', first_dash_ind + 1)
        section = useful_url[first_dash_ind + 1 : second_dash_ind]
        ep_num = int(section)
    except Exception:
        try:
            ep_ind = useful_url.index('episode')
            first_dash_ind = useful_url.index('-', ep_ind)
            second_dash_ind = useful_url.index('/', first_dash_ind + 1)
            section = useful_url[first_dash_ind + 1 : second_dash_ind]
            ep_num = int(section)
        except:
            return None
    return ep_num

def process_page(page_num):
    page_url = harmontown_videos_url + str(page_num) + '/'
    page_source = requests.get(page_url, allow_redirects = True).text
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
    final_dict = {}
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
        for page in range(1, num_video_pages + 1):
            print('preprocessing video page ' + str(page) + 
                  ' / ' + str(num_video_pages) + '...')
            video_links = process_page(page)
            for episode in video_links.keys():
                if not episode in handled_vids:
                    final_dict[episode] = get_download_url(
                        video_links[episode])
            #'d.' is off-style but makes println same width as above. Yeet.
            print('video page preprocessing completed.') 
    return final_dict