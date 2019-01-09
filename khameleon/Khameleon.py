
import os, pkgutil, importlib, configparser, subprocess

class Khameleon:
    config = None
    config_changed = False
    plugins = []
    current_theme_is_dark = False
    current_color_theme = None
    dark_color_theme = None
    light_color_theme = None

    def run(self):
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

        print("current theme: ", self.current_color_theme)
        print("is dark theme? ", self.current_theme_is_dark)
        print("dark theme: ", self.dark_color_theme)
        print("light theme: ", self.light_color_theme)

        self.config = self.load_ini("~/.config/kwinrulesrc")

        for plugin in self.plugins:
            plugin.update(self)

        print("has changes?", self.config_changed)
        self.config.write(open('test.ini', 'w'), False)

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
        print(params)
        count = self.config.getint('General', 'count')
        wmclass = params.get('wmclass')
        found = self.find_rule(params)
        decocolor = ''
        decocolorrule = 0

        if self.current_theme_is_dark != params.get('dark', False):
            decocolor = 'BreezeDark'
            decocolorrule = 2

        if found == None:
            found = str(count + 1)
            self.config.add_section(found)
            self.config.set(found, 'Description', wmclass + ' (khameleon)')
            self.config.set('General', 'count', found)

        self.change_rule(found, {
            'titlematch': str(0),
            'wmclass': wmclass,
            'wmclassmatch': str(1),
            'wmclasscomplete': 'false',
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
