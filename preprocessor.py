import time

#this should take maybe 15 or 20 minutes. Maybe a little more or less, based 
#on your device and internet speeds. Go watch an episode of Community or 
#sometthing. This will slow your whole script a bit.
def preprocess():
    #This actually does the audio preprocessing
    print('preprocessing audio...')
    import audio_preprocessor
    print('audio preprocessing completed')
    time.sleep(.5) #to fix a printing bug
    
    import video_preprocessor
    
    print('preprocessing video...')
    vid_adresses = video_preprocessor.preprocess()    
    for k in vid_adresses.keys():
        audio_preprocessor.episodes[k].video_link = vid_adresses[k]
    print('video preprocessing completed')
    
    print('preprocessing free video...')
    import free_video_preprocessor
    vid_adresses = free_video_preprocessor.preprocess()    
    for k in vid_adresses.keys():
        audio_preprocessor.episodes[k].video_link = vid_adresses[k]

    audio_preprocessor.write()
    
    print('preprocessing completed')