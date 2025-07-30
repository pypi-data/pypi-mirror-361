import cProfile
import tempfile
import requests
import threading
import atexit
import time

from .config import CODEW_API_URL

kxy_enabled = "not_initialized"
__profiler = cProfile.Profile()
TOKEN_SECRET = ""


def loop():
    global TOKEN_SECRET
    while True:
        time.sleep(2)
        check_token(TOKEN_SECRET)


def check_token(license_id):
    global kxy_enabled
    if kxy_enabled != "not_initialized" or not license_id:
        return

    base_url = CODEW_API_URL + "/kxy/status"
    try:
        response = requests.post(base_url, headers={"secret": license_id}, timeout=1)
        response.raise_for_status()
        kxy_enabled = response.text.strip()
    except Exception as e:
        print(f"Error checking kxy status: {e}")
        pass


def create_link(response):
    return CODEW_API_URL + "/kxy/profile/" + response.json().get("id")


def push_results(profiler):
    try:
        upload_url = CODEW_API_URL + "/kxy/upload"
        with tempfile.NamedTemporaryFile(suffix=".prof") as tmp:
            profiler.dump_stats(tmp.name)
            tmp.seek(0)
            files = {"file": ("profile.prof", tmp, "application/octet-stream")}
            response = requests.post(upload_url, files=files, headers={"secret": TOKEN_SECRET}, timeout=5)
            print(f"Profile report available at: {create_link(response)}")
            return response.json().get("id")
    except requests.RequestException as e:
        print("Error connecting to 7176")
        ...


def profile(func):
    def wrapper(*args, **kwargs):
        global kxy_enabled
        if kxy_enabled == "1":
            _profiler = cProfile.Profile()
            _profiler.enable()
            try:
                result = func(*args, **kwargs)
                _profiler.disable()
            except Exception as e:
                _profiler.disable()
                raise e
            finally:
                push_results(_profiler)
            return result
        else:
            return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def end_kxy(_time=None):
    global __profiler

    if _time:
        time.sleep(_time)
    __profiler.disable()
    push_results(__profiler)


def set_codew_token_secret(secret):
    global TOKEN_SECRET
    TOKEN_SECRET = secret


def init_kxy(_time=None):
    global __profiler
    __profiler.enable()
    if _time:
        end_thread = threading.Thread(target=end_kxy, args=(_time,), daemon=True)
        end_thread.start()
    atexit.register(end_kxy, None)


print("Initializing kxy-codew")
check_token(TOKEN_SECRET)
thread = threading.Thread(target=loop, daemon=True)
thread.start()
