import os, sys

def unsetproxy():
    if 'http_proxy' in os.environ:
        del os.environ['http_proxy']
        del os.environ['https_proxy']
        del os.environ['HTTP_PROXY']
        del os.environ['HTTPS_PROXY']
    
def setproxy(proxy=""):
    os.environ['http_proxy'] = proxy
    os.environ['https_proxy']=proxy

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
try:
    from dotenv import load_dotenv, find_dotenv
    if os.path.exists(os.path.expanduser(".env")):
        load_dotenv(os.path.expanduser(".env"))
    load_dotenv(find_dotenv("./.env"))
except ImportError:
    print("dotenv not found!, skipping...")

if os.path.exists("my_config.py"):
    import my_config
    from my_config import *
else:
    home_env = os.path.expanduser("~/.django/")
    home_con = home_env+ "/my_config.py"
    if not (home_env in sys.path):
        sys.path.append(home_env)

    if os.path.exists(home_con):
        import my_config
        from my_config import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_from_env_or_config(key):
    v = os.environ.get(key, "")
    if (v):
        return v
    try:
        v = vars(my_config).get(key)
        return v
    except:
        return None
