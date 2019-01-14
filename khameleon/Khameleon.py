
import sys, os, pkgutil, importlib, configparser, subprocess, argparse

try:
    import dbus
except ImportError:
    dbus = None

class Khameleon:
    config = None
    config_changed = False
    plugins = []
    current_theme_is_dark = False
    current_color_theme = None
    dark_color_theme = None
    light_color_theme = None
    options = None

    def __init__(self, options):
        self.options = options

    def parse_args():
        parser = argparse.ArgumentParser(description='Update window rules')
        parser.add_argument('--rules', dest='rules', default='~/.config/kwinrulesrc',
            help='Input file for KDE window rules (default: ~/.config/kwinrulesrc)')
        parser.add_argument('--rulesout', dest='rulesout', default='~/.config/kwinrulesrc',
            help='Output file for KDE window rules (default: ~/.config/kwinrulesrc)')
        parser.add_argument('--nosignal', dest='nosignal', action='store_true',
            help='Skip sending the KDE reloadConfig signal')
        parser.add_argument('--debug', dest='debug', action='store_true',
            help='Enable debugging output')
        return parser.parse_args()

    def debug(self, *args, **kwargs):
        if self.options.debug:
            print(*args, file=sys.stderr, **kwargs)

    def run(self):
        self.start()
        self.update()

    def start(self):
        self.load_plugins()
        self.current_color_theme = self.get_current_color_theme()

        if self.current_color_theme == None:
            print("ERROR: Cannot determine current color theme")
            return

        self.current_theme_is_dark = self.is_dark_theme(self.current_color_theme)

        if self.current_theme_is_dark:
            self.dark_color_theme = self.current_color_theme
            self.light_color_theme = self.find_opposite_theme(self.dark_color_theme, 'dark', 'light')
        else:
            self.light_color_theme = self.current_color_theme
            self.dark_color_theme = self.find_opposite_theme(self.light_color_theme, 'light', 'dark')

        self.debug("current theme is ", self.current_color_theme)
        self.debug("is dark theme? ", self.current_theme_is_dark)
        self.debug("dark theme: ", self.dark_color_theme)
        self.debug("light theme: ", self.light_color_theme)

        self.config = self.load_ini(self.options.rules)

    def update(self):
        for plugin in self.plugins:
            self.debug("Running plugin ", plugin.__name__)

            if plugin.check_active(self):
                plugin.update(self)

        self.debug("Config has changes" if self.config_changed else "Config has no changes")

        if self.config_changed:
            self.config.write(open(os.path.expanduser(self.options.rulesout), 'w'), False)

            if not self.options.nosignal:
                self.emit_signal()

    def load_plugins(self):
        for module in pkgutil.iter_modules([os.path.dirname(__file__) + "/plugins"]):
            if not module.name.startswith('__'):
                self.plugins.append(importlib.import_module("khameleon.plugins." + module.name))

    def load_ini(self, path):
        path = os.path.expanduser(path)
        parser = configparser.ConfigParser(allow_no_value=True)
        parser.optionxform = str

        if os.path.exists(path):
            parser.read(path)

        return parser

    def get_current_color_theme(self):
        kdeglobals = self.load_ini("~/.kde/share/config/kdeglobals")
        return kdeglobals.get('General', 'ColorScheme')

    def find_opposite_theme(self, theme, current, opposite):
        if current in theme:
            return theme.replace(current, opposite)
        elif current.title() in theme:
            return theme.replace(current.title(), opposite.title())

        return theme

    def rule(self, **params):
        self.debug("Updating rule", params)
        count = self.config.getint('General', 'count')
        wmclass = params.get('wmclass')
        dark = bool(params.get('dark', False))
        found = self.find_rule(params)
        decocolor = ''
        decocolorrule = 0

        if self.current_theme_is_dark != dark:
            decocolor = 'BreezeDark'
            decocolorrule = 2

        if found == None:
            if (dark == self.current_theme_is_dark):
                return

            found = str(count + 1)
            self.config.add_section(found)
            self.change_rule(found, {
                'Description': wmclass + ' (khameleon)',
                'titlematch': str(0),
                'wmclass': wmclass,
                'wmclassmatch': str(1),
                'wmclasscomplete': 'false',
            })
            self.config.set('General', 'count', found)

        self.change_rule(found, {
            'decocolor': str(decocolor),
            'decocolorrule': str(decocolorrule)
        })

    def find_rule(self, params):
        count = self.config.getint('General', 'count')
        wmclass = params.get('wmclass')

        for i in range(1, 1 + count):
            section = self.config[str(i)]

            if section.get('wmclass') == wmclass:
                return str(i)

    def change_rule(self, rule, changes):
        for key, value in changes.items():
            current = self.config.get(rule, key, fallback=None)

            if current != value:
                self.config_changed = True
                self.config.set(rule, key, value)

    def check_installed(self, program):
        result = subprocess.run(['which', program], stdout=subprocess.PIPE)

        if result.returncode:
            return False

        output = result.stdout.decode('utf-8').strip()
        return len(output) > 0

    # Check if a color theme is a dark theme
    def is_dark_theme(self, theme):
        if theme == None:
            return True

        theme = os.path.basename(theme)

        if 'dark' in theme.lower():
            return True

        return False

    def emit_signal(self):
        if not dbus:
            return;

        bus = dbus.SessionBus()
        msg = dbus.lowlevel.SignalMessage(path='/KWin', interface='org.kde.KWin', name='reloadConfig')
        bus.send_message(msg)
