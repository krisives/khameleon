
import os

def check_active(kha):
    return kha.check_installed('atom')

def get_files(kha):
    return ['~/.atom/config.cson']

def update(kha):
    # Sadly Atom uses "cson" files instead of json so instead of actually
    # inspecting the config.cson file we have to do basic text analysis
    path = os.path.expanduser("~/.atom/config.cson")
    dark = True

    if (os.path.exists(path)):
        text = open(path, 'r').read()
        dark = ("one-light-ui" not in text) and ("atom-light-ui" not in text)

    kha.rule(wmclass='atom', dark=dark)
