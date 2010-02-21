'''
Line utility functions for working with Line Commands
@author Justin Hileman <http://justinhileman.com>
'''

import tea_actions as tea

def is_line_ending(content, index, line_ending):
    '''Checks whether the character(s) at index equals line_ending'''
    end = index + len(line_ending)
    return len(content) >= end and content[index:end] == line_ending

def get_line_before(context, range = None):
    line, line_range = get_line_before_and_range(context, range)
    return line

def get_line_before_and_range(context, range = None):
    '''Get the full line immediately before the current (or supplied) range'''
    line_ending = tea.get_line_ending(context)
    if range is None: range = tea.get_range(context)
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
    line_range = tea.new_range(start, end - start)
    
    return tea.get_selection(context, line_range), line_range

def get_line_after(context, range = None):
    line, line_range = get_line_after_and_range(context, range)
    return line

def get_line_after_and_range(context, range = None):
    '''Get the full line immediately after the current (or supplied) range'''
    line_ending = tea.get_line_ending(context)
    len_line_ending = len(line_ending)
    if range is None: range = tea.get_range(context)
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
    line_range = tea.new_range(start, end - start)
    
    return tea.get_selection(context, line_range), line_range

def lines_and_range(context, range = None):
    '''Get the range of the full lines containing the current (or supplied) range'''
    line_ending = tea.get_line_ending(context)
    len_line_ending = len(line_ending)
    if range is None: range = tea.get_range(context)
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
    
    line_range = tea.new_range(start, end - start)
    
    return tea.get_selection(context, line_range), line_range

def balance_line_endings(first, second, line_ending):
    '''Swaps the line endings on first and second lines'''
    len_line_ending = len(line_ending)
    if first[-len_line_ending:] != line_ending:
        first += line_ending
        if second[-len_line_ending:] == line_ending: second = second[:-len_line_ending]
    return first, second