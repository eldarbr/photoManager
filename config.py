from configparser import ConfigParser
import os
from my_types import ExportPreset


class Configurator:
    
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("config.ini")

    def resizer(self):
        """
        Configurator for resizer module
        :return: list of ExportPresets, temp folder path
        """
        export_presets = []

        for preset in self.config["RESIZER"]["newSizes"].replace(" ", "").split(","):
            splitted = preset.split(":")
            if len(splitted) == 3:
                export_presets += [ExportPreset(*splitted)]
            else:
                raise Exception(f"Error parsing config for resizer: export preset {preset} does not match format!")
        if len(export_presets) != 3:
            raise Exception("Error parsing config for resizer: number of presets in config file is inappropriate!")
        temp_folder = self.config["GENERIC"]["temporaryFolder"].replace("/", "\\")
        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)
        return export_presets, temp_folder

    def uploader(self):
        """
        Configurator for uploader module
        :return: OAuthToken, backup, deleteTemp, mainFolder settings
        """
        return self.config["Y.DISK"]["OAuthToken"], \
               self.config["Y.DISK"]["mainfolder"]

    def oauth_read(self):
        """
        Configurator for oauth module
        :return: OAuthID, OAuthToken, expires_at settings
        """
        return self.config["Y.DISK"]["OAuthID"], \
               self.config["Y.DISK"]["OAuthToken"], \
               self.config["Y.DISK"]["expires_at"]

    def oauth_write(self, token, expiration):
        """
        Re-configurator for oauth module
        :param token: new token to be saved
        :param expiration: new expiration time to be saved
        """
        self.config.set("Y.DISK", "OAuthToken", token)
        self.config.set("Y.DISK", "expires_at", expiration)
        with open("config.ini", "w") as configfile:
            self.config.write(configfile)

    def api(self):
        """
        Configurator for api module
        :return: api host url, admin password
        """
        url = self.config["API"]["url"]
        password = self.config["API"]["admin_password"]
        return url, password
