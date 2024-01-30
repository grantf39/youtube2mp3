#!/usr/bin/env python3

#NOTE Run in python3 for least headaches

# importing packages
from pytube import YouTube
import os
from pathlib import Path
import sys
import subprocess

# For VideoFileClip reader
from moviepy.editor import *

# import urllib3
import urllib.request

from io import StringIO, BytesIO
from PIL import Image

# Eyed3:
import eyed3
from eyed3.id3.frames import ImageFrame

# Mutagen:
# from mutagen.mp3 import MP3
# from mutagen.id3 import ID3, APIC, error

# http = urllib3.PoolManager()
img_data = None
url = ""
thumbnail_image = None

def get_img_data(urls):
    global img_data

# INPUT: StreamQuery object from pytube
# OUTPUT: highest abr video an rate int in kbps
def get_highest_abr(videos):
    print(videos)

    # Just in cae no abr to check, set to first
    max_quality_video = videos[0]
    max_rate = 0
    

    # Iterate through StreamQuery object
    for video in videos:
        # iterate through the string and turn first numeric digits to ints
        rate_str = ""
        print(video)        
        if video.abr:
            for i in video.abr:
                if i.isdigit():
                    rate_str = rate_str + i
                else:
                    # assume no more numbers and break
                    break
            rate = int(rate_str)
            print("Rate: ", rate, "kbps")

            # try:
            #     print("fps: ", video.fps)
            #     # check if max
            #     if rate > max_rate:
            #         max_rate = rate
            #         max_quality_video = video
            # except:
            #     print("error- has no fps")

            if rate > max_rate:
                max_rate = rate
                max_quality_video = video

    print("Max Average Bit Rate: ", max_rate)
    print("Max qual video:")
    print(max_quality_video)

    return max_quality_video, max_rate


if __name__ == '__main__':

    # ADD THUMBNAIL 
    # print("READING: ", os.path.basename(new_file).replace(' ', '\\ '))
    # print("READING: ", "./test.mp3")
    # dirs = os.listdir()
    # for file in dirs:
    #     print(file)
    # exit()

    if len(sys.argv)>1:
        url = sys.argv[1]
    else:
        url = str(input("Enter the URL of the video you want to download: \n>> "))
    # url input from user
    yt = YouTube(url)
    
    
    videos = yt.streams.all()
    # Need vieo only since we need for initial mp4 conversion
    # videos = yt.streams.filter(only_video=True)
    # videos = yt.streams.filter(only_audio=True)
    # print("VIDEOS: ")
    # print(videos)

    max_quality_video, max_rate = get_highest_abr(videos)

    # max_quality_video.fps="30fps"


    # Get thumbnail DATA
    # print("Thumbnail: ", yt.thumbnail_url)
    # r = http.request('GET', yt.thumbnail_url)
    # print(r.status)

    # stuff = BytesIO(r.data)
    # thumbnail_image = Image.open(stuff)
    # print(thumbnail_image.size)
    print("Thumbnail: ", yt.thumbnail_url)
    response = urllib.request.urlopen(yt.thumbnail_url)
    thumbnail_image = response.read()
    # print(thumbnail_image.size)
    
    # check for destination to save file
    # print("Enter the destination (leave blank for current directory)")
    # destination = str(input(">> ")) or '.'
    # NOTE: keep as current directory for now
    destination = "."
    download_destination = os.path.join(destination, "Downloads")

    # Check if output src file exists
    if not os.path.exists(download_destination):
        print("Creating Destination: ", download_destination)
        os.mkdir(download_destination)
    else:
        print("Destination Exists ", download_destination)
        

    # download the file as mp4 or wemw
    out_file = max_quality_video.download(output_path=download_destination)
    print("OUT_FILE: ", out_file)
    
    # NOTE: Simply changing the file extension is not a valid way to convert to mp3, does nt properly add
    # MPEG frames and tags
    base, ext = os.path.splitext(out_file)
    # video = VideoFileClip(out_file)
    video = AudioFileClip(out_file)
    print("videoclip: ", video)

    # Write new audio file and 
    # new_file = base + '.mp3'
    new_file = os.path.join(download_destination, base + '.mp3')
    print("NEWFILE: ", new_file)
    # video.audio.write_audiofile(new_file)
    video.write_audiofile(new_file)
    # result of success
    print(yt.title + " has been successfully downloaded.")

    # DELETE MP4
    video.close()
    # os.remove(out_file)
    # print("DELETED: ", out_file)

    audiofile = eyed3.load(new_file)
    print("audio: ", audiofile)

    # adding ID3 tag if it is not present
    if (audiofile.tag == None):
        print("INITIALIZING TAG")
        audiofile.initTag()
    audiofile.tag.album = Path(new_file).stem


    print("AUDIO TAG:")
    print(audiofile.tag, audiofile.tag.album)

    # audiofile.tag.images.set(ImageFrame.FRONT_COVER, thumbnail_image, 'image/jpeg')
    audiofile.tag.images.set(3, thumbnail_image, 'image/jpeg', u"cover")
    audiofile.tag.save(version=eyed3.id3.ID3_V2_3)
