from .base_dir import get_www_path,get_directory_path
API_DIR = get_www_path("api")
FUNCTIONS_DIR = get_www_path("functions")
HTML_DIR = get_www_path("html")
MODULES_DIR = get_www_path("modules")
SITES_DIR = get_www_path("sites")
MEDIA_DIR = get_www_path("media")
ENV_DIR = get_www_path("env")
LANDING_PAGE_DIR = get_www_path("landing_page")
def get_apis_path(path):
    return get_directory_path(API_DIR, path)
def get_functions_path(path):
    return get_directory_path(FUNCTIONS_DIR, path)
def get_htmls_path(path):
    return get_directory_path(HTML_DIR, path)
def get_module_path(path):
    return get_directory_path(MODULES_DIR, path)
def get_sites_path(path):
    return get_directory_path(SITES_DIR, path)
def get_env_path(path):
    return get_directory_path(ENV_DIR, path)
def get_media_path(path):
    return get_directory_path(MEDIA_DIR, path)
def get_landing_page_path(path):
    return get_directory_path(LANDING_PAGE_DIR, path)
def create_env_path(env):
    envs_dir = get_envs_dir()
    return os.path.join(envs_dir,env)
