
import os, sqlite3, json

def check_active(kha):
    return kha.check_installed('discord')

def get_files(kha):
    return ['~/.config/discord/Local Storage/https_discordapp.com_0.localstorage']

def update(kha):
    # Discord stores the preference in an Sqlite file as JSON data
    path = os.path.expanduser('~/.config/discord/Local Storage/https_discordapp.com_0.localstorage')
    dark = True

    if os.path.exists(path):
        c = sqlite3.connect(path)
        result = c.execute("SELECT value FROM ItemTable WHERE key='UserSettingsStore'")
        row = result.fetchone()
        settings = json.loads(row[0])
        c.close()
        dark = 'dark' in settings.get('theme', 'dark')

    kha.rule(wmclass='discord', dark=dark)
