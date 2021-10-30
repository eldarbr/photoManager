from PIL import Image, JpegImagePlugin as JIP
from configparser import ConfigParser
import argparse
import os


def resize(source_path, size, target_path):
    max_side_size, quality = map(int, size.split(":"))
    with Image.open(source_path) as image:
        if image.format != "JPEG":
            print("Photo {} was not processed as it is in unsupported format ({}) instead of JPEG".format(source_path,
                                                                                                          image.format))
            return 1
        source_width, source_height = image.width, image.height
        aspect = source_width / source_height
        if max(source_width, source_height) > max_side_size:
            if aspect > 1:
                new_size = (max_side_size, round(max_side_size / aspect))
            else:
                new_size = (round(max_side_size * aspect), max_side_size)

            downscaled_image = image.resize(new_size, resample=Image.LANCZOS)
        else:
            downscaled_image = image
        if "exif" in image.info:
            exif = image.info['exif']
        else:
            exif = b""
        downscaled_image.save(target_path, 'jpeg', quality=quality, icc_profile=image.info.get('icc_profile'),
                              progressive=True, subsampling=JIP.get_sampling(image), exif=exif)


def parse_config():
    config = ConfigParser()
    config.read("config.ini")
    new_sizes = list(config["RESIZER"]["newSizes"].replace(" ", "").split(","))
    temp_path = config["GENERIC"]["temporaryFolder"]
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)
    return new_sizes, temp_path


def auto_resize(photo_path):
    new_sizes, temp_path = parse_config()
    for size in new_sizes:
        file_name = photo_path.split("/")[-1]
        resize(photo_path, size,
               temp_path+"/"+file_name.replace(".", "_"+size.split(":")[0]+"."))  # insert size suffix to new file name


def multiple_resize(photo_array):
    for element in photo_array:
        element = element.replace("\\", "/")
        if os.path.isfile(element):                                 # if given path is a file, resize it
            auto_resize(element)
        else:
            paths = [element+"/"+i for i in os.listdir(element)]
            multiple_resize(paths)                                  # else resize any file in given folder


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('photos', nargs='+')
    args = parser.parse_args()
    multiple_resize(args.photos)
