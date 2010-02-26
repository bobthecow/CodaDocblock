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


def lines_and_range(context, range = None):
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


def words_and_range(context, range = None):
    '''Get text and range for the current word(s)'''
    
    # word characters, for our purposes. include < and > for html, $ for php variables.
    word_chars = 'a-zA-Z0-9_\\?|`<>\$'
    
    line_ending = tea.get_line_ending(context)
    text = context.string()
    line_text, line_range = lines_and_range(context)
    
    if range is None:
        selection, selection_range = selection_and_range(context)
    else:
        selection_range = range
        selection = get_selection(context, selection_range)
    
    # move the start (out)
    prefix_start = line_range.location
    prefix_end = selection_range.location
    if prefix_end > prefix_start and not re.match('[^%s]' % word_chars, selection):
        result = rfind_not_chars(text[prefix_start:prefix_end], word_chars)
        if result != -1:
            start = prefix_start + result
        else:
            start = prefix_start
        
        selection_range = new_range(start, selection_range.length + prefix_end - start)
        selection = get_selection(context, selection_range)

    suffix_start = selection_range.location + selection_range.length
    suffix_end = line_range.location + line_range.length
    if suffix_start < suffix_end and not re.search('[^%s]$' % word_chars, selection):
        result = find_not_chars(text[suffix_start:suffix_end], word_chars)
        if result != -1:
            end = result + suffix_start
        else:
            end = suffix_end
        
        selection_range = new_range(selection_range.location, end - selection_range.location)
        selection = get_selection(context, selection_range)
    
    tea.say(context, '', '||%s||' % selection)
    return selection, selection_range


def beep():
    '''System beep!'''
    AppKit.NSBeep()


def find_chars(text, chars):
    '''Find the first index of any character from chars in text. chars is the guts of a regex []'''
    result = re.search('[%s]' % chars, text)
    if result:
        return result.start()
    else:
        return -1


def rfind_chars(text, chars):
    '''Find the last index of any character from chars in text. chars is the guts of a regex []'''
    result = re.search('([%s])[^%s]*$' % (chars, chars), text)
    if result:
        return result.end(1)
    else:
        return -1


def find_not_chars(text, chars):
    '''Find the first index of any character not in chars in text. chars is the guts of a regex []'''
    result = re.search('[^%s]' % chars, text)
    if result:
        return result.start()
    else:
        return -1


def rfind_not_chars(text, chars):
    '''Find the last index of any character not in chars in text. chars is the guts of a regex []'''
    result = re.search('([^%s])[%s]*$' % (chars, chars), text)
    if result:
        return result.end(1)
    else:
        return -1
