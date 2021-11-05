from PIL import Image
from configparser import ConfigParser
import argparse
import os


def resize(source_file, max_side, max_side_size, quality, target_file):
    """
    Resizes given jpeg according to specified and saves it to target file

    :param source_file: input image path
    :param max_side_size: size export settings
    :param max_side: side of image to be restricted
    :param quality: quality export settings
    :param target_file: output image path
    :return: 0 - no errors; 1 - wrong input image format
    """

    with Image.open(source_file) as image:
        if image.format != "JPEG":
            raise Exception("Image {} was not processed as it is in unsupported format ({}) instead of JPEG".
                            format(source_file, image.format))
        source_width, source_height = image.width, image.height
        aspect = source_width / source_height

        if max_side == "w":
            if source_width > max_side_size:
                new_size = (max_side_size, round(max_side_size / aspect))
                downscaled_image = image.resize(new_size, resample=Image.LANCZOS)
            else:
                downscaled_image = image

        elif max_side == "h":
            if source_height > max_side_size:
                new_size = (round(max_side_size * aspect), max_side_size)
                downscaled_image = image.resize(new_size, resample=Image.LANCZOS)
            else:
                downscaled_image = image

        elif max_side == "m":
            if max(source_width, source_height) > max_side_size:
                if aspect > 1:
                    new_size = (max_side_size, round(max_side_size / aspect))
                else:
                    new_size = (round(max_side_size * aspect), max_side_size)
                downscaled_image = image.resize(new_size, resample=Image.LANCZOS)
            else:
                downscaled_image = image
        else:
            raise Exception('Wrong max side property - not in range ["h", "w", "m"]')

        if "exif" in image.info:
            exif = image.info['exif']
        else:
            exif = b""
        downscaled_image.save(target_file, 'jpeg', quality=quality, icc_profile=image.info.get('icc_profile'),
                              progressive=True, subsampling=0, exif=exif)
        return 0


def parse_config():
    """
    Configuration parser
    Reads parameters from config.ini associated with resizer module

    :return: temp_folder, export_presets
    """
    config = ConfigParser()
    config.read("config.ini")
    export_presets = []
    for x in config["RESIZER"]["newSizes"].replace(" ", "").split(","):
        g = x.split(":")
        export_presets += [(g[0], int(g[1]), int(g[2]))]
    temp_folder = config["GENERIC"]["temporaryFolder"]
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)
    return temp_folder, export_presets


def auto_resize(image_path):
    """
    Automatically processes given image according to export parameters at config.ini

    :param image_path: input image path
    :return: 0 if resizing succeeded
    """
    target_folder, export_presets = parse_config()
    target_folder = target_folder.replace("/", "\\")

    for preset in export_presets:
        file_name = image_path.split("\\")[-1]
        side, size, quality = preset
        return resize(image_path, side, size, quality,
                      target_folder + "\\" + file_name.replace(".", "_" + str(size) + "_" + str(quality) + "."))
                                    # insert size-quality suffix to target file filename


def multiple_resize(image_paths_array):
    """
    Automatically processes every image from given array of paths according to export parameters at config.ini
    Can process folders - processes every image from folder

    :param image_paths_array: array of input images/folders paths
    :return: 0 on successful completion of processing all given images
    """

    for element in image_paths_array:
        if os.path.isfile(element):  # if given path is a file, resize it
            auto_resize(element)
        else:
            paths = [element + "\\" + i for i in os.listdir(element)]
            multiple_resize(paths)  # else resize any file in given folder


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('images', nargs='+', help="paths of input images or folders with images")
    args = parser.parse_args()
    multiple_resize(args.images)
