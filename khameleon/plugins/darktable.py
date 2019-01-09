
def check_active(kha):
    return kha.check_installed('darktable')

def get_files(kha):
    return []

def update(kha):
    kha.rule(wmclass='darktable', dark=True)
