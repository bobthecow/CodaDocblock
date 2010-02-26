'''Utility functions for working with Coda Plugin Skeleton'''

from tea_actions import *
from AppKit import *

def insert_text_with_insertion_point(context, text, range):
    '''Extracts insertion point tokens, inserts the text, and selects the insertion point range'''
    text, ip_range = extract_insertion_point_range(text)
    
    if ip_range:
        select_range = tea.new_range(range.location + ip_range.location, ip_range.length)
        tea.insert_text_and_select(context, text, range, select_range)
    else:
        tea.insert_text(context, text, range)


def extract_insertion_point_range(text):
    '''Extract a range for the insertion point delimited by `$$IP$$` and `$$`.'''
    start_token = '$$IP$$'
    end_token = '$$'

    start = text.find(start_token)
    if start == -1:
        return text, None
    
    else:
        text = text.replace(start_token, '', 1)
        end = text.find(end_token, start);
        
        if end == -1:
            return text, tea.new_range(start, 0)
        else:
            text = text.replace(end_token, '', 1)
            return text, tea.new_range(start, end - start)


def words_and_range(context, range=False):
    '''Get text and range for the current word(s)'''
    text = context.string()
    line, line_range = line.lines_and_range(context)
    
    if range == False:
        selection, selection_range = tea.selection_and_range(context)
    else:
        selection_range = range
        selection = tea.get_selection(context)
    
    # move the start (out)
    if selection_range.location > line_range.location and not selection.startswith(('\t', ' ')):
        prefix = text[line_range.location:selection_range.location]
        start = max(prefix.rfind(' '), prefix.rfind('\t'))
        if start == -1:
            start = line_range.location
        else:
            # plus one (at the end) is for the width of the whitespace character.
            start += line_range.location + 1
        selection_range = tea.new_range(start, selection_range.length - selection_range.location + start)
        selection = tea.get_selection(context, selection_range)
    
    suffix_start = selection_range.location + selection_range.length
    suffix_end = line_range.location + line_range.length
    if suffix_start < suffix_end and not selection.endswith(('\t', ' ')):
        suffix = text[suffix_start:suffix_end]
        end = min(suffix.find(' '), suffix.rfind('\t'))
        if end == -1:
            end = suffix_end
        else:
            end += suffix_start
        selection_range = tea.new_range(selection_range.location, end - selection_range.location)
        selection = tea.get_selection(context, selection_range)
    
    return selection, selection_range


def beep():
    '''System beep!'''
    NSBeep()