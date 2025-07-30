from .directories import get_htmls_path
TYPICALLY_OUTLIERS_DIR = get_htmls_path("typicallyoutliers")
THE_DAILY_DIALECTICS_DIR = get_htmls_path("thedailydialectics")
SOLCATCHER_DIR = get_htmls_path("solcatcher")
CLOWNWORLD_DIR = get_htmls_path("clownworld")
ABSTRACT_ENDEAVORSS_DIR = get_htmls_path("abstractendeavors")
def get_abstractendeavors_htmls_path(path):
    return get_htmls_path(ABSTRACT_ENDEAVORSS_DIR,path)
def get_clownworld_htmls_path(path):
    return get_htmls_path(CLOWNWORLD_DIR,path)
def get_solcatcher_htmls_path(path):
    return get_htmls_path(SOLCATCHER_DIR,path)
def get_thedailydialectics_htmls_path(path):
    return get_htmls_path(THE_DAILY_DIALECTICS_DIR,path)
def get_typicallyoutliers_htmls_path(path):
    return get_htmls_path(TYPICALLY_OUTLIERS_DIR,path)
