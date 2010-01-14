'''A Hello World action for the Coda Plugin Skeleton'''

import tea_actions as tea

def act(controller, bundle, options):
    '''
    Required action method
    
    if supplied, message will be written instead of Hello World
    
    Setting replace=True replace the current selection instead of inserting
    '''
    
    context = tea.get_context(controller)
    
    message = tea.get_option(options, 'message', 'Hello World')
    replace_selection = tea.get_option(options, 'replace', False)
    
    range = tea.get_range(context)
    
    if not replace_selection:
        range = tea.new_range(range.location, 0)
    
    tea.insert_text(context, message, range)