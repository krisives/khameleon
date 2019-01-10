
def check_active(kha):
    return kha.check_installed('kdenlive')

def get_files(kha):
    return ['~/.config/kdenliverc']

def update(kha):
    config = kha.load_ini('~/.config/kdenliverc')
    theme = config.get('unmanaged', 'colortheme', fallback=None)
    kha.rule(wmclass='kdenlive', dark=kha.is_dark_theme(theme))
