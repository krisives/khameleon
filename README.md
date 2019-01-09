
`khameleon` creates window rules and color themes for KDE to match the look
of popular Linux apps.

## Add an App

Don't see your favorite app? Create a new file inside the `plugins/` directory
with contents like this:

```python
def is_active(kha):
  return kha.is_installed('someapp')

def get_files(kha):
  return ['~/somefile']

def update(kha):
  # Do something cool here
  pass
```

In all of the functions declared here `kha` is a handle to the `Khameleon`
object.

### check_active(kha)

Check if an app is installed and therefor the plugin should be active. Most of
the time this should end up calling `kha.is_installed('something')` where
`something` is the Linux command that would run the app. This helps avoid
creating window rules that aren't going to be used.

### get_files(kha)

Get a list of files that if modified should cause this plugin to update. This
is used by the `khameleon-daemon` to watch files and automatically update when
configuration files are changed.

### update(kha)

Load app-specific configuration files and determine the best color scheme to
apply to match. Most plugins will want to end this with a call to
`Khameleon.rule()` to apply a window rule

## API

### Khameleon.rule(self, \*\*params)

Ensure a window rule exists with the given parameters, which can include:

Param       | Description
------------|-------------
wmclass     | Match based on a window class
dark        | Set if the window should have the default dark theme
decocolor   | Set if you want to apply a specific color scheme


### Khameleon.is_installed(self, program)

Check if a program is installed essentially calls `which program` to determine
if the command exists.
