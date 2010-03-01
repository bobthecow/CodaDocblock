'''A Hello World action for the Coda Plugin Skeleton'''

import cp_actions as cp

def act(controller, bundle, options):
    '''
    Required action method
    
    if supplied, message will be written instead of Hello World
    
    Setting replace=True replace the current selection instead of inserting
    '''
    
    context = cp.get_context(controller)
    
    message = cp.get_option(options, 'message', 'Hello World')
    replace_selection = cp.get_option(options, 'replace', False)
    
    range = cp.get_range(context)
    
    if not replace_selection:
        range = cp.new_range(range.location, 0)
    
    cp.insert_text(context, message, range)