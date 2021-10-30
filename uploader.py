import requests
from configparser import ConfigParser


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
