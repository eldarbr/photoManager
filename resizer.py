from PIL import Image, ExifTags
import argparse
from config import Configurator
import datetime

suffixes = ["preview", "medium", "large"]


class Resizer:
    def __init__(self):
        """
        Prepare config
        """
        configurator = Configurator()
        self.export_presets, self.temp_path = configurator.resizer()

    def resize_three(self, source_file):
        """
        Crucial RESIZE function
        Resize source file to preview, medium, large formats according to config file and saves to the temp folder
        :param source_file: source image
        :return:
        """
        source_file = source_file.replace("/", "\\")
        source_file_name = source_file.split("\\")[-1]
        report = {"created_images": [], "faulty_photos": []}
        for i in range(3):
            target_file = self.temp_path + "\\" + source_file_name.replace(".", "_" + suffixes[i] + ".")
            preset = self.export_presets[i]
            result = smart_resize(source_file, preset.side, preset.length, preset.quality, target_file)
            if not result:
                report["created_images"] += [target_file]
            else:
                report["faulty_photos"] += [target_file]
        return report


def smart_resize(source_file, max_side, max_side_size, quality, target_file):
    """
    Resizes given jpeg according to specified and saves it to target file

    :param source_file: input image path
    :param max_side_size: size export settings
    :param max_side: side of image to be restricted
    :param quality: quality export settings
    :param target_file: output image path
    :return: 0 - ok; 1 - unsupported input format; 2 - wrong max side property; 3 - exporting error
    """

    with Image.open(source_file) as image:
        if image.format != "JPEG":
            print("[smart_resize import exception]")
            print(f"Image {source_file} was not processed as it is in unsupported format"
                  f"({image.format}) instead of JPEG")
            return 1

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
            print("[smart_resize exception]")
            print(f'Wrong max side property ({max_side}) - not in range ["h", "w", "m"]')
            return 2

        # copy exif info from original photo
        if "exif" in image.info:
            exif = image.info['exif']
        else:
            exif = b""

        # export resized image
        try:
            downscaled_image.save(target_file, 'jpeg', quality=quality, icc_profile=image.info.get('icc_profile'),
                                  progressive=True, subsampling=0, exif=exif)
        # handle errors of exporting
        except Exception as e:
            print("[smart_resize export exception]")
            print(e)
            return 3

        return 0


def original_timestamp(photo_path):
    """
    Get original timestamp of a photo
    :param photo_path: path to photo
    :return: original timestamp or empty string if unable to get timestamp from the photo
    """
    image_exif = Image.open(photo_path).getexif()
    if image_exif:
        # Make a map with tag names
        exif = {ExifTags.TAGS[k]: v for k, v in image_exif.items() if k in ExifTags.TAGS and type(v) is not bytes}
        # Grab the date
        try:
            date_time_original = exif['DateTimeOriginal']
        except KeyError:
            return ""
        timestamp = datetime.datetime.strptime(date_time_original, '%Y:%m:%d %H:%M:%S').strftime("%d.%m.%y %H:%M")
        return timestamp
    else:
        return ""


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', nargs=1, help="path of input image")
    args = parser.parse_args()
    resizer = Resizer()
    print(resizer.resize_three(args.image[0]))
