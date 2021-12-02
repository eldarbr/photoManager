import requests
from config import Configurator
import argparse
from resizer import suffixes


class Uploaer:
    def __init__(self, oauth_token, mainfolder):
        self.oauth_token, self.target_folder = oauth_token, mainfolder

    def upload(self, file):
        """
        Uploads specified file to the destination folder at disk using given token

        :param file: local file path
        :return: json response for uploading
        """
        filename = file.replace("/", "\\").split("\\")[-1]
        suffix = filename.split(".")[0].split("_")[-1]
        if suffix not in suffixes:
            suffix = "unclassified"
        if self.target_folder[-1] != "/":
            self.target_folder += "/"
        remote_filepath = self.target_folder + suffix + "/" + filename
        invite = requests.get("https://cloud-api.yandex.net/v1/disk/resources/upload",
                              params={"path": remote_filepath},
                              headers={"Authorization": "OAuth " + self.oauth_token})

        invite_response = invite.json()
        if invite.status_code != 200:
            raise Exception("Could not receive invitation link: {} - {} ({})".format(invite.status_code,
                                                                                     invite_response["error"],
                                                                                     invite_response["description"]))

        uploading = requests.request(invite_response["method"], invite_response["href"], data=open(file, 'rb'),
                                     headers={"Authorization": "OAuth " + self.oauth_token})
        if uploading.status_code == 201:
            return remote_filepath
        else:
            raise Exception(f"Could not upload: {uploading.status_code} {uploading.reason} ({uploading.text})")

    def publish(self, filepath):
        pub = requests.request("put", "https://cloud-api.yandex.net/v1/disk/resources/publish",
                               params={"path": filepath},
                               headers={"Authorization": "OAuth " + self.oauth_token})
        jsn = pub.json()
        public_info = requests.request(jsn["method"], jsn["href"],
                                       headers={"Authorization": "OAuth " + self.oauth_token})
        json_response = public_info.json()
        return json_response

    def get_direct_link(self, path):
        meta = requests.get(f"https://cloud-api.yandex.net/v1/disk/resources?path={path}",
                            headers={"Authorization": "OAuth " + self.oauth_token})
        if meta.status_code == 200:
            return meta.json()["file"]
        else:
            raise Exception(f"Could not get file: {meta.text}")


def smart_upload(file):
    """
    Crucial UPLOAD function
    Uploads specified file according to the parameters at config.ini

    :param file: path of file to be uploaded
    :return: 0 if uploading succeeded
    """
    config = Configurator()
    token, target_folder = config.uploader()
    uploader = Uploaer(token, target_folder)
    json_response = uploader.publish(uploader.upload(file))
    return json_response#["public_url"]


def get_direct_link(public_file_link):
    """
    Obtains a direct link to the content, stored at specified link
    :param public_file_link:
    :return: direct link
    """
    api_endpoint = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'
    pk_request = requests.get(api_endpoint.format(public_file_link))
    try:
        href = pk_request.json()['href']
    except KeyError:
        return pk_request.json()
    return href


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', nargs=1)
    args = parser.parse_args()
    indirect_link = smart_upload(args.image[0])
    # direct_link = get_direct_link(indirect_link)
    # print(f"Indirect link: {indirect_link}\nDirect link:{direct_link}")
    print(indirect_link)
