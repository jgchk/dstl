import configparser
import os
import sys
import urllib.request

import colorthief
import pylast
import wordcloud
import random

config = configparser.ConfigParser()
tags = {}
tag_albums = {}


def write_config():
    config.write(open("config.ini", "w"))


def single_color_func(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
    color_ = tag_albums[word]
    return 'rgb({:.0f}, {:.0f}, {:.0f})'.format(color_[0], color_[1], color_[2])


if __name__ == "__main__":
    # Set up config
    if os.path.exists("config.ini"):
        config.read("config.ini")
    else:
        config["USER"] = {"Username": "", "Password": ""}
        config["API"] = {"ApiKey": "", "ApiSecret": ""}
        write_config()
        print("Created config.ini\nEnter login and API information before rerunning dstl")
        sys.exit(0)

    # Check for user stupidity
    if not config["USER"]:
        config["USER"] = {"Username": "", "Password": ""}
        write_config()
        print("Missing username and password in config.ini")
        sys.exit(1)
    if not config["USER"]["Username"]:
        print("Missing username in config.ini")
        sys.exit(1)
    if not config["USER"]["Password"]:
        print("Missing password in config.ini")
        sys.exit(1)
    if not config["API"]:
        config["API"] = {"ApiKey": "", "ApiSecret": ""}
        write_config()
        print("Missing API key and secret in config.ini")
        sys.exit(1)
    if not config["API"]["ApiKey"]:
        print("Missing API key in config.ini")
        sys.exit(1)
    if not config["API"]["ApiSecret"]:
        print("Missing API secret in config.ini")
        sys.exit(1)

    # Authenticate
    network = pylast.LastFMNetwork(api_key=config["API"]["ApiKey"],
                                   api_secret=config["API"]["ApiSecret"],
                                   username=config["USER"]["Username"],
                                   password_hash=pylast.md5(config["USER"]["Password"]))

    # Get some juicy info
    user = network.get_user(config["USER"]["Username"])
    tracks = user.get_top_tracks(cacheable=True)
    for track in tracks:
        album = track.item.get_album()
        color = None
        if album:
            picture_page = album.get_cover_image()
            if picture_page:
                filename = os.path.join("cache", picture_page.split('/')[-1])
                if not os.path.exists("cache"):
                    os.makedirs("cache")
                if not os.path.isfile(filename):
                    urllib.request.urlretrieve(picture_page, filename)
                    print(picture_page, filename)
                color = colorthief.ColorThief(filename).get_color()
            else:
                color = (255, 255, 255)
        else:
            color = (255, 255, 255)

        for tag in track.item.get_top_tags():
            tags[tag.item.name] = tags.get(tag.item.name, 0) + 1
            if tag.item.name not in tag_albums or random.random() < 0.1:
                tag_albums[tag.item.name] = color

    print(tags)
    print(tag_albums)

    cloud = wordcloud.WordCloud(width=800, height=600, color_func=single_color_func)
    cloud.generate_from_frequencies(tags)
    cloud.to_file("test.png")
