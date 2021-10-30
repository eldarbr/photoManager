from PIL import Image, JpegImagePlugin as JIP


def resize(source_path, size, target_path):
    max_side_size, quality = map(int, size.split(":"))
    with Image.open(source_path) as image:
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
        downscaled_image.save(target_path, 'jpeg', quality=quality, icc_profile=image.info.get('icc_profile'),
                              progressive=True, subsampling=JIP.get_sampling(image), exif=image.info['exif'])
