# Usage: python setup.py py2app
# Dev:   python setup.py py2app -A
# Built plugin will show up in ./dist directory
# Install in the standard plugin directory and relaunch Coda to run

from distutils.core import setup
import py2app
import os

# === CONFIG ===

# You will need to name your plugin something different
plugin_name = 'Docblock'

# Update this info by hand; defines the required Info.plist elements
info = dict(
    CFBundleVersion = '1.2.0',
    CFBundleIdentifier = 'com.justinhileman.Docblock',
    NSHumanReadableCopyright = '(c) 2011 Justin Hileman',
    CodaPlugInMinimumAPIVersion = '4',
)

# === You prob'ly won't need to change anything past this point ===

# Sets what directory to crawl for files to include
# Relative to location of setup.py; leave off trailing slash
includes_dir = 'src'

# Set the root directory for included files
# Relative to the bundle's Resources folder:
#     bundle.extension/Contents/Resources/
includes_target = '../../'

# === END CONFIG ===

# Initialize an empty list so we can use list.append()
includes = []

# Walk the includes directory and include all the files
for root, dirs, filenames in os.walk(includes_dir):
    if root is includes_dir:
        final = includes_target
    else:
        final = includes_target + root[len(includes_dir)+1:] + '/'
    files = []
    for file in filenames:
        if (file[0] != '.'):
            files.append(os.path.join(root, file))
    includes.append((final, files))

# Here's the guts of the setup call
setup(
    name = plugin_name,
    plugin = ['CodaPlugin.py'],
    data_files = includes,
    options = dict(py2app = dict(
        extension = '.codaplugin',
        semi_standalone = True,
        site_packages = True,
        plist=info,
    )),
)
