from os import path


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
