import glob
import json


def CreateSongList():
    path = r'C:/Users/MDiGG/PycharmProjects/Alfred/Music/*.webm'
    songList = glob.glob(path)
    songfile = {'url': songList}

    with open('music.json', 'w') as f:
        json.dump(songfile, f, indent=4)
