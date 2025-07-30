import pandas, os, math, logging
import pandas as pd
logging.basicConfig(level=logging.DEBUG)
from abstract_utilities import get_logFile, read_from_file,make_list,eatAll
from flask import Blueprint, request, render_template_string,render_template
def get_abs_file_path():
    abs_file_path = os.path.abspath(__file__)
    os.path.dirname(abs_file_path)
    if isinstance(abs_file_path,list) or ',' in str(abs_file_path):
        if ',' in str(abs_file_path):
            abs_file_path = str(abs_file_path).split(',')
        abs_piece = abs_file_path[-1]
        user = abs_piece.split('/')[0]
        abs_file_path = abs_piece[len(user):]
    return abs_file_path
def get_abs_dir():
    return os.path.dirname(get_abs_file_path())

def create_abs_path(path):
    abs_dir = get_abs_dir()
    abs_path = os.path.join(abs_dir,path)
    return abs_path
def get_envs_dir():
    return create_abs_path('envs')
def create_env_path(env):
    envs_dir = get_envs_dir()
    return os.path.join(envs_dir,env)
def join_path(*paths):
    for i, path in enumerate(make_list(paths)):  # <-- enumerating "paths" itself, not *paths
        logging.debug(path)
        if i == 0:
            
            if isinstance(path,tuple):
                for i, pat in enumerate(path):
                    if i == 0:
                        new_path=pat
                    else:
                        new_path= os.path.join(new_path, pat)
            else:
                new_path = path
        else:
            new_path = os.path.join(new_path, path)
        # If no dot, assume it's a directory and auto-create it
        if '.' not in path:
            logging.debug(f"Making directories if needed: {new_path}")
            os.makedirs(new_path, exist_ok=True)
            break
    
    return new_path
