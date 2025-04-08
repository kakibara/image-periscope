import os
from flask import render_template

def get_image_list(directory):
    """Retrieve a list of images in the specified directory, maintaining the hierarchy.

    Args:
        directory (str): The path to the directory to search for images.

    Returns:
        list: A list of dictionaries containing image paths and their respective hierarchy.
    """
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
    images = []

    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in image_extensions:
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                images.append({'path': relative_path, 'name': file})

    return images

def organize_images(images):
    """Organize images into a hierarchical structure.

    Args:
        images (list): A list of image dictionaries.

    Returns:
        dict: A nested dictionary representing the hierarchy of images.
    """
    organized = {}
    for image in images:
        parts = image['path'].split(os.sep)
        current_level = organized

        for part in parts[:-1]:  # Exclude the file name
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

        current_level[parts[-1]] = image['path']  # Add the image file

    return organized