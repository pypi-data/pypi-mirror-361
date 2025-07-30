import os
WWW_DIR="/var/www/"
def get_directory_path(directory, path):
    return os.path.join(directory, path)
def get_www_path(path):
    return get_directory_path(WWW_DIR, path)
