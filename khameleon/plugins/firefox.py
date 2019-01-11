from glob import glob
import os, re

def check_active(kha):
    return kha.check_installed('firefox')

def get_files(kha):
    path = locate_prefs()
    return [path] if path else None

def update(kha):
    theme = get_firefox_theme()
    dark = False

    if theme:
        theme = theme.lower()
        dark = ('dark' in theme) and not ('light' in theme)

    kha.rule(wmclass='firefox', dark=dark)

def locate_prefs():
    path = os.path.expanduser('~/.mozilla/firefox/*.default/prefs.js')
    files = glob(path)
    return files[0] if files else None

def get_firefox_theme():
    path = locate_prefs()

    if not path:
        return None

    pattern = re.compile(r"user_pref\(\"lightweightThemes\.selectedThemeID\", \"(.+)\"\);")

    for line in open(path, 'r').readlines():
        match = pattern.match(line)

        if match:
            return match.group(1)
