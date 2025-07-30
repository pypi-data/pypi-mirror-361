from .directories import get_apis_path
ABSTRACT_LOGINS_FLASK_DIR = get_apis_path("abstract_logins")
CHARTS_FLASK_DIR = get_apis_path("charts")
THE_DAILY_DIALECTICS_FLASK_DIR = get_apis_path("daily_dialectics_flask")
JAMAIL_FLASK_DIR = get_apis_path("jamail")
JOBEN_FLASK_DIR = get_apis_path("joben")
MEDIA_FLASK_DIR = get_apis_path("media")
OLD_JAMAIL_FLASK_DIR = get_apis_path("old_jamail")
SERVICE_FILES_FLASK_DIR = get_apis_path("service_files")
TODO_FLASK_DIR = get_apis_path("todo")
TYPING_FLASK_DIR = get_apis_path("typings")
USURPIT_FLASK_DIR = get_apis_path("usurpit")
VIDEO_PLAYER_FLASK_DIR = get_apis_path("video_player")
WSGIS_DIR = get_apis_path("wsgis")
def get_abtract_logins_flask_path(path):
    return get_directory_path(ABSTRACT_LOGINS_FLASK_DIR,path)
def get_chartts_flask_path(path):
    return get_directory_path(CHARTS_FLASK_DIR,path)
def get_the_dailyu_dialectics_flask_path(path):
    return get_directory_path(THE_DAILY_DIALECTICS_FLASK_DIR,path)
def get_jamail_flask_path(path):
    return get_directory_path(JAMAIL_FLASK_DIR,path)
def get_media_flask_path(path):
    return get_directory_path(MEDIA_FLASK_DIR,path)
def get_old_jamail_flask_path(path):
    return get_directory_path(OLD_JAMAIL_FLASK_DIR,path)
def get_service_files_flask_path(path):
    return get_directory_path(SERVICE_FILES_FLASK_DIR,path)
def get_todo_flask_path(path):
    return get_directory_path(TODO_FLASK_DIR,path)
def get_typings_path(path):
    return get_directory_path(TYPING_FLASK_DIR,path)
def get_usurpit_flask_path(path):
    return get_directory_path(USURPIT_FLASK_DIR,path)
def get_video_player_flask_path(path):
    return get_directory_path(VIDEO_PLAYER_FLASK_DIR,path)
def get_wsgis_path(path):
    return get_directory_path(WSGIS_DIR,path)
