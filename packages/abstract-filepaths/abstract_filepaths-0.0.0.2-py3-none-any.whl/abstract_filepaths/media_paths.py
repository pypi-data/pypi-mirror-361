from .directories import *
UPLOADS_DIR = get_media_path("uploads")
DOWNLOADS_DIR = get_media_path("downloads")
def get_uploads_path(path):
    return get_directory_path(UPLOADS_DIR, path)
def get_downloads_path(path):
    return get_directory_path(DOWNLOADS_DIR, path)
