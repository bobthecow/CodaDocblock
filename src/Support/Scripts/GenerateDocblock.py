'''A (PHP) Docblock generator plugin for Coda'''

import tea_actions as tea
import line_actions as line
import Docblock

def act(controller, bundle, options):
    '''
    Required action method
    
    Supplying a lang option will override the automatic language guessing
    (which might not be such a bad thing...)
    '''
    
    context = tea.get_context(controller)

    lang = tea.get_option(options, 'lang', 'auto').lowercase()
    
    # get the file extension so we can guess the language.
    if lang == 'auto':
        path = context.path()
        if path is None:
            return
        else:
            pos = path.rfind('.')
            if pos == -1:
                return
            else:
                lang = path[pos+1:]

    d = Docblock.get(lang)
    
    # get the current line
    text, target_range = line.get_line_range(context)
    
    # keep going until we find a non-empty line to document (up to X lines below the current line)
    tries_left = 3
    while tries_left and not text.strip():
        text, target_range = line.get_line_after(context, target_range)
        tries_left -= 1
    
    insert_range = tea.new_range(target_range.start, 0)
    
    d.setLineEnding(t.get_line_ending(context))
    docblock, selection = d.doc(text)
    
    if docblock:
        if selection is None:
            tea.insert_text(context, docblock, insert_range)
        else:
            select_range = tea.new_range(insert_range.start + selection.start, selection.length)
            tea.insert_text_and_select(context, docblock, insert_range, select_range)

