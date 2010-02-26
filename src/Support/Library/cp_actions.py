'''
Utility functions for working with Coda Plugin Skeleton
@author Justin Hileman <http://justinhileman.com>
'''

from tea_actions import *
import AppKit


def is_line_ending(content, index, line_ending):
    '''Checks whether the character(s) at index equals line_ending'''
    end = index + len(line_ending)
    return len(content) >= end and content[index:end] == line_ending


def end_is_line_ending(content, line_ending):
    '''Convenience function for checking the last characters of a string against the line_ending'''
    return is_line_ending(content, len(content) - len(line_ending), line_ending)


def get_line_before(context, range = None):
    '''Get the full line immediately before the current (or supplied) range'''
    line_ending = get_line_ending(context)
    if range is None: range = get_range(context)
    content = context.string()

    end = content.rfind(line_ending, 0, range.location)
    if end == -1:
        return None
    else:
        end = end + len(line_ending)
    
    start = content.rfind(line_ending, 0, end - len(line_ending))
    if start == -1:
        start = 0
    else:
        start += len(line_ending)
    
    start = max(0, start)
    end = min(end, len(content))
    
    return get_selection(context, new_range(start, end - start))


def get_line_after(context, range = None):
    '''Get the full line immediately after the current (or supplied) range'''
    line_ending = get_line_ending(context)
    len_line_ending = len(line_ending)
    if range is None: range = get_range(context)
    content = context.string()
    
    start = range.location + range.length
    
    if not is_line_ending(content, start - len_line_ending, line_ending):
        start = content.find(line_ending, start)
        if start == -1:
            return None
        else:
            start += len_line_ending
    
    end = content.find(line_ending, start)
    if end == -1:
        end = len(content)
    else:
        end += len_line_ending
    
    start = max(0, start)
    end = min(end, len(content))
    
    return get_selection(context, new_range(start, end - start))


def get_line_range(context, range = None):
    '''Get the range of the full lines containing the current (or supplied) range'''
    line_ending = get_line_ending(context)
    len_line_ending = len(line_ending)
    if range is None: range = get_range(context)
    content = context.string()
    
    start, end = range.location, range.location + range.length
    
    if not is_line_ending(content, start - len_line_ending, line_ending):
        start = content.rfind(line_ending, 0, start)
        if start == -1:
            start = 0
        else:
            start += len_line_ending
    
    # select to the end of the line (if it's not already selected)
    if not is_line_ending(content, end, line_ending):
        # edge case: cursor is at start of line and more than one line selected:
        if not is_line_ending(content, end - len_line_ending, line_ending) or len(content[start:end].split(line_ending)) <= 1:
            end = content.find(line_ending, end)
            if end == -1:
                end = len(content)
            else:
                end += len_line_ending
    # edge case: empty line, not selected
    elif is_line_ending(content, end - len_line_ending, line_ending):
        if len(content[start:end].split(line_ending)) <= 1:
            end = content.find(line_ending, end)
            if end == -1:
                end = len(content)
            else:
                end += len_line_ending
    else:
        end += len_line_ending
    
    start = max(0, start)
    end = min(end, len(content))
    
    line_range = new_range(start, end - start)
    
    return get_selection(context, line_range), line_range


def balance_line_endings(first, second, line_ending):
    '''Swaps the line endings on first and second lines'''
    len_line_ending = len(line_ending)
    if first[-len_line_ending:] != line_ending:
        first += line_ending
        if second[-len_line_ending:] == line_ending: second = second[:-len_line_ending]
    return first, second


def insert_text_with_insertion_point(context, text, range):
    '''Extracts insertion point tokens, inserts the text, and selects the insertion point range'''
    text, ip_range = extract_insertion_point_range(text)
    
    if ip_range:
        select_range = new_range(range.location + ip_range.location, ip_range.length)
        insert_text_and_select(context, text, range, select_range)
    else:
        insert_text(context, text, range)


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
            return text, new_range(start, 0)
        else:
            text = text.replace(end_token, '', 1)
            return text, new_range(start, end - start)


def words_and_range(context, range=False):
    '''Get text and range for the current word(s)'''
    text = context.string()
    line, line_range = line.lines_and_range(context)
    
    if range == False:
        selection, selection_range = selection_and_range(context)
    else:
        selection_range = range
        selection = get_selection(context)
    
    # move the start (out)
    if selection_range.location > line_range.location and not selection.startswith(('\t', ' ')):
        prefix = text[line_range.location:selection_range.location]
        start = max(prefix.rfind(' '), prefix.rfind('\t'))
        if start == -1:
            start = line_range.location
        else:
            # plus one (at the end) is for the width of the whitespace character.
            start += line_range.location + 1
        selection_range = new_range(start, selection_range.length - selection_range.location + start)
        selection = get_selection(context, selection_range)
    
    suffix_start = selection_range.location + selection_range.length
    suffix_end = line_range.location + line_range.length
    if suffix_start < suffix_end and not selection.endswith(('\t', ' ')):
        suffix = text[suffix_start:suffix_end]
        end = min(suffix.find(' '), suffix.rfind('\t'))
        if end == -1:
            end = suffix_end
        else:
            end += suffix_start
        selection_range = new_range(selection_range.location, end - selection_range.location)
        selection = get_selection(context, selection_range)
    
    return selection, selection_range


def beep():
    '''System beep!'''
    AppKit.NSBeep()