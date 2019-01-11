
def check_active(kha):
    return kha.is_installed('spotify')

def get_files(kha):
    return []

# Spotify always has a dark UI theme
def update(kha):
    kha.rule(wmclass='spotify', dark=True)
