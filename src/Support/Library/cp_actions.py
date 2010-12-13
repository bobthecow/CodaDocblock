'''
Utility functions for working with Coda Plugin Skeleton
@author Justin Hileman <http://justinhileman.com>
'''

import re
from types import StringTypes

import AppKit
from Foundation import *

import cp_html_replace as html_replace
import cp_html_matcher as html_matcher


def is_line_ending(content, index, line_ending):
    '''Checks whether the character(s) at index equals line_ending'''
    end = index + len(line_ending)
    return len(content) >= end and content[index:end] == line_ending


def end_is_line_ending(content, line_ending):
    '''Convenience function for checking the last characters of a string against the line_ending'''
    return content.endswith(line_ending)


def get_line_before(context, range = None):
    line, line_range = get_line_before_and_range(context, range)
    return line

def get_line_before_and_range(context, range = None):
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
    line_range = new_range(start, end - start)
    
    return get_selection(context, line_range), line_range

def get_line_after(context, range = None):
    line, line_range = get_line_after_and_range(context, range)
    return line

def get_line_after_and_range(context, range = None):
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
    line_range = new_range(start, end - start)
    
    return get_selection(context, line_range), line_range

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
    
    line_ending = get_line_ending(context)
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





# ===============================================================
# From TEA for Coda
# ===============================================================





# ===============================================================
# Interact with the user and output information
# ===============================================================

def say(context, title, message,
        main_button=None, alt_button=None, other_button=None):
    '''Displays a dialog with a message for the user'''
    alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
        title,
        main_button,
        alt_button,
        other_button,
        message
    )
    if context.window() is not None:
        return alert.beginSheetModalForWindow_modalDelegate_didEndSelector_contextInfo_(
            context.window(), None, None, None
        )
    else:
        return alert.runModal()

def log(message):
    '''
    Convenience function for logging messages to console
    
    Please make sure they are strings before you try to log them; wrap
    anything you aren't sure of in str()
    '''
    NSLog(str(message))

# ===============================================================
# Coda-specific options helpers
# ===============================================================

def get_option(options, option, default=None):
    option = options.objectForKey_(option)
    if default is not None and option is None:
        option = default
    return option

def get_context(controller, sender=None):
    return controller.focusedTextView_(sender)

# ===============================================================
# Preference lookup shortcuts
# ===============================================================

def get_line_ending(context):
    '''Shortcut function to get the line-endings for the context'''
    return context.lineEnding()

def get_indentation_string(context):
    '''Shortcut to retrieve the indentation string'''
    if context.usesTabs():
        tabString = '\t'
    else:
        tabString = ' ' * context.tabWidth()
    return tabString

# ===============================================================
# Text manipulations and helper functions
# ===============================================================

def parse_word(selection):
    '''
    Extract the first word from a string
    
    Returns the word:
    parse_word('p class="stuff"') => word = 'p'
    '''
    matches = re.match(r'(([a-zA-Z0-9_-]+)\s*.*)$', selection)
    if matches == None:
        return None
    return matches.group(2)

def string_to_tag(string):
    '''
    Parses a string into a tag with id and class attributes
    
    For example, div#stuff.good.things translates into
    `div id="stuff" class="good things"`
    '''
    if string.find('#') > 0 or string.find('.') > 0:
        match = re.search('#([a-zA-Z0-9_-]+)', string)
        if match:
            id = match.group(1)
        else:
            id = False
        matches = re.findall('\.([a-zA-Z0-9_-]+)', string)
        classes = ''
        for match in matches:
            if classes:
                classes += ' '
            classes += match
        tag = parse_word(string)
        if id:
            tag += ' id="' + id + '"'
        if classes:
            tag += ' class="' + classes + '"'
        return tag
    else:
        return string

def is_selfclosing(tag):
    '''Checks a tag and returns True if it's a self-closing XHTML tag'''
    # For now, we're just checking off a list
    selfclosing = ['img', 'input', 'br', 'hr', 'link', 'base', 'meta']
    # Make sure we've just got the tag
    if not tag.isalnum():
        tag = parse_word(tag)
        if tag is None:
            return False
    return tag in selfclosing

def encode_ampersands(text, enc='&amp;'):
    '''Encodes ampersands'''
    return re.sub('&(?!([a-zA-Z0-9]+|#[0-9]+|#x[0-9a-fA-F]+);)', enc, text)

def named_entities(text):
    '''Converts Unicode characters into named HTML entities'''
    text = text.encode('ascii', 'html_replace')
    return encode_ampersands(text)

def numeric_entities(text, ampersands=None):
    '''Converts Unicode characters into numeric HTML entities'''
    text = text.encode('ascii', 'xmlcharrefreplace')
    if ampersands == 'numeric':
        return encode_ampersands(text, '&#38;')
    elif ampersands == 'named':
        return encode_ampersands(text)
    else:
        return text

