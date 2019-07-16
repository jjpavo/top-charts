from os import path

from PIL import Image


def construct_image_path(input_path):
    """Constructs an image path from a hash string.

    If the input hash is abcdefg then the output is of format a/b/c/defg.png.
    This is to prevent too many images from being in one directory, which can cause performance issues.

    Args:
        input_path (str): A hash string to transform into a path.

    Returns:
        image_path (str): The path to save the image at.
    """
    return path.join(input_path[0], input_path[1], input_path[2], (input_path[3:] + ".png"))


def crop_image(image, bound_width, bound_height, crop_coor=None):
    # Ensures that the image fits within the bound. Ideally the image will already be cropped to do so.
    # Resizes the image to fill the bound and then crops to cut off overfill.

    width, height = image.size

    # Center Cropping by default.
    if crop_coor is None:
        left = (width - bound_width) / 2
        top = (height - bound_height) / 2
        right = (width + bound_width) / 2
        bottom = (height + bound_height) / 2
    else:
        left = crop_coor[0]
        top = crop_coor[1]
        right = crop_coor[2]
        bottom = crop_coor[3]

    image = image.crop((left, top, right, bottom))

    # Get size of new cropped image.
    width, height = image.size

    # Take the smaller ratio, as that is the one that should be the bound.
    # That is, if one side is much smaller than its bound side compared to the other,
    # we have to scale it up more;
    # If one side is not much larger than its bound side compared to the other,
    # we shouldn't scale it down as much.
    # This ensures that image will fill the bound and there will be no empty space.
    ratio = None
    if (width / bound_width) <= (height / bound_height):
        ratio = width / bound_width
    else:
        ratio = height / bound_height

    width = int(width / ratio)
    height = int(height / ratio)
    image = image.resize((width, height), Image.ANTIALIAS)

    return image
