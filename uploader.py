import requests
from configparser import ConfigParser
import argparse


def parse_config():
    """
    Configuration parser
    Reads parameters from config.ini associated with uploader module

    :return: yandex oauth_token, main_folder at disk, backup flag
    """
    config = ConfigParser()
    config.read("config.ini")
    oauth_token = config["Y.DISK"]["OAuthToken"]
    main_folder = config["Y.DISK"]["mainFolder"]
    backup = config.getboolean("Y.DISK", "backup")
    return oauth_token, main_folder, backup


def upload(file, token, target_folder):
    filename = file.replace("/", "\\").split("\\")[-1]
    if target_folder[-1] != "/":
        target_folder += "/"
    invite = requests.get("https://cloud-api.yandex.net/v1/disk/resources/upload",
                          params=[("path", target_folder+filename)],
                          headers={"Authorization": "OAuth "+token})


if __name__ == '__main__':
    print("aboba")