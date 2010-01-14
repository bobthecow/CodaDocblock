Coda Plugin Skeleton
--------------------

Coda Plugin Skeleton is a poorly named framework for writing Cocoa plugins for
[Coda][1] using Python.

The skeleton is essentially the gutted remains of Ian Beck's excellent
[TEA for Coda plugin][2]. It provides a PyObjC bridge to the Cocoa plugin API,
along with several convenience functions for dealing with text manipulation,
menu generation, etc.

   [1]: http://panic.com/coda/
   [2]: http://onecrayon.com/tea/coda/

Building from source
====================

In order to get anything useful out of Coda Plugin Skeleton, you will need to
download and build the source:

	git clone git://github.com/bobthecow/coda-plugin.git
	cd coda-plugin
	python setup.py py2app

If you wish to create a development version, you can run this instead:

	python setup.py py2app -A

This will create a normal version of your Coda plugin, but symlink all the
internal files so that you don't have to rebuild the plugin to try out
changes (you'll still need to relaunch Coda between changes, though).

Now go build something cool
===========================

 1. Edit `setup.py`, enter your sweet new plugin name and details.

 2. Rename `CodaPluginSkeleton.py` (and the class inside) to match your plugin
    name. Be sure to change `CodaPluginSkeleton`'s `plugin_name` variable as
    well.

 3. Edit `src/Contents/Resources/English.lproj/PluginActions.plist` and add your
    actions.

 4. Add corresponding action scripts to `src/Support/Scripts`. If your plugin
    needs additional libraries, drop them in `src/Library` and they'll be
    automatically included.
