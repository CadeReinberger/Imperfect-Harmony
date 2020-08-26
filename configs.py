##############################################################################
##############################################################################
##                                                                          ##
##   ________  ________  ________   ________ ___  ________  ________        ##
##  |\   ____\|\   __  \|\   ___  \|\  _____\\  \|\   ____\|\   ____\       ##    
##  \ \  \___|\ \  \|\  \ \  \\ \  \ \  \__/\ \  \ \  \___|\ \  \___|_      ##
##   \ \  \    \ \  \\\  \ \  \\ \  \ \   __\\ \  \ \  \  __\ \_____  \     ##
##    \ \  \____\ \  \\\  \ \  \\ \  \ \  \_| \ \  \ \  \|\  \|____|\  \    ##
##     \ \_______\ \_______\ \__\\ \__\ \__\   \ \__\ \_______\____\_\  \   ##
##      \|_______|\|_______|\|__| \|__|\|__|    \|__|\|_______|\_________\  ##
##                                                            \|_________|  ##
##                                                                          ##
##############################################################################
##############################################################################
                              
#you don't have to change this param, it will create the files, but you can
#if you want it to be named somethign else                                        
info_filename = 'episodes.txt' #stores data about episodes of Harmontown

#this is useful for ad hoc mods to save yourself some time. Maybe just 4 devs.
backup_info_filename = 'backup.txt' #backup of info_filename

#This one you have to create. Just define it in this folder, and make it blank.
meta_filename = 'completed.txt' #stores data about the progress of downloading

#This you have to update with your Harmontown account. You must have one. This
#program is for people who subscribe, but want to download all of it and don't
#want to go through the trouble of doing it by hand. It's literally $5 a month.
harmontown_un = 'example_un'
harmontown_pw = 'example_pw'

#This is the number right now. As of currently, it seems like Harmontown will 
#not air again, so this seems that it will not change. But, if more episodes 
#ever did some day come to be, and more pages of video exist, you could modify
#this. Also, if Harmontown ever redoes its website, this whole script will
#assureduly fail. It works as of May 2020. 
num_video_pages = 23
num_free_video_pages = 2 #free videos are separate on the ht website. 

#Because of the immense amount of time this download could take, if you have a
#twilio and want to use it, you can put in your info here, and opt to send an
#sms message to yourself (a text) when your download is done. 
parties = True #True or false based on whether you send a text or not
#these don't matter if parties is False
twilio_sid = 'your_twilio_sid_here'
twilio_auth_token = 'your_twilio_auth_token'
twilio_number = '+15555555555' #the number of your twilio
my_number = '+15558675309' #your phone number
my_name = 'your_name' #name you want the notification text to call you

#this is the folder that you want to save Harmontown to. I recommend unless 
#your cpu has a bunch of storage and you plan on keeping it forever you make
#this an external hard drive. This MUST have two subfolders in it, one callled
#"audio" and the other called "video", or the program won't work. Use /.
destination_dir = 'D:/harmontown/'