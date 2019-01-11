
def check_active(kha):
    return kha.check_installed('obs')

def get_files(kha):
    return ['~/.config/obs-studio/global.ini']

def update(kha):
    config = kha.load_ini('~/.config/obs-studio/global.ini')
    theme = config.get('General', 'CurrentTheme', fallback='Default')
    kha.rule(wmclass='obs', dark=(theme != 'Default'))
