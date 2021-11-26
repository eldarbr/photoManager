from configparser import ConfigParser
import os
from my_types import ExportPreset


class Configurator:
    
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("config.ini")

    def resizer(self):
        """
        Configurator for resizer
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
        pass
