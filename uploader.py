import requests
from config import Configurator
import argparse


class Uploaer:
    def __init__(self, oauth_token, mainfolder):
        self.oauth_token, self.target_folder = oauth_token, mainfolder

    def upload(self, file):
        """
        Uploads specified file to the destination folder at disk using given token

        :param file: local file path
        :return: path to file if success
        """
        filename = file.replace("/", "\\").split("\\")[-1]
        if self.target_folder[-1] != "/":
            self.target_folder += "/"
        invite = requests.get("https://cloud-api.yandex.net/v1/disk/resources/upload",
                              params={"path": self.target_folder + filename},
                              headers={"Authorization": "OAuth " + self.oauth_token})

        invite_response = invite.json()
        if invite.status_code != 200:
            raise Exception("Could not receive invitation link: {} - {} ({})".format(invite.status_code,
                                                                                     invite_response["error"],
                                                                                     invite_response["description"]))

        uploading = requests.request(invite_response["method"], invite_response["href"], data=open(file, 'rb'),
                                     headers={"Authorization": "OAuth " + self.oauth_token})
        if uploading.status_code == 201:
            return self.target_folder + filename
        else:
            raise Exception(f"Could not upload: {uploading.status_code} {uploading.reason} ({uploading.text})")

    def publish(self, filepath):
        pub = requests.request("put", "https://cloud-api.yandex.net/v1/disk/resources/publish",
                               params={"path": filepath},
                               headers={"Authorization": "OAuth " + self.oauth_token})
        jsn = pub.json()
        public_info = requests.request(jsn["method"], jsn["href"],
                                       headers={"Authorization": "OAuth " + self.oauth_token})
        public_link = public_info.json()["public_url"]
        return public_link


def smart_upload(file):
    """
    Uploads specified file according to the parameters at config.ini

    :param file: path of file to be uploaded
    :return: 0 if uploading succeeded
    """
    config = Configurator()
    token, target_folder = config.uploader()
    uploader = Uploaer(token, target_folder)
    return uploader.publish(uploader.upload(file))


def get_direct_link(public_file_link):
    """
    Obtains a direct link to the content, stored at specified link
    :param public_file_link:
    :return: direct link
    """
    api_endpoint = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'
    pk_request = requests.get(api_endpoint.format(public_file_link))
    return pk_request.json()['href']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', nargs=1)
    args = parser.parse_args()
    indirect_link = smart_upload(args.image[0])
    direct_link = get_direct_link(indirect_link)
    print(f"Indirect link: {indirect_link}\nDirect link:{direct_link}")
