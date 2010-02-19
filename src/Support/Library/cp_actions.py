'''Utility functions for working with Coda Plugin Skeleton'''

import tea_actions as tea
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


def beep():
    '''System beep!'''
    NSBeep()