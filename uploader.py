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
    oauth_token = config["Y.DISK"]["oauthtoken"]
    main_folder = config["Y.DISK"]["mainFolder"]
    return oauth_token, main_folder


def upload(file, token, target_folder):
    """
    Uploads specified file to the destination folder at disk using given token

    :param file: local file path
    :param token: Yandex OAuth token
    :param target_folder: path to target folder at Yandex.disk
    :return: 0 if success
    """
    filename = file.replace("/", "\\").split("\\")[-1]
    if target_folder[-1] != "/":
        target_folder += "/"
    invite = requests.get("https://cloud-api.yandex.net/v1/disk/resources/upload",
                          params=[("path", target_folder+filename)],
                          headers={"Authorization": "OAuth "+token})

    invite_response = invite.json()
    if invite.status_code != 200:
        raise Exception("Could not receive invitation link: {} - {} ({})".format(invite.status_code,
                                                                                 invite_response["error"],
                                                                                 invite_response["description"]))

    uploading = requests.request(invite_response["method"], invite_response["href"], data=open(file, 'rb'),
                                 headers={"Authorization": "OAuth " + token})
    if uploading.status_code == 201:
        return 0
    else:
        raise Exception("Could not upload: {} {} ({})".format(uploading.status_code, uploading.reason, uploading.text))


def auto_upload(file):
    """
    Uploads specified file according to the parameters at config.ini

    :param file: path of file to be uploaded
    :return: 0 if uploading succeeded
    """
    token, target_folder = parse_config()
    return upload(file, token, target_folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', nargs=1)
    args = parser.parse_args()
    auto_upload(args.image[0])