def entities_to_hex(text, wrap):
    '''
    Converts HTML entities into hexadecimal; replaces $HEX in wrap
    with the hex code
    '''
    # This is a bit of a hack to make the variable available to the function
    wrap = [wrap]
    def wrap_hex(match):
        hex = '%X' % int(match.group(2))
        while len(hex) < 4:
            hex = '0' + hex
        return wrap[0].replace('$HEX', hex)
    return re.sub(r'&(#x?)?([0-9]+|[0-9a-fA-F]+);', wrap_hex, text)

def trim(context, text, lines=True, sides='both', respect_indent=False,
         preserve_linebreaks=True, discard_empty=False):
    '''
    Trims whitespace from the text
    
    If lines=True, will trim each line in the text.
    
    sides can be both, start, or end and dictates where trimming occurs.
    
    If respect_indent=True, indent characters at the start of lines will be
    left alone (specific character determined by preferences)
    
    If discard_empty=True, whitespace on empty lines will be discarded
    regardless of indentation status
    '''
    def trimit(text, sides, indent, preserve_linebreaks, discard_empty):
        '''Utility function for trimming the text'''
        # If we're discarding empties, check for empty line
        if discard_empty:
            match = re.match(r'\s*?([\n\r]+)$', text)
            if match:
                return match.group(1)
        # Preserve the indent if an indent string is passed in
        if (sides.lower() == 'both' or sides.lower() == 'start') and indent != '':
            match = re.match('(' + indent + ')+', text)
            if match:
                indent_chars = match.group(0)
            else:
                indent_chars = ''
        else:
            indent_chars = ''
        # Preserve the linebreaks at the end if needed
        match = re.search(r'[\n\r]+$', text)
        if match and preserve_linebreaks:
            linebreak = match.group(0)
        else:
            linebreak = ''
        # Strip that whitespace!
        if sides.lower() == 'start':
            text = text.lstrip()
        elif sides.lower() == 'end':
            text = text.rstrip()
        else:
            text = text.strip()
        return indent_chars + text + linebreak
    
    # Set up which characters to treat as indent
    if respect_indent:
        indent = get_indentation_string(context)
    else:
        indent = ''
    finaltext = ''
    if lines:
        for line in text.splitlines(True):
            finaltext += trimit(line, sides, indent, preserve_linebreaks, discard_empty)
    else:
        finaltext = trimit(text, sides, indent, preserve_linebreaks, discard_empty)
    return finaltext

def unix_line_endings(text):
    '''Converts all line endings to Unix'''
    if text.find('\r\n') != -1:
        text = text.replace('\r\n','\n')
    if text.find('\r') != -1:
        text = text.replace('\r','\n')
    return text

def clean_line_endings(context, text, line_ending=None):
    '''
    Converts all line endings to the default line ending of the file,
    or if line_ending is specified uses that
    '''
    text = unix_line_endings(text)
    if line_ending is None:
        target = get_line_ending(context)
    else:
        target = line_ending
    return text.replace('\n', target)

# ===============================================================
# Working with ranges and selected text
# ===============================================================

def new_range(location, length):
    '''Convenience function for creating an NSRange'''
    return NSMakeRange(location, length)

def get_selection(context, range):
    '''Convenience function; returns selected text within a given range'''
    return context.string().substringWithRange_(range)

def set_selected_range(context, range):
    '''Sets the selection to the single range passed as an argument'''
    context.setSelectedRange_(range)

def get_line(context):
    return context.currentLine(), context.rangeOfCurrentLine()

def get_range(context):
    return context.selectedRange()

def selection_and_range(context, with_errors=False):
    '''
    If there's a single selection, returns the selected text,
    otherwise throws optional descriptive errors
    
    Returns a tuple with the selected text first and its range second
    '''
    range = context.selectedRange()
    if range.length is 0:
        if with_errors:
            say(
                context, "Error: selection required",
                "You must select some text in order to use this action."
            )
        return '', range
    return get_selection(context, range), range

def get_character(context, range):
    '''Returns the character immediately preceding the cursor'''
    if range.location > 0:
        range = new_range(range.location - 1, 1)
        return get_selection(context, range), range
    else:
        return None, range

