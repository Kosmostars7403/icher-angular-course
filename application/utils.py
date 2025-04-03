import os


def delete_image_by_path(image_path: str):
    if image_path is not None:
        if os.path.exists(image_path):
            os.remove(image_path)