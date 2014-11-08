'''
Docblock

Copyright (c) 2010 Justin Hileman
'''

import sys
import os.path

from Foundation import *
from AppKit import *
import objc

NSObject = objc.lookUpClass('NSObject')
CodaPlugIn = objc.protocolNamed('CodaPlugIn')

class Docblock(NSObject, CodaPlugIn):
    '''
    Initializes the menu items and is responsible for directing
    actions to the appropriate class
    '''

	# AT A MINIMUM you must change this line:
    plugin_name = 'Docblock'

    # Change this to disable automatic sorting of menu items:
    sort_menu_items = True

    def initWithPlugInController_plugInBundle_(self, controller, bundle):
        self.initWithPlugInController_bundle_(controller, bundle)

    def initWithPlugInController_bundle_(self, controller, bundle):
        '''Required method; run when the plugin is loaded'''
        self = super(self.__class__, self).init()
        if self is None: return None

        defaults = NSUserDefaults.standardUserDefaults()
        # Set up default action set
        defaults.registerDefaults_(NSDictionary.dictionaryWithContentsOfFile_(
            bundle.pathForResource_ofType_('PluginActions', 'plist')
        ))
        ns_actions = defaults.dictionaryForKey_('PluginActions')
        actions = dict(
            [str(arg), dict(value)] \
            for arg, value in ns_actions.iteritems()
        )

        self.controller = controller
        self.bundle = bundle

        # Loop over the actions and add them to the menus
        rootlevel = {}
        submenus = {}
        # Extract out our submenus and root items
        for key, value in actions.iteritems():
            if 'submenu' in value:
                if not str(value['submenu']) in submenus:
                    submenus[str(value['submenu'])] = {}
                submenus[str(value['submenu'])][key] = value
            else:
                rootlevel[key] = value
        # Process the submenus
        submenu_keys = submenus.keys()
        submenu_keys.sort()
        for menu in submenu_keys:
            menu_actions = submenus[menu]
            temp_keys = menu_actions.keys()
            if self.sort_menu_items:
                temp_keys.sort()
            for title in temp_keys:
                action = menu_actions[title]
                self.register_action(controller, action, title)
        # Process the root level items
        keys = rootlevel.keys()
        if self.sort_menu_items:
            keys.sort()
        for title in keys:
            action = rootlevel[title]
            self.register_action(controller, action, title)

        # Add the Support/Scripts folder to the Python import path
        sys.path.append(os.path.join(bundle.bundlePath(), "Support/Scripts"))
        sys.path.append(os.path.join(bundle.bundlePath(), "Support/Library"))

        return self

    def validateMenuItem_(self, sender):
        '''
        Validate the menu item for an action.
        '''

        # Make sure there's a focused TextView
        # NOTE: Panic still hands us a 'focused' TextView when the Sites tab is open, so this isn't always reliable...
        if sender.representedObject().objectForKey_('requireDocument') and self.controller.focusedTextView_(sender) is None:
            return False

        # Make sure the user has selected something...
        if sender.representedObject().objectForKey_('requireSelection'):
            textView = self.controller.focusedTextView_(sender)
            if textView is None or textView.selectedRange().length is 0:
                return False

        # Allow this action to validate its own menu item.
        # NOTE: This can make a submenu really slow the first time it is used.
        if sender.representedObject().objectForKey_('validateMenuItem'):
            sender.representedObject().objectForKey_('actionname')
            actionname = sender.representedObject().objectForKey_('actionname')
            mod = __import__(actionname)
            if actionname in mod.__dict__:
                target = mod.__dict__[actionname].alloc().init()
            else:
                target = mod

            if 'showmenu' in target.__dict__:
                return target.showmenu(self.controller, self.bundle, sender.representedObject().objectForKey_('options'))

        return True

    def name(self):
        '''Required method; returns the name of the plugin'''
        return self.plugin_name

    def act_(self, sender):
        '''
        Imports the module, initializes the class, and runs its act() method
        '''
        actionname = sender.representedObject().objectForKey_('actionname')
        mod = __import__(actionname)
        if actionname in mod.__dict__:
            target = mod.__dict__[actionname].alloc().init()
        else:
            target = mod
        try:
            target.act(self.controller, self.bundle, sender.representedObject().objectForKey_('options'))
        except Exception, e:
            NSLog('Docblock error: %s' % str(e))

    def register_action(self, controller, action, title):
        if 'action' not in action:
            NSLog('%s: module missing `action` entry' % self.name())
            return False

        # Required items
        actionname = action['action']

        # Set up defaults
        submenu = action['submenu'] if 'submenu' in action else None
        shortcut = action['shortcut'] if 'shortcut' in action else ''
        options = action['options'] if 'options' in action else NSDictionary.dictionary()

        # Menu item validation.
        requireDocument = action['requireDocument'] if 'requireDocument' in action else True
        requireSelection = action['requireSelection'] if 'requireSelection' in action else False
        validateMenuItem = action['validateMenuItem'] if 'validateMenuItem' in action else False

        rep = NSDictionary.dictionaryWithObjectsAndKeys_(
            actionname,
            'actionname',
            options,
            'options',
            validateMenuItem,
            'validateMenuItem',
            requireDocument,
            'requireDocument',
            requireSelection,
            'requireSelection',
        )
        controller.registerActionWithTitle_underSubmenuWithTitle_target_selector_representedObject_keyEquivalent_pluginName_(
            title,
            submenu,
            self,
            'act:',
            rep,
            shortcut,
            self.name()
        )
