from Faab.Faab import faab
from Faab import utils
from werkzeug.datastructures.file_storage import FileStorage


def compress_image(file: FileStorage, app: faab, path: str = None, quality: int = 100, format_: str = None) -> str:
    """
    Compresses an image during upload.

    Args:
        file (str): The image file to be uploaded.
        app (str): The application name.
        path (str, optional): The path where the compressed image should be stored. If not provided, the image will be stored in the 'static' folder of the Faab startup folder.
        format_ (str, optional): The desired format of the compressed image. Valid values are 'PNG', 'JPEG', and 'WEBP'.
        quality (int, optional): The quality of the compressed image. Range is 1-100, with higher values indicating higher quality. Defaults to 100.

    Returns:
        str: The URL of the compressed image.

    """
    return utils.faab_compress_image(file=file, path=path, app=app, format_=format_, quality=quality)


def upload(file: FileStorage, app: faab, path: str = None) -> str:
    """
    Uploads a file to a specified path.

    Args:
        file: The file to be uploaded.
        path (str, optional): The path where the file should be saved. If not provided, the file will be saved in the 'static' folder.
        app (object, optional): The application object. If not provided, the 'app' parameter must be set.

    Returns:
        str: The file path of the uploaded file.

    Raises:
        ValueError: If the file is not selected or if 'app' is not delivered.

    """
    return utils.upload(file=file, app=app, path=path)
