'''A (PHP) Docblock generator plugin for Coda'''

import cp_actions as cp
from Docblock import Docblock

def act(controller, bundle, options):
    '''
    Required action method
    
    Supplying a lang option will override the automatic language guessing
    (which might not be such a bad thing...)
    '''
    
    context = cp.get_context(controller)

    lang = cp.get_option(options, 'lang', 'auto').lower()
    
    # get the file extension so we can guess the language.
    if lang == 'auto':
        path = context.path()
        if path is not None:
            pos = path.rfind('.')
            if pos != -1:
                lang = path[pos+1:]
    
    d = Docblock.get(lang)
    
    # get the current line
    text, target_range = cp.lines_and_range(context)
    
    # keep going until we find a non-empty line to document (up to X lines below the current line)
    tries_left = 3
    while tries_left and not text.strip():
        text, target_range = cp.get_line_after_and_range(context, target_range)
        
        if text is None:
            # we're at the end of the document?
            cp.beep()
            return
        
        tries_left -= 1
    
    insert_range = cp.new_range(target_range.location, 0)
    
    d.setLineEnding(cp.get_line_ending(context))
    docblock = d.doc(text)
    
    if docblock:
        cp.insert_text_with_insertion_point(context, docblock, insert_range)
    else:
        cp.beep()