def get_word(context, range, alpha_numeric=True, extra_characters='_-',
             bidirectional=True):
    '''
    Selects and returns the current word and its range from the passed range
    
    By default it defines a word as a contiguous string of alphanumeric
    characters plus extra_characters. Setting alpha_numeric to False will
    define a word as a contiguous string of alphabetic characters plus
    extra_characters
    
    If bidirectional is False, then it will only look behind the cursor
    '''
    # Helper regex for determining if line ends with a tag
    # Includes checks for ASP/PHP/JSP/ColdFusion closing delimiters
    re_tag = re.compile(r'(<\/?[\w:\-]+[^>]*|\s*(\?|%|-{2,3}))>$')
    
    def test_word():
        # Mini-function to cut down on code bloat
        if alpha_numeric:
            return all(c.isalnum() or c in extra_characters for c in char)
        else:
            return all(char.isalpha() or c in extra_characters for c in char)
    
    def ends_with_tag(cur_index):
        # Mini-function to check if line to index ends with a tag
        linestart = context.rangeOfCurrentLine().location
        text = get_selection(
            context, new_range(linestart, cur_index - linestart + 1)
        )
        return re_tag.search(text) != None
    
    # Set up basic variables
    index = range.location
    word = ''
    maxlength = context.string().length()
    if bidirectional:
        # Make sure the cursor isn't at the end of the document
        if index != maxlength:
            # Check if cursor is mid-word
            char = get_selection(context, new_range(index, 1))
            if test_word():
                inword = True
                # Parse forward until we hit the end of word or document
                while inword:
                    char = get_selection(context, new_range(index, 1))
                    if test_word():
                        word += char
                    else:
                        inword = False
                    index += 1
                    if index == maxlength:
                        inword = False
            else:
                # lastindex logic assumes we've been incrementing as we go,
                # so bump it up one to compensate
                index += 1
        lastindex = index - 1 if index < maxlength else index
    else:
        # Only parsing backward, so final index is cursor
        lastindex = range.location
    # Reset index to one less than the cursor
    index = range.location - 1
    # Only walk backwards if we aren't at the beginning
    if index >= 0:
        # Parse backward to get the word ahead of the cursor
        inword = True
        while inword:
            char = get_selection(context, new_range(index, 1))
            if test_word() and not (char == '>' and ends_with_tag(index)):
                word = char + word
                index -= 1
            else:
                inword = False
            if index < 0:
                inword = False
    # Since index is left-aligned and we've overcompensated,
    # need to increment +1
    firstindex = index + 1
    # Switch last index to length for use in range
    lastindex = lastindex - firstindex
    range = new_range(firstindex, lastindex)
    return word, range

def get_word_or_selection(context, range, alpha_numeric=True,
                          extra_characters='_-', bidirectional=True):
    '''
    Selects and returns the current word and its range from the passed range,
    or if there's already a selection returns the contents and its range
    
    See get_word() for an explanation of the extra arguments
    '''
    if range.length == 0:
        return get_word(context, range, alpha_numeric, extra_characters, bidirectional)
    else:
        return get_selection(context, range), range

def indent_snippet(context, snippet, range):
    '''
    Sets a snippet's indentation level to match that of the line starting
    at the location of range
    '''
    # Are there newlines?
    if re.search(r'[\n\r]', snippet) is not None:
        # Check if line is indented
        line = context.rangeOfCurrentLine()
        # Check if line is actually indented
        if line.location != range.location:
            line = get_selection(context, line)
            match = re.match(r'([ \t]+)', line)
            # Only indent if the line starts with whitespace
            if match is not None:
                current_indent = match.group(1)
                indent_string = get_indentation_string(context)
                # Convert tabs to indent_string and indent each line
                if indent_string != '\t':
                    snippet = snippet.replace('\t', indent_string)
                lines = snippet.splitlines(True)
                # Convert to iterator so we can avoid processing item 0
                lines = iter(lines)
                snippet = lines.next()
                for line in lines:
                    snippet += current_indent + line
                if re.search(r'[\n\r]$', snippet) is not None:
                    # Ends with a newline, add the indent
                    snippet += current_indent
    return snippet

# ===============================================================
# Check document syntax methods
# ===============================================================

def get_zen_doctype(context, default='html'):
    '''
    Tests the document to see if it is CSS or XSL; for use with zen
    coding actions to determine type of snippets to use
    '''
    doc_type = default
    css_exts = ['css', 'less']
    xsl_exts = ['xsl', 'xslt']
    path = context.path()
    if path is not None:
        pos = path.rfind('.')
        if pos != -1:
            pos += 1
            ext = path[pos:]
            if ext in css_exts:
                doc_type = 'css'
            elif ext in xsl_exts:
                doc_type = 'xsl'
    # No luck with the extension; check for inline style tags
    if doc_type == 'html':
        range = get_range(context)
        cursor = range.location + range.length
        content = context.string()
        start, end = html_matcher.match(content, cursor)
        tag = html_matcher.last_match['opening_tag']
        if tag is not None:
            tag = tag.name
            if tag == 'style':
                doc_type = 'css'
    return doc_type

# ===============================================================
# Insertion methods
# ===============================================================

def insert_text(context, text, range):
    '''Immediately replaces the text at range with passed in text'''
    context.beginUndoGrouping()
    context.replaceCharactersInRange_withString_(range, text)
    context.endUndoGrouping()

def insert_text_and_select(context, text, range, select_range):
    '''Immediately inserts the text and selects the given range'''
    context.beginUndoGrouping()
    context.replaceCharactersInRange_withString_(range, text)
    context.setSelectedRange_(select_range)
    context.endUndoGrouping()
