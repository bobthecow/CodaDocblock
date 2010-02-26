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
            [str(arg), value] \
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
        Imports the module, initializes the class, and runs its act() method
        '''
        actionname = sender.representedObject().objectForKey_('actionname')
        mod = __import__(actionname)
        if actionname in mod.__dict__:
            target = mod.__dict__[actionname].alloc().init()
        else:
            target = mod
        
        if 'showmenu' in target.__dict__:
            return target.showmenu(self.controller, self.bundle, sender.representedObject().objectForKey_('options'))
        else:
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
        target.act(self.controller, self.bundle, sender.representedObject().objectForKey_('options'))
    
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
        
        rep = NSDictionary.dictionaryWithObjectsAndKeys_(
            actionname,
            'actionname',
            options,
            'options'
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
